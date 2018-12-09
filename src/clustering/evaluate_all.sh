#!/bin/bash

echo "complex-with"
python src/clustering/evaluate.py --dir data/fake-graphs/complex-with > data/results/complex-with

echo "complex-missing"
python src/clustering/evaluate.py --dir data/fake-graphs/complex-missing > data/results/complex-missing

echo "ripme"
python src/clustering/evaluate.py --dir data/fake-graphs/ripme > data/results/ripme

echo "ripme-more"
python src/clustering/evaluate.py --dir data/fake-graphs/ripme-more > data/results/ripme-more

echo "ripme-more2"
python src/clustering/evaluate.py --dir data/fake-graphs/ripme-more2 > data/results/ripme-more2

echo "simple"
python src/clustering/evaluate.py --dir data/fake-graphs/simple > data/results/simple

echo "sectioned"
python src/clustering/evaluate.py --dir data/fake-graphs/sectioned > data/results/sectioned
