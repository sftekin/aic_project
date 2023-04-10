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
    data_df = pd.read_csv(data_path, parse_dates=["block_timestamp"], index_col=0,
                          usecols=['Unnamed: 0', 'hash', 'from_address', 'to_address', 'value', 'block_timestamp'])

    # index users without clipping data
    nodes = np.unique(data_df["from_address"].tolist() + data_df["to_address"].tolist()).tolist()
    add2id = {n: i for i, n in enumerate(nodes)}

    # clip dates
    data_df = data_df.loc[(data_df["block_timestamp"] > start_date) & (data_df["block_timestamp"] < end_date)]

    print("Creating Graph")
    edges = pd.merge(data_df.groupby(['from_address', 'to_address'])['value'].sum(),
                     data_df.groupby(['from_address', 'to_address']).size().to_frame('count'),
                     left_index=True, right_index=True).reset_index()
    edges['from_address'] = edges['from_address'].apply(lambda x: add2id[x])
    edges['to_address'] = edges['to_address'].apply(lambda x: add2id[x])
    for col in edges.columns:
        if col != 'value':
            edges[col] = edges[col].astype(int)

    json_obj = json.dumps(add2id)
    save_path = os.path.join("data", "add2id.json")
    print(f"saving as json to file {save_path}")
    with open(save_path, "w") as f:
        f.write(json_obj)

    edges.to_csv(os.path.join("data", "edges.csv"))


if __name__ == '__main__':
    str_date = "2022-02-22"  # "2017-06-22"
    e_date = "2022-03-01"    # "2022-03-01"
    create_graph(start_date=str_date, end_date=e_date)


