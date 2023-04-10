import os
import pandas as pd
import matplotlib.pyplot as plt


def plot_time(data_df, fig_path):
    plt.style.use("seaborn")
    data_df = data_df.set_index("block_timestamp")["hash"]
    freq_dict = {"H": "hourly", "D": "daily", "M": "monthly"}
    for freq, freq_str in freq_dict.items():
        fig, ax = plt.subplots(figsize=(10, 6))
        count_df = data_df.groupby(pd.Grouper(freq=freq)).count()
        count_df.plot(ax=ax, label=freq_str)
        ax.set_xlabel(f"time ({freq_str})")
        ax.set_ylabel("transaction count")
        ax.legend()
        save_path = os.path.join(fig_path, f"time_{freq_str}.png")
        plt.savefig(save_path, bbox_inches="tight", dpi=200)
    plt.style.use("default")


def plot_time_account(data_df, deon_acc, phis_acc, figures_path):
    deon_idx, phis_idx = [], []
    for idx, row in data_df.iterrows():
        if (row["from_address"] in deon_acc) | (row["to_address"] in deon_acc):
            deon_idx.append(idx)

        if (row["from_address"] in phis_acc) | (row["to_address"] in phis_acc):
            deon_idx.append(idx)

    deon_df = data_df.iloc[deon_idx]
    phis_df = data_df.iloc[phis_idx]



    pass

def run():
    figures_path = "figures"
    if not os.path.exists(figures_path):
        os.makedirs(figures_path)

    data_path = os.path.join("data", "eth_data.csv")
    data_df = pd.read_csv(data_path, parse_dates=["block_timestamp"], index_col=0,
                          usecols=['Unnamed: 0', 'hash', 'from_address', 'to_address', 'value', 'block_timestamp'])

    # plot_time(data_df, figures_path)

    ens_pair_path = "../EthereumDataset/exp_ENS_pairs.txt"
    deon_acc = []
    with open(ens_pair_path, "r") as f:
        for line in f.readlines():
            pair = line.strip().split(',')
            deon_acc += pair
    deon_acc = set(pair)

    phis_path = "../EthereumDataset/exp_phishing_eoa.txt"
    phis_acc = []
    with open(phis_path, "r") as f:
        for line in f.readlines():
            phis_acc.append(line.strip())
    phis_acc = set(phis_acc)

    plot_time_account(data_df, deon_acc, phis_acc, figures_path)

if __name__ == '__main__':
    run()

