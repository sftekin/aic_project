import os
import numpy as np
import pandas as pd
from datetime import datetime


def run():
    cur_dir = os.path.dirname(__file__)
    data_path = os.path.join(cur_dir, "../EthereumDataset/phishing_deanony_2hop_transaction.csv")

    columns = ['hash', 'block_number', 'transaction_index', 'from_address',
               'to_address', 'value', 'gas', 'gas_price', 'block_timestamp']
    data = []
    with open(data_path, "r") as f:
        for line in f.readlines():
            data.append(line.strip().split(","))
    data_df = pd.DataFrame(data, columns=columns)

    for col in ["block_number", "transaction_index", "value", "gas", "gas_price"]:
        data_df[col] = data_df[col].astype(float)
    data_df.value /= 1e18

    data_df["block_timestamp"] = data_df["block_timestamp"].astype(int)
    data_df.sort_values("block_timestamp", inplace=True)

    data_df["block_timestamp"] = data_df["block_timestamp"].apply(lambda x: pd.Timestamp(datetime.fromtimestamp(x)))
    data_df.reset_index(inplace=True)
    data_df.drop(columns=["index"], inplace=True)

    if not os.path.exists("data"):
        os.makedirs("data")
    data_df.to_csv(os.path.join(cur_dir, "data", "eth_data.csv"))


if __name__ == '__main__':
    run()
