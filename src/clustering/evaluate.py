import csv
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse
import networkx as nx
from tqdm import tqdm
from datetime import datetime
import sys

import cutoff
import knn
import randomwalk
import graphnormalize
from delaunay import delaunay
import fakegraph
import comm

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

def save_graph(graph, filename):
    with open(filename, 'wb+') as f:
        f.write('r1,r2\n')
        nx.write_edgelist(graph, f, delimiter=',', data=False)

def evaluate(param, category, nodes, labels):
    correct, wrong = labels[category] 
    both = correct.intersection(nodes)
    if len(nodes) and len(correct) and len(both):
        precision = float(len(both)) / len(nodes)
        recall = float(len(both)) / len(correct)
        f1 = 2 * precision * recall / (precision + recall)
    else:
        precision = 0.0
        recall = 0.0
        f1 = 0.0
    return {'label': param, 'precision': precision, 'recall': recall, 'f1': f1}

def get_best(res):
    to_ret = {}
    for c in res:
        l = [(k,v) for k,v in res[c].iteritems()]
        l.sort(key=lambda (k,v): v['f1'], reverse=True)
        to_ret[c] = l[0][1]
    return to_ret

def assess_knn(name, point_info, categories, labels, actions=['save','load','evaluate']):
    '''
    name: name of graph being assessed
    point_info: coords (list of coordinates), nids (list of node ids), 
        category_map (map of node ids to categories), nodes (dataframe of all this info)
    categories: categories to assess
    labels: correct and incorrect high-density nodes of a given category
    actions: [evaluate/graph/save] -> what to do
    '''
    print >> sys.stderr, 'assessing knn...'
    coords, nids, category_map, nodes = point_info
    pos = {}
    for nid, coord in zip(nids, coords):
        pos[nid] = (coord[0], coord[1])


    ks = list(range(4,20))
    results = {cat : {} for cat in categories}
    if 'load' in actions:
        for k in ks:
            for c in categories:
                graphfile = 'src/clustering/graphs/{}-{}-knn-{:02}.csv'.format(name, c, k)
                if os.path.isfile(graphfile):
                    edges = pd.read_csv(graphfile, ',', header=0)
                    edges['r1'] = edges['r1'].apply(str)
                    edges['r2'] = edges['r2'].apply(str)
                    cat_graph = nx.from_pandas_edgelist(edges, source='r1', target='r2')
                    if 'evaluate' in actions:
                        res = evaluate('knn,k={}'.format(k), c, set(cat_graph.nodes()), labels)
                        results[c][k] = res

    for i, k in enumerate(ks):
        if all([k in results[c] for c in categories]):
            continue
        graph = knn.knn(nodes, k)
        for c in categories:
            cat_graph = knn.split(graph, c, category_map)
            cat_graph = cutoff.filter_connected_components(cat_graph)
            if 'evaluate' in actions:
                res = evaluate('knn,k={}'.format(k), c, set(cat_graph.nodes()), labels)
                results[c][k] = res
            if 'graph' in actions:
                draw_graph(cat_graph, pos, 'knn with filter and k={}'.format(k), 
                        'src/clustering/figures/{}-{}-knn-{:02}.png'.format(name, c, k))
            if 'save' in actions:
                save_graph(cat_graph, 
                        'src/clustering/graphs/{}-{}-knn-{:02}.csv'.format(name, c, k))
    return results

def evaluate_knn(name, point_info, categories, labels):
    res = assess_knn(name, point_info, categories, labels)
    return [get_best(res)]

