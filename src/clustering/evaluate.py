import csv
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse
import networkx as nx
from tqdm import tqdm
from datetime import datetime

import cutoff
import knn
import randomwalk
import graphnormalize
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

def draw_graph(graph, pos, title, to_save):
    '''
    graph: graph to draw, pos: position of nodes, 
    title: title of plot, to_save: location to save
    '''
    plt.figure(figsize=(22,17))
    plt.title(title)
    nx.draw(graph, pos=pos, node_size=0)
    plt.savefig(to_save)
    plt.close()

def evaluate(param, category, nodes, labels):
    correct, wrong = labels[category] 
    both = correct.intersection(nodes)
    precision = float(len(both)) / len(nodes)
    recall = float(len(both)) / len(correct)
    f1 = 2 * precision * recall / (precision + recall)
    return {'label': param, 'precision': precision, 'recall': recall, 'f1': f1}

def get_best(res):
    to_ret = {}
    for c in res:
        l = [(k,v) for k,v in res[c].iteritems()]
        l.sort(key=lambda (k,v): v['f1'], reverse=True)
        to_ret[c] = l[0][1]
    return to_ret

def assess_knn(name, point_info, categories, labels, actions=['evaluate']):
    '''
    name: name of graph being assessed
    point_info: coords (list of coordinates), nids (list of node ids), 
        category_map (map of node ids to categories), nodes (dataframe of all this info)
    categories: categories to assess
    labels: correct and incorrect high-density nodes of a given category
    actions: [evaluate/graph] -> what to do
    '''
    print 'assessing knn...'
    coords, nids, category_map, nodes = point_info
    pos = {}
    for nid, coord in zip(nids, coords):
        pos[nid] = (coord[0], coord[1])

    ks = [6,8,10]
    nrows = 2
    ncols = 3
    results = {cat : {} for cat in categories}
    for i, k in enumerate(ks):
        graph = knn.knn(nodes, k)
        for c in categories:
            cat_graph = knn.split(graph, c, category_map)
            cat_graph = cutoff.filter_connected_components(cat_graph)
            if 'graph' in actions:
                draw_graph(cat_graph, pos, 'knn with filter and k={}'.format(k), 
                        'src/clustering/figures/{}-{}-knn-{:02}.png'.format(name, c, k))
            if 'evaluate' in actions:
                res = evaluate('knn,k={}'.format(k), c, set(cat_graph.nodes()), labels)
                results[c][k] = res
    return results

def evaluate_knn(name, point_info, categories, labels):
    res = assess_knn(name, point_info, categories, labels)
    return [get_best(res)]

def assess_edgerem(name, point_info, categories, labels, actions=['evaluate'], normalize='edge'):
    '''
    name: name of graph being assessed
    point_info: coords (list of coordinates), nids (list of node ids), 
        category_map (map of node ids to categories), nodes (dataframe of all this info)
    categories: categories to assess
    labels: correct and incorrect high-density nodes of a given category
    actions: [evaluate/graph] -> what to do
    normalize: edge/angle
    '''
    print 'assessing edgerem {}...'.format(normalize)
    coords, nids, category_map, nodes = point_info
    pos = {}
    for nid, coord in zip(nids, coords):
        pos[nid] = (coord[0], coord[1])

    rounds_interval = 1
    num_its = 5
    basegraph = delaunay(coords, nids, category_map, None)
    results = {c : {} for c in categories}
    for c in categories:
        graph = delaunay(coords, nids, category_map, c)
        if normalize == 'edge':
            graph = graphnormalize.normalize_edge(graph, c, basegraph, nodes)
        else:
            graph = graphnormalize.normalize_angle(graph, c, basegraph, nodes)
        for i in range(num_its):
            num_rounds = rounds_interval * (i+1)
            graph = cutoff.remove_edges_rounds(graph, rounds_interval, True)
            cut_graph = cutoff.filter_connected_components(graph)

            if 'graph' in actions:
                draw_graph(cut_graph, pos, 
                        'edge removal: normalize={} rounds={}'.format(normalize, num_rounds), 
                        'src/clustering/figures/{}-{}-edgerem-{}-{:02}.png'.format(
                            name, c, normalize, num_rounds))
            if 'evaluate' in actions:
                res = evaluate('er,{},r={}'.format(normalize, num_rounds), c, 
                        set(cut_graph.nodes()), labels)
                results[c][num_rounds] = res
    return results

def evaluate_edgerem(name, point_info, categories, labels):
    res1 = assess_edgerem(name, point_info, categories, labels, normalize='edge')
    res2 = assess_edgerem(name, point_info, categories, labels, normalize='angle')
    return [get_best(res1), get_best(res2)]

