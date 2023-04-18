import os
import json
import pickle as pkl
from tqdm import tqdm

import numpy as np
import pandas as pd
import numpy as np


def create_addresses():
    data_path = os.path.join("data", "eth_data.csv")
    data_df = pd.read_csv(data_path, parse_dates=["block_timestamp"], index_col=0,
                          usecols=['Unnamed: 0', 'hash', 'from_address', 'to_address', 'value', 'block_timestamp'])

    # index users without clipping data
    nodes = np.unique(data_df["from_address"].tolist() + data_df["to_address"].tolist()).tolist()

    phish_path = os.path.join("../EthereumDataset", "exp_phishing_eoa.txt")
    with open(phish_path, "r") as f:
        phish_acc_list = f.read().splitlines()

    pair_path = os.path.join("../EthereumDataset", "exp_ENS_pairs.txt")
    deanon_pair_list = []
    with open(pair_path, "r") as f:
        counter = 0
        for line in f.readlines():
            if counter % 2 == 0:
                deanon_pair_list.append(line.strip().split(','))
            counter += 1

    type_path = os.path.join("../EthereumDataset", "AIC_node_type.txt")
    node_type_df = pd.read_csv(type_path, index_col='address')

    address_list = [(i, n, n in phish_acc_list, generate_pair_idx(deanon_pair_list, n), node_type_df.loc[n]['type']) for i, n in enumerate(nodes)]  # TODO: optimize
    address_df = pd.DataFrame.from_records(address_list, columns=['id', 'address', 'phish_flag', 'pair_idx', 'node_type'], index='id')

    return address_df


def create_edges(address_df, start_date, end_date):

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    data_path = os.path.join("data", "eth_data.csv")
    data_df = pd.read_csv(data_path, parse_dates=["block_timestamp"], index_col=0,
                          usecols=['Unnamed: 0', 'hash', 'from_address', 'to_address', 'value', 'block_timestamp'])

    # clip dates
    data_df = data_df.loc[(data_df["block_timestamp"] >= start_date) & (data_df["block_timestamp"] < end_date)]

    print("Creating Graph")
    edges = pd.merge(data_df.groupby(['from_address', 'to_address'])['value'].sum(),
                     data_df.groupby(['from_address', 'to_address']).size().to_frame('count'),
                     left_index=True, right_index=True).reset_index()

    address_df_ = address_df.set_index('address')
    address_df_['id'] = address_df.index
    edges['from_address'] = edges['from_address'].map(address_df_['id'].to_dict())
    edges['to_address'] = edges['to_address'].map(address_df_['id'].to_dict())

    for col in edges.columns:
        if col != 'value':
            edges[col] = edges[col].astype(int)
    # edges.sort_values(by='id', inplace=True)

    return edges


def generate_pair_idx(deanon_pair_list, address):
    deanon_pair_list_flat = [item for pair in deanon_pair_list for item in pair]
    try:
        idx = deanon_pair_list_flat.index(address) // 2
    except:
        idx = -1
    return idx


if __name__ == '__main__':
    start_date = "2017-06-22"  # "2017-06-22"
    end_date = "2022-03-01"    # "2022-03-01"

    address_data_path = os.path.join("data", "address_data.csv")
    edges_data_path = os.path.join("data", f"edges_{start_date}_{end_date}.csv")

    if os.path.isfile(address_data_path):
        print('Loading addresses...')
        address_df = pd.read_csv(address_data_path, index_col='id')
    else:
        print('Creating addresses...')
        address_df = create_addresses()
        address_df.to_csv(address_data_path)

    if os.path.isfile(edges_data_path):
        print('Loading edges...')
        edges = pd.read_csv(edges_data_path)
    else:
        print('Creating edges...')
        edges = create_edges(address_df, start_date=start_date, end_date=end_date)
        edges.to_csv(edges_data_path)


