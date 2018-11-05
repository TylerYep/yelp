import csv
import collections
import argparse
import os

parser = argparse.ArgumentParser(description = 'generate all categorized edge lists based on base edge list')
parser.add_argument('--edge-list-file', '-e', help='file of base edges to categorize', default='data/toronto_knn_20.csv')
parser.add_argument('--node-file', '-n', help='file of nodes', default='data/yelp_toronto.csv')
parser.add_argument('--categories', '-c', nargs='+', help='categories to split on', default=['Coffee & Tea', 'Bars', 'Sandwiches', 'Chinese'])
parser.add_argument('--counts', action='store_true', help='print category counts to help pick things to split')
parser.add_argument('--destination', default = 'data/categories', help='destination directory for categorized edge lists')

args = parser.parse_args()

edgelist = []
with open(args.edge_list_file, 'r') as f:
    reader = csv.reader(f, delimiter=',', quotechar='"')
    next(reader, None)
    for row in reader:
        edgelist.append((row[0], row[1]))

nodes = {}
category_counts = collections.defaultdict(int)
with open(args.node_file, 'r') as f:
    reader = csv.reader(f, delimiter=' ', quotechar='"')
    next(reader, None)
    for row in reader:
        l = row[3].split(', ')
        nodes[row[0]] = l
        for category in l:
            category_counts[category] += 1

if args.counts:
    category_counts_list = [(k, category_counts[k]) for k in category_counts]
    category_counts_list.sort(key = lambda p: -p[1])
    for i, tup in enumerate(category_counts_list[:20]):
        print "{0}\t{2}\t{1}".format(i+1, *tup)

# create directory if not created
if not os.path.exists(args.destination):
    os.makedirs(args.destination)
base_filename = os.path.join(args.destination, os.path.basename(args.edge_list_file).split('.')[0])

for category in args.categories:
    print category
    category_edge_list = [ edge for edge in edgelist \
            if category in nodes[edge[0]] and category in nodes[edge[1]] ]
    categoryname = category.replace(' ', '_')
    with open(base_filename + '_' + categoryname + '.csv', 'w+') as fout:
        fout.write('r1,r2\n')
        for edge in category_edge_list:
            fout.write('{},{}\n'.format(*edge))
