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

    address_data_path = os.path.join("data", "address_data.csv")
    edge_data_path = os.path.join("data", "edges.csv")
    data_path = os.path.join("data", "eth_data.csv")
    data_df = pd.read_csv(data_path, parse_dates=["block_timestamp"], index_col=0,
                          usecols=['Unnamed: 0', 'hash', 'from_address', 'to_address', 'value', 'block_timestamp'])

    # index users without clipping data
    nodes = np.unique(data_df["from_address"].tolist() + data_df["to_address"].tolist()).tolist()

    phish_path = os.path.join("../EthereumDataset", "exp_phishing_eoa.txt")
    phish_acc_list = []
    with open(phish_path, "r") as f:
        for line in f.readlines():
            phish_acc_list.append(line)

    pair_path = os.path.join("../EthereumDataset", "exp_ENS_pairs.txt")
    phish_pair_list = []
    with open(pair_path, "r") as f:
        counter = 0
        for line in f.readlines():
            if counter % 2 == 0:
                phish_pair_list.append(line.strip().split(','))
            counter += 1

    if os.path.isfile(address_data_path):
        address_df = pd.read_csv(address_data_path, index_col='id')
    else:
        address_list = [(i, n, n in phish_acc_list, get_pair_idx(phish_pair_list, n)) for i, n in enumerate(nodes)]
        address_df = pd.DataFrame.from_records(address_list, columns=['id', 'address', 'phish_flag', 'pair_idx'], index='id')
        address_df.to_csv(address_data_path)

    address_df_ = address_df.set_index('address')
    address_df_['id'] = address_df.index
    # clip dates
    data_df = data_df.loc[(data_df["block_timestamp"] > start_date) & (data_df["block_timestamp"] < end_date)]

    print("Creating Graph")
    edges = pd.merge(data_df.groupby(['from_address', 'to_address'])['value'].sum(),
                     data_df.groupby(['from_address', 'to_address']).size().to_frame('count'),
                     left_index=True, right_index=True).reset_index()
    edges['from_address'] = edges['from_address'].apply(lambda x: address_df_.loc[x]['id'])
    edges['to_address'] = edges['to_address'].apply(lambda x: address_df_.loc[x]['id'])
    for col in edges.columns:
        if col != 'value':
            edges[col] = edges[col].astype(int)
    # edges.sort_values(by='id', inplace=True)
    edges.to_csv(edge_data_path)


def get_pair_idx(phish_pair_list, address):
    phish_pair_list_flat = [item for pair in phish_pair_list for item in pair]
    try:
        idx = phish_pair_list_flat.index(address) // 2
    except:
        idx = -1
    return idx


if __name__ == '__main__':
    str_date = "2022-02-22"  # "2017-06-22"
    e_date = "2022-03-01"    # "2022-03-01"
    create_graph(start_date=str_date, end_date=e_date)


