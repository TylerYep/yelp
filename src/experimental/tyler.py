import snap
import json
from pprint import pprint

yelpf = open("../yelp_dataset/yelp_business.json", "r")
with open("../yelp_dataset/yelp_business.json") as f:
    data = json.load(f)
    pprint(data)
