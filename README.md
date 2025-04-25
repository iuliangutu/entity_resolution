# Entity Resolution

This project solves the Entity Resolution challenge by identifying and clustering company records that refer to the same real-world entity, even if their names or addresses vary.

## Strategy
- blocking (grouping similar records together)
- scoring (comparing how similar they are)
- clustering (grouping records referring to the same entity)


1. **Blocking**:  
   - To reduce the number of comparisons, companies are grouped into "blocks" using a combination of normalized company names and location information (e.g., city, country).
   - This drastically reduces the number of comparisons from millions to manageable subsets.

2. **Matching**:  
   - Inside each block, company names are compared using fuzzy string matching (`fuzz.token_set_ratio`) to determine their similarity.
   - Matches with a similarity score above a defined threshold (e.g. 90%) are considered duplicates.

3. **Clustering**:  
   - A graph-based approach is used to group similar companies into clusters.
   - Each node is a company, and edges connect companies with strong similarity. Connected components form the final clusters.

## Tech Stack

- **Python 3.12**
- **Pandas** – for data manipulation
- **FuzzyWuzzy** – for fuzzy string similarity
- **re** - for text cleaning
- **itertools.combinations** - for generating pairs
- **UnionFind** - for clustering
- **PyCharm** – for development and testing

## Sample Results

Here are some of the actual clusters found:

### Cluster ID: 29462 (Tescoma)
- tescoma  
- tescoma budaörs  
- tescoma corvin  
- tescoma kft  
- tescoma (multiple Budapest addresses)

### Cluster ID: 33198 (AAA Auto)
- aaa auto otrokovice zlín  
- aaa auto zličín  
- aaa auto ostrava  
- aaa auto praha čestlice  
- aaa auto teplice  
- aaa auto jihlava  
- aaa auto brno  
- aaa auto online prodej  
*(and many more city variants)*

### Cluster ID: 30746 (Dental Planet)
- dental planet manukau  
- dental planet mt roskill  
- dental planet howick  
- dental planet limited  

## Output

The final clustered results are saved in:

entity_resolution_clustered.csv

where companies with the same cluster_id are likely the same and -1 means no match was found

## Summary
1. Cleans the data - standardizez strings (lowercase, remove punctuation)
2. Creates blocking keys - limits comparisons to likely matches only
3. Fuzzy matches within blocks - scores all possible pairs
4. Clusters matches - groups records that are similar enough using a union-find structure
5. Assigns a cluster_id - every record gets a cluster_id to indicate which group it belongs to