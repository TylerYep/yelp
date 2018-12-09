from PIL import Image
import argparse
import random
import collections
import matplotlib.pyplot as plt
import os

parser = argparse.ArgumentParser(description = 'generate fake graph using $BASE-category.png and $BASE-density.png')
parser.add_argument('--dir', '-d', help='directory of density and category files', default='data/fake-graphs/1')
args = parser.parse_args()

# dat hardcode lmao
cat_map_hex = {"c9daf8ff" : 1, "5b0f00ff" : 2, "00000000" : 0}
density_map_hex = {"00000000" : 0, "00ffffff" : 1, "4a86e8ff" : 2, "0000ffff" : 3}

def hex_to_rgb(h):
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4, 6))

cat_map = {}
density_map = {}
for c in cat_map_hex:
    cat_map[hex_to_rgb(c)] = cat_map_hex[c]
for c in density_map_hex:
    density_map[hex_to_rgb(c)] = density_map_hex[c]

print cat_map
print density_map

category_file = os.path.join(args.dir, 'category.png')
density_file = os.path.join(args.dir, 'density.png')
if not os.path.exists(category_file) or not os.path.exists(density_file):
    raise ValueError('category.png and density.png not found in given directory')

catim = Image.open(category_file)
denim = Image.open(density_file)

if catim.size != denim.size:
    print "image dimensions must be the same"
    print "{} {}".format(catim.size, denim.size)
    exit()

def pixdist(p1, p2):
    return max([abs(p1[i] - p2[i]) for i in range(len(p1))])
def round_img(pix, im, cmap, x, y):
    dists = {cat : pixdist(cat, pix[x,y]) for cat in cmap}
    mindist = float('inf')
    categ = None
    for cat in cmap:
        dist = pixdist(cat, pix[x,y])
        if dist < mindist:
            categ = cat
            mindist = dist
    return cmap[categ]

pixc = catim.load()
pixd = denim.load()
density_levels = {0 : 0, 1 : 2e-2, 2: 6e-2, 3: 18e-2}
category_density_mod = 0.4
base_prob = 0.2
points = {}
labels = {}
for x in range(catim.size[0]):
    for y in range(catim.size[1]):
        cat = round_img(pixc, catim, cat_map, x, y)
        den = round_img(pixd, denim, density_map, x, y)
        is_point = random.random()
        pixc[x,y] = {v: k for k, v in cat_map.iteritems()}[cat]
        if is_point > density_levels[den]:
            continue
        points[(x,y)] = set()
        for i in range(3):
            prob = base_prob
            label_cat = False
            if cat != 0 and i == cat:
                prob += category_density_mod
                label_cat = True
            is_cat = random.random()
            if is_cat < prob:
                points[(x,y)].add(i)
                if label_cat:
                    labels[(x,y)] = i
        if (x,y) not in labels:
            labels[(x,y)] = 0

categorized_points = collections.defaultdict(list)
for k in points:
    for cat in points[k]:
        categorized_points[cat].append(k)

colors = ['b', 'g', 'r', 'm', 'k']

for i, point_type in enumerate(categorized_points):
    type_points = categorized_points[point_type]
    xpoints, ypoints = zip(*type_points)
    plt.scatter(xpoints, ypoints, c = colors[i], marker = '.')
plt.show() 

dirname = os.path.join(args.dir)
pointfile = os.path.join(dirname, 'points.csv')
idmap = {}
with open(pointfile, 'w+') as f:
    f.write('id latitude longitude categories\n')
    it = 0
    for point in points:
        idmap[point] = it
        f.write('{} {} {} "{}"\n'.format(it, point[0], point[1], ', '.join([str(x) for x in points[point]])))
        it += 1

labelfile = os.path.join(dirname, 'labels.csv')
with open(labelfile, 'w+') as f:
    f.write('id label\n')
    for point in labels:
        f.write('{} {}\n'.format(idmap[point], labels[point]))
