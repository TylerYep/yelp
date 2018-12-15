import collections
import numpy as np
import json
import requests
import csv
np.set_printoptions(edgeitems=30, linewidth=100000)
API_KEY = '' # Get it yourself
ELEMENT_LIMIT = 10
API_CALL_LIMIT = 20

def main():
    locations_arr = []
    with open('data/yelp_toronto.csv', 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=' ')
        first = True
        for row in reader:
            if first:
                first = False
                continue
            id = row[0]
            x = row[1].replace(",","")
            y = row[2].replace(",","")
            locations_arr.append([id, (float(x), float(y))])
    # Uncomment this line to fetch the distance matrix
    # get_all_distances(locations_arr[:API_CALL_LIMIT])
    construct_matrix()


def get_all_distances(locations_arr):
    ''' Gets chunks from query and stores them into a json file. '''
    all_results = []
    for chunk in range(len(locations_arr) / ELEMENT_LIMIT):
        query1 = make_query_chunk(locations_arr, chunk)
        for chunk2 in range(len(locations_arr) / ELEMENT_LIMIT):
            query2 = make_query_chunk(locations_arr, chunk2)
            distance_matrix_json = get_distance(query1, query2)
            all_results.append(distance_matrix_json)

    with open('data/distance_matrix.json', 'w') as out:
        for res_json in all_results:
            json.dump(res_json, out)
            out.write('\n')


def construct_matrix():
    shape = (ELEMENT_LIMIT - 1, ELEMENT_LIMIT - 1)
    distance_matrix = np.zeros(shape)
    duration_matrix = np.zeros(shape)
    address_to_index_map = dict()
    num_entries = 0

    with open('data/distance_matrix.json', 'r') as f:
        for line in f:
            ''' For each query result '''
            entry_batch = json.loads(line)
            origins = entry_batch[u'origin_addresses']
            dests = entry_batch[u'destination_addresses']
            for origin_address in origins:
                if origin_address not in address_to_index_map:
                    address_to_index_map[origin_address] = num_entries
                    num_entries += 1

            for dest_address in dests:
                if dest_address not in address_to_index_map:
                    address_to_index_map[dest_address] = num_entries
                    num_entries += 1

            for i, row in enumerate(entry_batch[u'rows']):
                for j, elem in enumerate(row[u'elements']):
                    r = address_to_index_map[origins[i]]
                    c = address_to_index_map[dests[j]]

                    distance_matrix[r][c] = elem[u'distance'][u'value']
                    duration_matrix[r][c] = elem[u'duration'][u'value']

    print(distance_matrix)
    print(duration_matrix)
    dist_df = distance_matrix


def make_query_chunk(locations_arr, chunk):
    origins_and_dests = []
    # if len(locations_arr) - chunk * ELEMENT_LIMIT < ELEMENT_LIMIT:
    #     for i in range(len(locations_arr) - chunk * ELEMENT_LIMIT, len(locations_arr)):
    #         l1 = locations_arr[i][1]
    #         origins_and_dests.append('enc:' + polyline.encode([l1]) + ':')
    # else:
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


def get_distance(locs1, locs2):
    headr = dict()
    headr['key'] = API_KEY
    headr['origins'] = locs1
    headr['destinations'] = locs2
    req = requests.get("https://maps.googleapis.com/maps/api/distancematrix/json", params=headr)
    return req.json()


if __name__ == '__main__':
    main()
