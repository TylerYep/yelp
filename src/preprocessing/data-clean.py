import json
import collections

city_name = u'Montreal'

# FOR MONTREAL - Remove node 729, 1526
# FOR CALGARY - Change sign of  node 2700 latitude longitude, delete node 2459

# investigation
with open('data/yelp_business.json', 'r') as f:
    with open('data/yelp_' + city_name.lower() + '.json', 'w') as out:
        for l in f:
            ex = json.loads(l)
            categories = ex[u'categories']
            if ex[u'city'] == city_name and categories and (u'Food' in categories or u'Restaurants' in categories):
                json.dump(ex, out)
                out.write('\n')

blah = collections.defaultdict(int)

with open('data/yelp_' + city_name.lower() + '.json', 'r') as f:
    with open('data/yelp_' + city_name.lower() + '.csv', 'w') as out:
        out.write('id latitude longitude categories stars review_count\n')
        for i, line in enumerate(f):
            ex = json.loads(line)
            out.write('{business_id} {latitude} {longitude} "{categories}" {stars} {review_count}\n'.format(**ex))

