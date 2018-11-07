import snap
import json
from pprint import pprint
import requests


def main():
    # with open("../yelp_dataset/yelp_business.json") as f:
    #     data = json.load(f)
    # Add all addresses and ids maybe
    loc1 = '3000 Fowler Rd'
    loc2 = '455 Arguello Way'
    get_one_distance(loc1, loc2)


def get_all_distances(locations_arr):
    distance_matrix = [[] for _ in len(locations_arr)]
    for i in range(len(locations_arr)):
        for j in range(len(locations_arr)):
            distance_matrix[i][j] = get_distance(locations_arr[i], locations_arr[j])


def get_distance(loc1, loc2):
    headr = dict()
    headr['key'] = 'AIzaSyBTHAUwdhwblKNeddbm4hkcCm_AI1pLNb0'
    headr['origins'] = loc1
    headr['destinations'] = loc2
    req = requests.get("https://maps.googleapis.com/maps/api/distancematrix/json", params=headr)
    print(req.json())


if __name__ == '__main__':
    main()
