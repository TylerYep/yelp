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

Move to directory called `data/fake-graphs/1` as `category.png` and `density.png`

Run
```
python src/preprocessing/generate-fake-graph.py -d data/fake-graphs/1

python src/graph-construction/knn.py -k 3 -f data/fake-graphs/1/points.csv -o data/fake-graphs/1/edges-{}.csv
python src/graph-construction/knn.py -k 5 -f data/fake-graphs/1/points.csv -o data/fake-graphs/1/edges-{}.csv
python src/graph-construction/knn.py -k 10 -f data/fake-graphs/1/points.csv -o data/fake-graphs/1/edges-{}.csv

python src/preprocessing/split-edges.py -e data/fake-graphs/1/edges-knn_3.csv -c 0 1 2 --destination data/fake-graphs/1/categories -n data/fake-graphs/1/points.csv
python src/preprocessing/split-edges.py -e data/fake-graphs/1/edges-knn_5.csv -c 0 1 2 --destination data/fake-graphs/1/categories -n data/fake-graphs/1/points.csv
python src/preprocessing/split-edges.py -e data/fake-graphs/1/edges-knn_10.csv -c 0 1 2 --destination data/fake-graphs/1/categories -n data/fake-graphs/1/points.csv

python src/graph-construction/delaunay.py -f data/fake-graphs/1/points.csv -o data/fake-graphs/1/delaunay.csv -d data/fake-graphs/1/categories -c 0 1 2
```

To visualize:
`python src/visualization/fake-graph-viz.py -n data/fake-graphs/1/points.csv -e data/fake-graphs/1/categories/edges-knn_10_*.csv`
