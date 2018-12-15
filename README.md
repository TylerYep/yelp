# Yelp
## Predicting Restaurant Success using Attribute-Specific Spatial Clusters
### Community Detection on the Yelp Dataset
By Heidi Chen (heidichen7), Edward Lee (ed-w-lee), Tyler Yep (tyleryep)  

# Preprocess/Clean Dataset
```
python src/preprocesssing/data-clean.py
```
Extracts the relevant fields from the Yelp data files.

# Graph Construction / Spatial Clustering
```
python src/graph-construction/knn.py or /louvain.py
```
Creates networkx or snap graphs.

# Graph Visualization
```
python src/visualization/graph-viz.py
```

Given a Yelp CSV of latitude/longitude coordinates, maps data into a nice-looking map.
Note that any outlier points will ruin the graph - make sure all data passed in is within a couple lat/long degrees of each other.

# Community Detection
```
python src/clustering/comm.py
```
Detects a lot of variations of communities to varying degrees of success.

# Supervised Learning
```
python src/ml/runner.py
```
Runs every single sci-kit learn model to look for best prediction.

# Administrivia

To generate distance matrix:
```
python create_distance_matrix.py
```

To generate fake graphs:
---
Download these as png:

`complex-with`:
density: https://docs.google.com/drawings/d/18clYRmUvQUYK4-6_25sIb3hop1rvRhZS60e_rc0yoNE/edit?usp=sharing
category: https://docs.google.com/drawings/d/1HJFULW14yUPwTRJEUaYNT_TrOrV4JNJ8C7BnC75LOoM/edit?usp=sharing

`simple`:
density: https://docs.google.com/drawings/d/1cgTknj5zB51gxLiLbsQbujIPEOQG-tveB36-kDSmrvA/edit?usp=sharing
category: https://docs.google.com/drawings/d/1upoeZrkXGolW8HyuKzxikNGQT-2xSH2Z5NQ8yNVYZCM/edit?usp=sharing

`ripme`:
density: https://docs.google.com/drawings/d/1z78tWqMCXoW6ApREiQvWca92PcX9Fdfwks94NrgxEX8/edit?usp=sharing
category: https://docs.google.com/drawings/d/1inpZScOC-Qdlez4hvsy4X25c8p1QF2QP_aVR8EU4G9g/edit?usp=sharing

`ripme-more` and `ripme-more2`:
density: https://docs.google.com/drawings/d/1CVAvbzfV5gTjYO5szOMbn9kQ5lVDvacXoPtbGjSbpvw/edit?usp=sharing
category (ripme-more2): https://docs.google.com/drawings/d/10mLzaC4qDZW_Vy4LrZ4qIR7_w4sN8fKz56SzP4v9XcY/edit?usp=sharing
category: swap the colors of ripme-more2

`sectioned`:
density: https://docs.google.com/drawings/d/10mLzaC4qDZW_Vy4LrZ4qIR7_w4sN8fKz56SzP4v9XcY/edit?usp=sharing
category: https://docs.google.com/drawings/d/1kFr55sA33yvxNUw341eSKf5pHttXQda7tyUgOyKWmbE/edit?usp=sharing

Move to directory called `data/fake-graphs/$GRAPH_DIRNAME_HERE` as `category.png` and `density.png`

To generate some relevant graphs:
```
sh src/experimental/lazy.sh $GRAPH_DIRNAME_HERE
```

To evaluate:
```
mkdir src/clustering/graphs
mkdir src/clustering/figures
mkdir -p data/results
python src/clustering/evaluate.py --dir data/fake-graphs/$GRAPH_DIRNAME_HERE
```
The resulting graphs will be in `src/clustering/graphs` and the F1 scores will be in `data/results`

To visualize:
`python src/visualization/fake-graph-viz.py -n data/fake-graphs/$GRAPH_DIRNAME_HERE/points.csv -e data/fake-graphs/$GRAPH_DIRNAME_HERE/categories/edges-knn_10_*.csv`
