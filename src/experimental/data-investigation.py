import json
import collections

# investigation
citystate = collections.defaultdict(int)
state = collections.defaultdict(int)
with open('data/yelp_business.json', 'r') as f:
    for l in f:
        ex = json.loads(l)
        citystate[(ex[u'state'], ex[u'city'])] += 1
        state[ex[u'state']] += 1

li = [(k, citystate[k]) for k in citystate]
li.sort(key = lambda k: -k[1])
for p in li[:10]:
    print p[0], p[1]

l2 = [(k, state[k]) for k in state]
l2.sort(key = lambda k: -k[1])
for p in l2[:10]:
    print p[0], p[1]