def assess_edgerem(name, point_info, categories, labels, 
        actions=['save','load','evaluate'], normalize='edge'):
    '''
    name: name of graph being assessed
    point_info: coords (list of coordinates), nids (list of node ids), 
        category_map (map of node ids to categories), nodes (dataframe of all this info)
    categories: categories to assess
    labels: correct and incorrect high-density nodes of a given category
    actions: [evaluate/graph/save] -> what to do
    normalize: edge/angle
    '''
    print >> sys.stderr, 'assessing edgerem {}...'.format(normalize)
    coords, nids, category_map, nodes = point_info
    pos = {}
    for nid, coord in zip(nids, coords):
        pos[nid] = (coord[0], coord[1])

    rounds_interval = 1
    num_its = 6
    results = {c : {} for c in categories}
    if 'load' in actions:
        for c in categories:
            for rounds in range(rounds_interval, rounds_interval*num_its+1, rounds_interval):
                graphfile = 'src/clustering/graphs/{}-{}-edgerem-{}-{:02}.csv'.format(
                        name, c, normalize, rounds)
                if os.path.isfile(graphfile):
                    edges = pd.read_csv(graphfile, ',', header=0)
                    edges['r1'] = edges['r1'].apply(str)
                    edges['r2'] = edges['r2'].apply(str)
                    cut_graph = nx.from_pandas_edgelist(edges, source='r1', target='r2')
                    if 'evaluate' in actions:
                        res = evaluate('er,{},r={}'.format(normalize, rounds), c, 
                                set(cut_graph.nodes()), labels)
                        results[c][rounds] = res

    basegraph = delaunay(coords, nids, category_map, None)
    for c in categories:
        if all([(rounds_interval*(i+1)) in results[c] for i in range(num_its)]):
            continue
        graph = delaunay(coords, nids, category_map, c)
        if normalize == 'edge':
            graph = graphnormalize.normalize_edge(graph, c, basegraph, nodes)
        else:
            graph = graphnormalize.normalize_angle(graph, c, basegraph, nodes)
        for i in range(num_its):
            num_rounds = rounds_interval * (i+1)
            graph = cutoff.remove_edges_rounds(graph, rounds_interval, True)
            cut_graph = cutoff.filter_connected_components(graph)

            if 'evaluate' in actions:
                res = evaluate('er,{},r={}'.format(normalize, num_rounds), c, 
                        set(cut_graph.nodes()), labels)
                results[c][num_rounds] = res
            if 'graph' in actions:
                draw_graph(cut_graph, pos, 
                        'edge removal: normalize={} rounds={}'.format(normalize, num_rounds), 
                        'src/clustering/figures/{}-{}-edgerem-{}-{:02}.png'.format(
                            name, c, normalize, num_rounds))
            if 'save' in actions:
                save_graph(cut_graph, 
                        'src/clustering/graphs/{}-{}-edgerem-{}-{:02}.csv'.format(
                            name, c, normalize, num_rounds))
    return results

def evaluate_edgerem(name, point_info, categories, labels):
    res1 = assess_edgerem(name, point_info, categories, labels, normalize='edge')
    res2 = assess_edgerem(name, point_info, categories, labels, normalize='angle')
    return [get_best(res1), get_best(res2)]

def assess_ns(name, point_info, categories, labels, 
        actions=['save','load','evaluate'], normalize='edge'):
    '''
    name: name of graph being assessed
    point_info: coords (list of coordinates), nids (list of node ids), 
        category_map (map of node ids to categories), nodes (dataframe of all this info)
    categories: categories to assess
    labels: correct and incorrect high-density nodes of a given category
    actions: [evaluate/graph/save] -> what to do
    normalize: edge/angle
    '''
    print >> sys.stderr, "assessing ns {}...".format(normalize)
    coords, nids, category_map, nodes = point_info
    pos = {}
    for nid, coord in zip(nids, coords):
        pos[nid] = (coord[0], coord[1])

    cutps = list(range(60,61,1))
    results = {c : {} for c in categories}
    if 'load' in actions:
        for c in categories:
            for cutp in cutps:
                graphfile = 'src/clustering/graphs/{}-{}-ns-{}-{:02}.csv'.format(
                        name, c, normalize, cutp)
                if os.path.isfile(graphfile):
                    edges = pd.read_csv(graphfile, ',', header=0)
                    edges['r1'] = edges['r1'].apply(str)
                    edges['r2'] = edges['r2'].apply(str)
                    cut_graph = nx.from_pandas_edgelist(edges, source='r1', target='r2')
                    if 'evaluate' in actions:
                        res = evaluate('ns,{},c={}'.format(normalize, cutp), c, 
                                set(cut_graph.nodes()), labels)
                        results[c][cutp] = res

    basegraph = delaunay(coords, nids, category_map, None)
    for c in categories:
        if all([cutp in results[c] for cutp in cutps]):
            continue
        graph = delaunay(coords, nids, category_map, c)
        if normalize == 'edge':
            graph = graphnormalize.normalize_edge(graph, c, basegraph, nodes)
        else:
            graph = graphnormalize.normalize_angle(graph, c, basegraph, nodes)
        graph = randomwalk.invert_graph_probs(graph)
        graph = randomwalk.ns(randomwalk.ns(graph))
        for cutp in cutps:
            cut = float(cutp) / 100
            cut_graph = cutoff.remove_edges(graph, cut, False)
            cut_graph = cutoff.filter_connected_components(cut_graph)

            if 'evaluate' in actions:
                res = evaluate('ns,{},c={}'.format(normalize, cutp), c, 
                        set(cut_graph.nodes()), labels)
                results[c][cutp] = res
            if 'graph' in actions:
                draw_graph(cut_graph, pos, 
                        'randomwalk-ns: normalize={} cut={}'.format(normalize, cutp), 
                        'src/clustering/figures/{}-{}-ns-{}-{:02}.png'.format(
                            name, c, normalize, cutp))
            if 'save' in actions:
                save_graph(cut_graph,
                        'src/clustering/graphs/{}-{}-ns-{}-{:02}.csv'.format(
                            name, c, normalize, cutp))
    return results

