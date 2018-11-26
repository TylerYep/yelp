# yelp
Community Detection on the Yelp Dataset

To generate distance matrix:
python download_distances.py
python create_distance_matrix.py

To generate fake graphs:
---
Download these as png:

https://docs.google.com/drawings/d/1HJFULW14yUPwTRJEUaYNT_TrOrV4JNJ8C7BnC75LOoM/edit?usp=sharing

https://docs.google.com/drawings/d/18clYRmUvQUYK4-6_25sIb3hop1rvRhZS60e_rc0yoNE/edit?usp=sharing

Move to directory called `data/fake-graphs/$GRAPH_DIRNAME_HERE` as `category.png` and `density.png`

Run
```
sh src/experimental/lazy.sh $GRAPH_DIRNAME_HERE
```

To visualize:
`python src/visualization/fake-graph-viz.py -n data/fake-graphs/$GRAPH_DIRNAME_HERE/points.csv -e data/fake-graphs/$GRAPH_DIRNAME_HERE/categories/edges-knn_10_*.csv`
