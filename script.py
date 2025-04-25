# Open and explore the Dataset
import pandas as pd # for data manipulation
import re # for regular expressions used in cleaning text
from fuzzywuzzy import fuzz # for fuzzy string matching
from itertools import combinations # for generating all possible pairs from a group

# load the dataset
df = pd.read_parquet("veridion_entity_resolution_challenge.snappy.parquet")

# show general info
print(df.info())

# show first few rows
print(df.head())


# Inspect the Columns
# relevant columns that can help determine if two records are the same company
cols_to_use = [
    "company_name",
    "company_legal_names",
    "company_commercial_names",
    "website_domain",
    "primary_email",
    "main_country",
    "main_city",
    "main_address_raw_text",
]


# Cleaning Script
# load only needed columns using pyarrow engine
df = pd.read_parquet("veridion_entity_resolution_challenge.snappy.parquet", engine="pyarrow")

df = df[cols_to_use] # filter only the relevant columns


# define a cleaning function for text fields
def clean_text(text):

    if pd.isna(text):
        return "" # replace NaN (not a number) with empty string
    text = text.lower()     # convert to lowercase
    text = re.sub(r"[^\w\s]", "", text)    # remove punctuation
    text = re.sub(r"\s+", " ", text).strip()    # colapse whitespace and strip ends
    return text


# apply cleaning function to each relevant column
for col in cols_to_use:
    df[col] = df[col].apply(clean_text)

# display first 10 cleaned records
print(df.head(10))


# Blocking (reducing comparisons)
# define a function that generates a blpcl key for each row
def create_block_key(row):

    name = row["company_name"][:3] if row["company_name"] else "" # first 3 letters of company name
    country = row["main_country"][:3] if row["main_country"] else "" # first 3 letters of country
    domain = row["website_domain"][:3] if row["website_domain"] else "" # first 3 letters of domain
    return f"{name}_{country}_{domain}" # join them with underscores

# apply block key creation to each row
df["block_key"] = df.apply(create_block_key, axis = 1)

# show 10 most common blocks by size
print(df.groupby("block_key").size().sort_values(ascending=False).head(10))

# show all companies that fall under a sample block
sample_block = df[df["block_key"] == "tes_hun_tes"]
print(sample_block)


# Fuzzy matching within blocks
matches = [] # list to store matching pairs

# group records by block and process only those with more than one record
for block_key, group in df.groupby("block_key"):
    if len(group) < 2:
        continue # skip blocks with only 1 record

    # compare all possible pairs within each block
    for idx1, idx2 in combinations(group.index, 2):
        name1 = df.at[idx1, "company_name"] # a fast method to access a value from the dataframe
        name2 = df.at[idx2, "company_name"]
        score = fuzz.token_set_ratio(name1, name2) # compute fuzzy similarity score

        if score >= 90: # keep only highly similar pairs
            matches.append((idx1, idx2, name1, name2, score))

# show a few example matches
print("Sample matches:")
for m in matches[:10]:
    print(f"[{m[2]}] vs [{m[3]}] - Similarity: {m[4]}")


# Clustering matches (entity groups)
# use union-find data structure to group matching records into clusters
class UnionFind:

    def __init__(self):
        self.parent = {} # dictionary to hold parent relationships

    def find(self, u):
        if u not in self.parent:
            self.parent[u] = u # each element is its own parent initially
        if self.parent[u] != u:
            self.parent[u] = self.find(self.parent[u]) # path compression
        return self.parent[u]

    def union(self, u, v):
        pu, pv = self.find(u), self.find(v) # find root parents
        if pu != pv:
            self.parent[pu] = pv # merge clusters

# initialize union-find instance
uf = UnionFind()


# union all matched pairs
for idx1, idx2, _, _, _ in matches:
    uf.union(idx1, idx2)

# create clusters from union-find results
clusters = {}
for idx in df.index:
    root = uf.find(idx) # find cluster representative
    if root not in clusters:
        clusters[root] = []
    clusters[root].append(idx) # add index to its cluster

# show sample clusters (those with more than 1 record)
print("\nSample clusters (more than 1 entity): ")
for cluster_id, indices in list(clusters.items())[:10]:
    if len(indices) < 2:
        continue
    print(f"\nCluster ID: {cluster_id}")

    for idx in indices:
        print(f" - {df.at[idx, 'company_name']}")


# Assign cluster_id to each row
cluster_ids = {} # dictionary to map index to cluster_id
for cluster_id, indices in clusters.items():
    for idx in indices:
        cluster_ids[idx] = cluster_id

# add cluster_id column to dataframe, default is -1
df["cluster_id"] = df.index.map(lambda x: cluster_ids.get(x, -1)) # -1 means unmatched

# show sample output with cluster IDs
print("\nOutput with cluster IDs:")
print(df[["company_name", "cluster_id"]].head(10))


# Export to CSV
# save results to CSV file
df.to_csv("entity_resolution_clustered.csv", index=False)
print("\nExported clustered results to 'entity_resolution_clustered.csv'")