def evaluate_ns(name, point_info, categories, labels):
    res1 = assess_ns(name, point_info, categories, labels, normalize='edge')
    res2 = assess_ns(name, point_info, categories, labels, normalize='angle')
    return [get_best(res1), get_best(res2)]

def assess_ce(name, point_info, categories, labels, 
        actions=['save','load','evaluate'], normalize='edge'):
    '''
    name: name of graph being assessed
    point_info: coords (list of coordinates), nids (list of node ids), 
        category_map (map of node ids to categories), nodes (dataframe of all this info)
    categories: categories to assess
    labels: correct and incorrect high-density nodes of a given category
    actions: [evaluate/graph/save] -> what to do
    normalize: edge/angle
    '''
    print >> sys.stderr, 'assessing ce {}...'.format(normalize)
    coords, nids, category_map, nodes = point_info
    pos = {}
    for nid, coord in zip(nids, coords):
        pos[nid] = (coord[0], coord[1])

    cutps = list(range(21,22,1))
    results = {c : {} for c in categories}
    if 'load' in actions:
        for c in categories:
            for cutp in cutps:
                graphfile = 'src/clustering/graphs/{}-{}-ce-{}-{:02}.csv'.format(
                        name, c, normalize, cutp)
                if os.path.isfile(graphfile):
                    edges = pd.read_csv(graphfile, ',', header=0)
                    edges['r1'] = edges['r1'].apply(str)
                    edges['r2'] = edges['r2'].apply(str)
                    cut_graph = nx.from_pandas_edgelist(edges, source='r1', target='r2')
                    if 'evaluate' in actions:
                        res = evaluate('ce,{},c={}'.format(normalize, cutp), c, 
                                set(cut_graph.nodes()), labels)
                        results[c][cutp] = res
    basegraph = delaunay(coords, nids, category_map, None)
    for c in categories:
        if all([cutp in results[c] for cutp in cutps]):
            continue
        graph = delaunay(coords, nids, category_map, c)
        if normalize == 'edge':
            graph = graphnormalize.normalize_edge(graph, c, basegraph, nodes)
        else:
            graph = graphnormalize.normalize_angle(graph, c, basegraph, nodes)
        graph = randomwalk.invert_graph_probs(graph)
        graph = randomwalk.ce(graph)
        for cutp in cutps:
            cut = float(cutp) / 100
            cut_graph = cutoff.remove_edges(graph, cut, False)
            cut_graph = cutoff.filter_connected_components(cut_graph)

            if 'evaluate' in actions:
                res = evaluate('ce,{},c={}'.format(normalize, cutp), c, 
                        set(cut_graph.nodes()), labels)
                results[c][cutp] = res
            if 'graph' in actions:
                draw_graph(cut_graph, pos, 
                        'randomwalk-ce: normalize={} cut={}'.format(normalize, cutp), 
                        'src/clustering/figures/{}-{}-ce-{}-{:02}.png'.format(
                            name, c, normalize, cutp))
            if 'save' in actions:
                save_graph(cut_graph,
                        'src/clustering/graphs/{}-{}-ce-{}-{:02}.csv'.format(
                            name, c, normalize, cutp))

    return results

