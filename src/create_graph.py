import os
import json
import pickle as pkl
from tqdm import tqdm

import numpy as np
import pandas as pd
import numpy as np


def create_graph(start_date, end_date):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    data_path = os.path.join("data", "eth_data.csv")
    data_df = pd.read_csv(data_path, parse_dates=["block_timestamp"], index_col=0)

    data_df = data_df.loc[(data_df["block_timestamp"] > start_date) & (data_df["block_timestamp"] < end_date)]

    print("Creating Graph")
    nodes = np.unique(data_df["from_address"].tolist() + data_df["to_address"].tolist()).tolist()
    add2id = {n: i for i, n in enumerate(nodes)}

    # creating the graph
    edges = []
    for i in tqdm(range(len(data_df))):
        src, dst = data_df.loc[i, ["from_address", "to_address"]]
        edge = (add2id[src], add2id[dst])
        edges.append(edge)

    json_obj = json.dumps(add2id)
    save_path = os.path.join("data", "add2id.json")
    print(f"saving as json to file {save_path}")
    with open(save_path, "w") as f:
        f.write(json_obj)

    save_path = os.path.join("data", "edges.pkl")
    with open(save_path, "wb") as f:
        pkl.dump(edges, f)


if __name__ == '__main__':
    str_date = "2017-06-22"
    e_date = "2022-03-01"
    create_graph(start_date=str_date, end_date=e_date)


