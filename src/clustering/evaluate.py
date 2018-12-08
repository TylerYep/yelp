import csv
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse
import networkx as nx
from tqdm import tqdm
from datetime import datetime

import ccfilter
import knn
import randomwalk
import normalize
from delaunay import delaunay
import fakegraph

parser = argparse.ArgumentParser(description='evaluate all clustering methods, I guess')
parser.add_argument('--dir', '-d', help='directory containing "category.png" and "density.png", images of the categories and densities of the graphs', default='data/fake-graphs/complex-with')

def get_points_with_categories(points):
    coords = []
    rids = []
    cat_map = {}
    with open(points, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=' ', quotechar='"')
        hdr = next(reader, None)
        x_idx = hdr.index('latitude')
        y_idx = hdr.index('longitude')
        cat_idx = hdr.index('categories')
        for row in reader:
            rid = row[0]
            x = row[x_idx].replace(',', '')
            y = row[y_idx].replace(',', '')
            coords.append([float(x), float(y)])
            rids.append(rid)
            l = sorted(row[cat_idx].split(', '))
            cat_map[rid] = l
    return coords, rids, cat_map

def get_as_df(points):
    to_ret = pd.read_csv(points, ' ', header=0, quotechar='"')
    to_ret['id'] = to_ret['id'].apply(str)
    return to_ret

def get_point_info(points_file):
    coords, nids, category_map = get_points_with_categories(points_file)
    nodes = get_as_df(points_file)
    point_info = (coords, nids, category_map, nodes)
    return point_info

def get_labels(point_info, categories, label_file):
    '''
    returns {category : (set of nodes of category in higher-density, set of nodes in lower-density)}
    '''
    coords, nids, category_map, nodes = point_info
    labeldf = get_as_df(label_file)
    labeldf['label'] = labeldf['label'].apply(str)
    x = labeldf.set_index('id').to_dict('index')
    x = {k: v['label'] for k,v in x.iteritems()}
    # first is in high-density, second is not in high-density
    labels = {c : (set(),set()) for c in categories}
    for rid, cats in category_map.iteritems():
        if x[rid] not in categories:
            continue
        for cat in cats:
            if cat not in categories:
                continue
            if x[rid] == cat:
                labels[cat][0].add(rid)
            else:
                labels[cat][1].add(rid)
    return labels

def evaluate(category, nodes, labels):
    correct, wrong = labels[category] 
    both = correct.intersection(nodes)
    precision = float(len(both)) / len(nodes)
    recall = float(len(both)) / len(correct)
    f1 = 2 * precision * recall / (precision + recall)
    print "{:<10}|{:<10}|{:<10}".format('precision', 'recall', 'f1')
    print "{:10.4f}|{:10.4f}|{:10.4f}".format(precision, recall, f1)

def assess_knn(name, point_info, categories, labels, actions=['evaluate']):
    '''
    point_file: file with points
    '''
    coords, nids, category_map, nodes = point_info
    pos = {}
    for nid, coord in zip(nids, coords):
        pos[nid] = (coord[0], coord[1])

    ks = [6,8,10]
    nrows = 2
    ncols = 3
    for i, k in enumerate(ks):
        print "-"*20 + "{:02}".format(k) + "-"*20
        graph = knn.knn(nodes, k)
        for c in categories:
            cat_graph = knn.split(graph, c, category_map)
            cat_graph = ccfilter.filter_connected_components(cat_graph)
            print c
            if 'graph' in actions:
                plt.title('knn with filter and k={}'.format(k))
                plt.figure(figsize=(22,17))
                nx.draw(cat_graph, pos=pos, node_size=0)
                plt.savefig('src/clustering/figures/{}-{}-knn-{:02}.png'.format(name, c, k))

            # evaluate
            if 'evaluate' in actions:
                evaluate(c, set(cat_graph.nodes()), labels)

def 

if __name__=='__main__':
    args = parser.parse_args()
    name = os.path.basename(args.dir)
    # get info about points and their labels
    points_file, label_file = fakegraph.generate_fake_graph(args.dir)
    point_info = get_point_info(points_file)
    categories = ['1', '2']
    labels = get_labels(point_info, categories, label_file)
    assess_knn(name, point_info, categories, labels)

