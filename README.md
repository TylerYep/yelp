# yelp
Community Detection on the Yelp Dataset

To generate fake graphs:
---
Download these as png:

https://docs.google.com/drawings/d/1HJFULW14yUPwTRJEUaYNT_TrOrV4JNJ8C7BnC75LOoM/edit?usp=sharing

https://docs.google.com/drawings/d/18clYRmUvQUYK4-6_25sIb3hop1rvRhZS60e_rc0yoNE/edit?usp=sharing

Move to directory called `data/fake-graphs` as `3-cateory.png` and `3-density.png`

Run 
```
python src/preprocessing/generate-fake-graph.py -f data/fake-graphs/3

python src/graph-construction/knn.py -k 3 -f data/fake-graphs/3/points.csv -o data/fake-graphs/3/edges-{}.csv
python src/graph-construction/knn.py -k 5 -f data/fake-graphs/3/points.csv -o data/fake-graphs/3/edges-{}.csv
python src/graph-construction/knn.py -k 10 -f data/fake-graphs/3/points.csv -o data/fake-graphs/3/edges-{}.csv

python src/preprocessing/split-edges.py -e data/fake-graphs/3/edges-3.csv -c 0 1 2 --destination data/fake-graphs/3/categories -n data/fake-graphs/3/points.csv
python src/preprocessing/split-edges.py -e data/fake-graphs/3/edges-5.csv -c 0 1 2 --destination data/fake-graphs/3/categories -n data/fake-graphs/3/points.csv
python src/preprocessing/split-edges.py -e data/fake-graphs/3/edges-10.csv -c 0 1 2 --destination data/fake-graphs/3/categories -n data/fake-graphs/3/points.csv
```

To visualize:
`python src/visualization/fake-graph-viz.py -n data/fake-graphs/3/points.csv -e data/fake-graphs/3/categories/edges-10_*.csv`