def evaluate_ce(name, point_info, categories, labels):
    res1 = assess_ce(name, point_info, categories, labels, normalize='edge')
    res2 = assess_ce(name, point_info, categories, labels, normalize='angle')
    return [get_best(res1), get_best(res2)]

def evaluate_baseline(name, point_info, categories, labels):
    print >> sys.stderr, 'assessing baseline...'
    results = {}
    for c in categories:
        full = set([point for point in point_info[1] if c in point_info[2][point]])
        results[c] = evaluate('baseline', c, set(full), labels)
    return [results]

def assess_knn_louvain(name, point_info, categories, labels, actions=['save', 'load', 'evaluate']):
    '''
    name: name of graph being assessed
    point_info: coords (list of coordinates), nids (list of node ids), 
        category_map (map of node ids to categories), nodes (dataframe of all this info)
    categories: categories to assess
    labels: correct and incorrect high-density nodes of a given category
    actions: [evaluate/graph/save] -> what to do
    '''
    print >> sys.stderr, 'assessing knn + louvain...'
    coords, nids, category_map, nodes = point_info
    pos = {}
    for nid, coord in zip(nids, coords):
        pos[nid] = (coord[0], coord[1])

    ks = list(range(15,16,1))
    results = {cat : {} for cat in categories}
    if 'load' in actions:
        for k in ks:
            for c in categories:
                graphfile = 'src/clustering/graphs/{}-{}-kl-{:02}.csv'.format(name, c, k)
                if os.path.isfile(graphfile):
                    edges = pd.read_csv(graphfile, ',', header=0)
                    edges['r1'] = edges['r1'].apply(str)
                    edges['r2'] = edges['r2'].apply(str)
                    cat_graph = nx.from_pandas_edgelist(edges, source='r1', target='r2')
                    if 'evaluate' in actions:
                        res = evaluate('kl,k={}'.format(k), c, set(cat_graph.nodes()), labels)
                        results[c][k] = res

    for i, k in enumerate(ks):
        if all([k in results[c] for c in categories]):
            continue
        graph = knn.knn(nodes, k)
        for c in categories:
            cat_graph = knn.split(graph, c, category_map)
            cat_graph = cutoff.filter_connected_components(cat_graph)
            cat_graph = comm.filter_communities(cat_graph, comm.louvain(cat_graph), 
                    filter_on='edge_density')
            if 'evaluate' in actions:
                res = evaluate('kl,k={}'.format(k), c, set(cat_graph.nodes()), labels)
                results[c][k] = res
            if 'graph' in actions:
                draw_graph(cat_graph, pos, 'knn + louvain and k={}'.format(k), 
                        'src/clustering/figures/{}-{}-kl-{:02}.png'.format(name, c, k))
            if 'save' in actions:
                save_graph(cat_graph, 
                        'src/clustering/graphs/{}-{}-kl-{:02}.csv'.format(name, c, k))
    return results

def evaluate_knn_louvain(name, point_info, categories, labels):
    res = assess_knn_louvain(name, point_info, categories, labels)
    return [get_best(res)]

