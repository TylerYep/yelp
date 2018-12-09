# yelp
Community Detection on the Yelp Dataset

To generate distance matrix:
python create_distance_matrix.py

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
