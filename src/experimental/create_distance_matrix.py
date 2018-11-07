import snap
import collections
import numpy as np
import json
import polyline
import requests
import csv

API_KEY = 'AIzaSyBTHAUwdhwblKNeddbm4hkcCm_AI1pLNb0'
ELEMENT_LIMIT = 10

def main():
    api_calls = 0
    locations_arr = []
    with open('data/yelp_toronto.csv', 'r') as csvfile:
    	reader = csv.reader(csvfile, delimiter=' ')
        for row in reader:
            id = row[0]
            x = row[1].replace(",","")
            y = row[2].replace(",","")
            locations_arr.append([id, (float(x), float(y))])
    get_all_distances(locations_arr[:ELEMENT_LIMIT * 1])
    construct_matrix()



def construct_matrix():
    distance_matrix = []
    duration_matrix = []
    is_first = True
    with open('data/distance_matrix.json', 'r') as f:
        for line in f:
            entry_batch = json.loads(line)
            if is_first:
                for row in entry_batch[u'rows']:
                    dist_matrix_row, dur_matrix_row = [], []
                    for elem in row[u'elements']:
                        distance = elem[u'distance'][u'value']
                        duration = elem[u'duration'][u'value']
                        dist_matrix_row.append(distance)
                        dur_matrix_row.append(duration)
                    distance_matrix.append(dist_matrix_row)
                    duration_matrix.append(dur_matrix_row)
    print(np.array(distance_matrix))
    print(np.array(duration_matrix))



def make_query_chunk(locations_arr, chunk):
    origins_and_dests = []
    if len(locations_arr) - chunk * ELEMENT_LIMIT < ELEMENT_LIMIT:
        for i in range(len(locations_arr) - chunk * ELEMENT_LIMIT, len(locations_arr)):
            l1 = locations_arr[i][1]
            origins_and_dests.append('enc:' + polyline.encode([l1]) + ':')
    else:
        for i in range(chunk * ELEMENT_LIMIT, (chunk+1) * ELEMENT_LIMIT):
            l1 = locations_arr[i][1]
            origins_and_dests.append('enc:' + polyline.encode([l1]) + ':')

    query = ''
    first = True
    for enc in origins_and_dests:
        if first:
            first = False
        elif len(origins_and_dests) > 1:
            query += '|'
        query += enc
    return query


def get_all_distances(locations_arr):
    all_results = []
    for chunk in range(len(locations_arr) / ELEMENT_LIMIT + 1):
        for chunk2 in range(len(locations_arr) / ELEMENT_LIMIT + 1):
            query1 = make_query_chunk(locations_arr, chunk)
            query2 = make_query_chunk(locations_arr, chunk2)
            distance_matrix_json = get_distance(query1, query2)
            all_results.append(distance_matrix_json)

    with open('data/distance_matrix.json', 'w') as out:
        for res_json in all_results:
            json.dump(res_json, out)
            out.write('\n')


def get_distance(locs1, locs2):
    headr = dict()
    headr['key'] = API_KEY
    headr['origins'] = locs1
    headr['destinations'] = locs2
    req = requests.get("https://maps.googleapis.com/maps/api/distancematrix/json", params=headr)
    return req.json()


if __name__ == '__main__':
    main()
