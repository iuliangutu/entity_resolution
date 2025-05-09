# Entity Resolution

This project tackles the Entity Resolution challenge by identifying and clustering company records that refer to the same real-world entity, even when attributes such as names, addresses, or contact details vary significantly.

The goal is to design a scalable, adaptable solution specifically tailored to company datasets, which often suffer from inconsistent formatting, language variations, and incomplete data.

## Problem Understanding & Approach
Real-world company data is messy: names can have suffixes (LLC, SRL), locations are expressed in different ways, and websites/phones may be missing or incorrect. This solution takes a deterministic but flexible approach combining:

Blocking to reduce the number of comparisons

Fuzzy Matching to identify similar entities within blocks

Graph-Based Clustering to group matching entities


## Feature Selection & Preprocessing
To ensure relevance and data quality, the following preprocessing steps were applied:

Normalized Names: Lowercased strings, removed accents and punctuation, stripped legal suffixes (Kft, GmbH, LLC, etc.)

Locations: Used a combination of city and country as blocking attributes

Data Cleaning: Removed empty rows, normalized Unicode characters, and eliminated noise tokens (e.g., "online only", "--")

Attributes considered but not used due to incompleteness or noise: email, phone number, and website.

## Blocking Strategy
To make pairwise comparisons tractable (from millions of rows), companies were grouped into blocks based on:

Cleaned name prefixes

City + Country


## Matching Logic
Within each block, companies were compared using:

FuzzyWuzzy’s token_set_ratio to compute name similarity

A threshold of 90% was chosen empirically to balance precision and recall
Example:
"Tescoma Budaörs" ↔ "Tescoma Kft" → Similarity Score: 92 → Match

## Clustering Logic
A Union-Find (Disjoint Set) data structure was used to build clusters:

Each company is a node

Edges are added between matching pairs

Connected components form a cluster


## Sample Clusters
Cluster ID: 29462 – Tescoma

- tescoma
- tescoma budaörs
- tescoma corvin
- tescoma kft

Cluster ID: 33198 – AAA Auto

- aaa auto otrokovice zlín 
- aaa auto ostrava 
- aaa auto jihlava 
- aaa auto praha čestlice

Cluster ID: 30746 – Dental Planet

- dental planet howick 
- dental planet limited 
- dental planet mt roskill


## Output
Final clusters are saved in: entity_resolution_clustered.csv

Each record includes:

cluster_id (companies in the same group share a cluster)

-1 for unclustered records (no matches found)


## Strengths & Limitations
### Strengths
Fast and scalable through blocking

Deterministic and interpretable logic

Works well for moderately clean data with consistent name/location info

### Limitations
Weak performance on online-only or incomplete records

Struggles with deep name variations or translations

No ML used — not adaptive to subtle signals across attributes


## Scalability Considerations
Blocking ensures sub-linear scaling with input size

Pairwise fuzzy matching can be parallelized by block

Future improvements may include LSH (Locality Sensitive Hashing) for faster approximate matching


## Future Work
Geocoding support: Normalize addresses by coordinates for better location grouping

ML-based scoring: Learn match probabilities from labeled data

Rule engine: Add rules like "same domain = likely match"

Active learning loop: Include manual review and feedback integration


## Tech Stack
Python 3.12

- pandas – data wrangling 
- fuzzywuzzy – string similarity 
- re, itertools, collections – core Python for preprocessing & logic 
- UnionFind – custom class for clustering

Developed in PyCharm

## Reflections
This project helped me understand:

- The complexity of real-world deduplication tasks
- How to design for performance using blocking 
- The importance of balancing simplicity, interpretability, and accuracy