def assess_norm_louvain(name, point_info, categories, labels, 
        actions=['save','load','evaluate'], normalize='edge'):
    '''
    name: name of graph being assessed
    point_info: coords (list of coordinates), nids (list of node ids), 
        category_map (map of node ids to categories), nodes (dataframe of all this info)
    categories: categories to assess
    labels: correct and incorrect high-density nodes of a given category
    actions: [evaluate/graph/save] -> what to do
    normalize: edge/angle
    '''
    print >> sys.stderr, 'assessing norm {} + louvain...'.format(normalize)
    coords, nids, category_map, nodes = point_info
    pos = {}
    for nid, coord in zip(nids, coords):
        pos[nid] = (coord[0], coord[1])

    key = 'a'
    results = {c:{} for c in categories}
    if 'load' in actions:
        for c in categories:
            graphfile = 'src/clustering/graphs/{}-{}-nl-{}.csv'.format(
                    name, c, normalize)
            if os.path.isfile(graphfile):
                edges = pd.read_csv(graphfile, ',', header=0)
                edges['r1'] = edges['r1'].apply(str)
                edges['r2'] = edges['r2'].apply(str)
                cut_graph = nx.from_pandas_edgelist(edges, source='r1', target='r2')
                if 'evaluate' in actions:
                    res = evaluate('nl,{}'.format(normalize), c, 
                            set(cut_graph.nodes()), labels)
                    results[c][key] = res

    basegraph = delaunay(coords, nids, category_map, None)
    for c in categories:
        if key in results[c]:
            continue
        graph = delaunay(coords, nids, category_map, c)
        if normalize == 'edge':
            graph = graphnormalize.normalize_edge(graph, c, basegraph, nodes)
        else:
            graph = graphnormalize.normalize_angle(graph, c, basegraph, nodes)
        cut_graph = comm.filter_communities(graph, comm.louvain(graph), 
                filter_on='edge_length')

        if 'evaluate' in actions:
            res = evaluate('nl,{}'.format(normalize), c, 
                    set(cut_graph.nodes()), labels)
            results[c][key] = res
        if 'graph' in actions:
            draw_graph(cut_graph, pos, 
                    'norm + louvain: normalize={}'.format(normalize), 
                    'src/clustering/figures/{}-{}-nl-{}.png'.format(
                        name, c, normalize))
        if 'save' in actions:
            save_graph(cut_graph, 
                    'src/clustering/graphs/{}-{}-nl-{}.csv'.format(
                        name, c, normalize))
    return results

def evaluate_norm_louvain(name, point_info, categories, labels):
    res1 = assess_norm_louvain(name, point_info, categories, labels, normalize='edge')
    res2 = assess_norm_louvain(name, point_info, categories, labels, normalize='angle')
    return [get_best(res1), get_best(res2)]

def evaluate_all(name, point_info, categories, labels):
    all_res = []
    args = (name, point_info, categories, labels)
    all_res.extend(evaluate_baseline(*args))
    all_res.extend(evaluate_knn(*args))
    all_res.extend(evaluate_edgerem(*args))
    all_res.extend(evaluate_ns(*args))
    all_res.extend(evaluate_ce(*args))
    all_res.extend(evaluate_knn_louvain(*args))
    all_res.extend(evaluate_norm_louvain(*args))
    full_res = {}
    for c in categories:
        print '-'*20 + c + '-'*20
        l = [method_best[c] for method_best in all_res]
        l.sort(key=lambda el: el['f1'], reverse=True)
        print "{:<15}|{:<10}|{:<10}|{:<10}".format('', 'precision', 'recall', 'f1')
        for el in l:
            print "{label:<15}|{precision:10.4f}|{recall:10.4f}|{f1:10.4f}".format(**el)

def graph_all(name, point_info, categories, labels):
    args = (name, point_info, categories, labels)
    assess_knn(*args, actions=['save','load','graph'])
    assess_edgerem(*args, actions=['save','load','graph'], normalize='edge')
    assess_edgerem(*args, actions=['save','load','graph'], normalize='angle')
    assess_ns(*args, actions=['save','load','graph'], normalize='edge')
    assess_ns(*args, actions=['save','load','graph'], normalize='angle')
    assess_ce(*args, actions=['save','load','graph'], normalize='edge')
    assess_ce(*args, actions=['save','load','graph'], normalize='angle')
    assess_knn_louvain(*args, actions=['save', 'load', 'graph'])
    assess_norm_louvain(*args, actions=['save', 'load', 'graph'], normalize='edge')
    assess_norm_louvain(*args, actions=['save', 'load', 'graph'], normalize='angle')

def fake_graph(fakegraph_dir):
    name = os.path.basename(fakegraph_dir)
    points_file, label_file = fakegraph.generate_fake_graph(fakegraph_dir)
    point_info = get_point_info(points_file)
    categories = ['1', '2']
    labels = get_labels(point_info, categories, label_file)
    evaluate_all(name, point_info, categories, labels)

def actual_data(real_dir):
    name = os.path.basename(real_dir)
    points_file = os.path.join(real_dir, 'points.csv')
    point_info = get_point_info(points_file)
    categories = ['Chinese']
    labels = None
    graph_all(name, point_info, categories, labels)

if __name__=='__main__':
    args = parser.parse_args()
    actual_data(args.dir)
