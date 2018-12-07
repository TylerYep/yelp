#!/bin/bash

if [ -z "$1" ]; then
    echo 'needs an argument'
    exit
fi

python src/preprocessing/generate-fake-graph.py -d data/fake-graphs/"$1" \
&& python src/graph-construction/knn.py -k 3 -f data/fake-graphs/"$1"/points.csv -o data/fake-graphs/"$1"/edges-{}.csv \
&& python src/graph-construction/knn.py -k 5 -f data/fake-graphs/"$1"/points.csv -o data/fake-graphs/"$1"/edges-{}.csv \
&& python src/graph-construction/knn.py -k 7 -f data/fake-graphs/"$1"/points.csv -o data/fake-graphs/"$1"/edges-{}.csv \
&& python src/graph-construction/knn.py -k 10 -f data/fake-graphs/"$1"/points.csv -o data/fake-graphs/"$1"/edges-{}.csv \
&& python src/preprocessing/split-edges.py -e data/fake-graphs/"$1"/edges-knn_3.csv -c 0 1 2 --destination data/fake-graphs/"$1"/categories -n data/fake-graphs/"$1"/points.csv \
&& python src/preprocessing/split-edges.py -e data/fake-graphs/"$1"/edges-knn_5.csv -c 0 1 2 --destination data/fake-graphs/"$1"/categories -n data/fake-graphs/"$1"/points.csv \
&& python src/preprocessing/split-edges.py -e data/fake-graphs/"$1"/edges-knn_7.csv -c 0 1 2 --destination data/fake-graphs/"$1"/categories -n data/fake-graphs/"$1"/points.csv \
&& python src/preprocessing/split-edges.py -e data/fake-graphs/"$1"/edges-knn_10.csv -c 0 1 2 --destination data/fake-graphs/"$1"/categories -n data/fake-graphs/"$1"/points.csv \
&& python src/graph-construction/delaunay.py -f data/fake-graphs/"$1"/points.csv -o data/fake-graphs/"$1"/delaunay.csv -d data/fake-graphs/"$1"/categories -c 0 1 2 \
&& python src/experimental/autoclust-investigation.py graph --default -d data/fake-graphs/"$1" --normalize angle --full \
&& python src/experimental/autoclust-investigation.py graph --default -d data/fake-graphs/"$1" --normalize edge --full