def assess_ns(name, point_info, categories, labels, actions=['evaluate'], normalize='edge'):
    '''
    name: name of graph being assessed
    point_info: coords (list of coordinates), nids (list of node ids), 
        category_map (map of node ids to categories), nodes (dataframe of all this info)
    categories: categories to assess
    labels: correct and incorrect high-density nodes of a given category
    actions: [evaluate/graph] -> what to do
    normalize: edge/angle
    '''
    print "assessing ns {}...".format(normalize)
    coords, nids, category_map, nodes = point_info
    pos = {}
    for nid, coord in zip(nids, coords):
        pos[nid] = (coord[0], coord[1])

    rounds_interval = 1
    num_its = 5
    basegraph = delaunay(coords, nids, category_map, None)
    results = {c : {} for c in categories}
    for c in categories:
        graph = delaunay(coords, nids, category_map, c)
        if normalize == 'edge':
            graph = graphnormalize.normalize_edge(graph, c, basegraph, nodes)
        else:
            graph = graphnormalize.normalize_angle(graph, c, basegraph, nodes)
        graph = randomwalk.invert_graph_probs(graph)

        num_its = 3
        for i in range(num_its):
            num_rounds = i+1
            graph = randomwalk.ns(graph)
            cut_graph = cutoff.remove_edges(graph, 0.21, False)
            cut_graph = cutoff.filter_connected_components(cut_graph)

            if 'graph' in actions:
                draw_graph(cut_graph, pos, 
                        'randomwalk-ns: normalize={} rounds={}'.format(normalize, num_rounds), 
                        'src/clustering/figures/{}-{}-ns-{}-{:02}.png'.format(
                            name, c, normalize, num_rounds))
            if 'evaluate' in actions:
                res = evaluate('ns,{},r={}'.format(normalize, num_rounds), c, 
                        set(cut_graph.nodes()), labels)
                results[c][num_rounds] = res
    return results

def evaluate_ns(name, point_info, categories, labels):
    res1 = assess_ns(name, point_info, categories, labels, normalize='edge')
    res2 = assess_ns(name, point_info, categories, labels, normalize='angle')
    return [get_best(res1), get_best(res2)]

def assess_ce(name, point_info, categories, labels, actions=['evaluate'], normalize='edge'):
    '''
    name: name of graph being assessed
    point_info: coords (list of coordinates), nids (list of node ids), 
        category_map (map of node ids to categories), nodes (dataframe of all this info)
    categories: categories to assess
    labels: correct and incorrect high-density nodes of a given category
    actions: [evaluate/graph] -> what to do
    normalize: edge/angle
    '''
    print 'assessing ce {}...'.format(normalize)
    coords, nids, category_map, nodes = point_info
    pos = {}
    for nid, coord in zip(nids, coords):
        pos[nid] = (coord[0], coord[1])

    rounds_interval = 1
    num_its = 5
    basegraph = delaunay(coords, nids, category_map, None)
    results = {c : {} for c in categories}
    for c in categories:
        graph = delaunay(coords, nids, category_map, c)
        if normalize == 'edge':
            graph = graphnormalize.normalize_edge(graph, c, basegraph, nodes)
        else:
            graph = graphnormalize.normalize_angle(graph, c, basegraph, nodes)
        graph = randomwalk.invert_graph_probs(graph)
        graph = randomwalk.ce(graph)
        for cutp in range(0, 30, 1):
            cut = float(cutp) / 100
            cut_graph = cutoff.remove_edges(graph, cut, False)
            cut_graph = cutoff.filter_connected_components(cut_graph)

            if 'graph' in actions:
                draw_graph(cut_graph, pos, 
                        'randomwalk-ce: normalize={} cut={}'.format(normalize, cutp), 
                        'src/clustering/figures/{}-{}-ce-{}-{:02}.png'.format(
                            name, c, normalize, cutp))
            if 'evaluate' in actions:
                res = evaluate('ce,{},c={}'.format(normalize, cutp), c, 
                        set(cut_graph.nodes()), labels)
                results[c][cutp] = res
    return results

def evaluate_ce(name, point_info, categories, labels):
    res1 = assess_ce(name, point_info, categories, labels, normalize='edge')
    res2 = assess_ce(name, point_info, categories, labels, normalize='angle')
    return [get_best(res1), get_best(res2)]

def evaluate_all(name, point_info, categories, labels):
    all_res = []
    all_res.extend(evaluate_knn(name, point_info, categories, labels))
    all_res.extend(evaluate_edgerem(name, point_info, categories, labels))
    all_res.extend(evaluate_ns(name, point_info, categories, labels))
    all_res.extend(evaluate_ce(name, point_info, categories, labels))
    full_res = {}
    for c in categories:
        print '-'*20 + c + '-'*20
        l = [method_best[c] for method_best in all_res]
        l.sort(key=lambda el: el['f1'], reverse=True)
        print "{:<15}|{:<10}|{:<10}|{:<10}".format('', 'precision', 'recall', 'f1')
        for el in l:
            print "{label:<15}|{precision:10.4f}|{recall:10.4f}|{f1:10.4f}".format(**el)

if __name__=='__main__':
    args = parser.parse_args()
    name = os.path.basename(args.dir)
    # get info about points and their labels
    points_file, label_file = fakegraph.generate_fake_graph(args.dir)
    point_info = get_point_info(points_file)
    categories = ['1', '2']
    labels = get_labels(point_info, categories, label_file)
    evaluate_all(name, point_info, categories, labels)
