import json
import collections

# investigation
with open('data/yelp_academic_dataset_business.json', 'r') as f:
    with open('data/yelp_toronto.json', 'w') as out:
        for l in f:
            ex = json.loads(l)
            categories = ex[u'categories']
            if ex[u'city'] == u'Toronto' and categories and (u'Food' in categories or u'Restaurants' in categories):
                json.dump(ex, out)
                out.write('\n')

blah = collections.defaultdict(int)

with open('data/yelp_toronto.json', 'r') as f:
    with open('data/yelp_toronto.csv', 'w') as out:
        out.write('id latitude longitude categories stars\n')
        for l in f:
            ex = json.loads(l)
            out.write('{business_id} {latitude} {longitude} "{categories}" {stars}\n'.format(**ex))
