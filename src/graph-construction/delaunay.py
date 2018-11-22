import snap
import pandas as pd
from scipy.spatial import Delaunay
import numpy as np
import csv
import argparse
import os

parser = argparse.ArgumentParser(description='generate graph(s) based on Delaunay triangulation and categories')
parser.add_argument('--point-file', '-f', help='file with points and categories', default='data/yelp_toronto.csv')
parser.add_argument('--output-file', '-o', help='file to output edges to', default='data/toronto_delaunay.csv')
parser.add_argument('--output-dir', '-d', help='directory to output categorized edges to', default='data/categories')
parser.add_argument('--categories', '-c', nargs='+', help='categories to isolate on', default=['Chinese', 'Bars', 'Sandwiches'])
args = parser.parse_args()

point_file = args.point_file
output_file = args.output_file
output_dir = args.output_dir
categories = args.categories

coords = []
rids = []

cat_map = {}
with open(point_file, 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter=' ', quotechar='"')
    hdr = next(reader, None) # skip header
    x_idx = hdr.index("latitude")
    y_idx = hdr.index("longitude")
    cat_idx = hdr.index("categories")
    for row in reader:
        rid = row[0]
        x = row[x_idx].replace(",","")
        y = row[y_idx].replace(",","")
    
        coords.append([float(x), float(y)])
        rids.append(rid)

        l = sorted(row[cat_idx].split(', '))
        cat_map[rid] = l

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# full delaunay
def get_delaunay_graph(coords, category = None):
    if category == None:
        points = coords
    else:
        print category
        points = []
        cat_to_full = {}
        for i, point in enumerate(coords):
            if category in cat_map[rids[i]]:
                cat_to_full[len(points)] = i
                points.append(point)
    x = np.array(points)
    tri = Delaunay(x)
    
    edges = set()
    for n in xrange(tri.nsimplex):
        for i in range(3):
            for j in range(i, 3):
                edge = sorted([tri.vertices[n, i], tri.vertices[n, j]])
                edges.add(tuple(edge))
    
    if category == None:
        output_filename = output_file
    else:
        output_filename = os.path.join(output_dir, os.path.basename(point_file).split('.')[0]) \
                + '_delaunay_' + category + '.csv'
    with open(output_filename, 'w+') as fout:
        fout.write('r1,r2\n')
        for edge in edges:
            if category != None:
                a = cat_to_full[edge[0]]
                b = cat_to_full[edge[1]]
            else:
                a = edge[0]
                b = edge[1]
            fout.write('{},{}\n'.format(rids[a], rids[b]))

# get full delaunay graph
get_delaunay_graph(coords)
# get category-specific delaunay graphs
for category in categories:
    get_delaunay_graph(coords, category)
