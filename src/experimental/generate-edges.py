import pandas as pd
from tqdm import tqdm

rest = pd.read_csv('data/yelp_toronto.csv', ' ', header = 0)

# generate edges
edge = pd.DataFrame(columns=('r1', 'r2'))
for i in tqdm(range(8000)):
    while True:
        e = rest.sample(2)['id']
        iedge = (e.iloc[0], e.iloc[1])
        if ((edge['r1'] == iedge[0]) & (edge['r2'] == iedge[1])).any():
            continue
        edge.loc[i] = iedge
        break
edge.to_csv('data/test_edges.csv', ',')
