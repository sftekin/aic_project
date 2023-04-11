import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def iqr_outliers(data):
    q1, q3 = np.nanquantile(data, [0.25, 0.75])
    iqr = q3 - q1
    low, high = q1 - 5*iqr, q3 + 10*iqr
    return data[(data < low) | (data > high)]


def has_outlier(data):
    return iqr_outliers(data).any()


def plot_time(data_df, fig_path, prefix="", title="", el_outlier=False):
    plt.style.use("seaborn")
    data_df = data_df["hash"]
    freq_dict = {"H": "hourly", "D": "daily", "M": "monthly"}
    for freq, freq_str in freq_dict.items():
        count_df = data_df.groupby(pd.Grouper(freq=freq)).count()

        fig, ax = plt.subplots(figsize=(10, 6))
        if has_outlier(count_df) and el_outlier:
            outs = iqr_outliers(count_df)
            # ax.scatter(outs.index, outs.to_numpy(), c="r", lw=1)
            count_df.loc[outs.index] = np.nan
            count_df = count_df.interpolate(axis=0)
        count_df.plot(ax=ax, label=freq_str)
        ax.set_xlabel(f"time ({freq_str})")
        ax.set_ylabel("transaction count")
        ax.legend()
        ax.set_title(title)
        dr = pd.date_range(count_df.index[0], count_df.index[-1], freq="M")
        dr_labels = [date.strftime("%Y-%m") for date in dr]
        ax.set_xticks(dr[::2])
        ax.set_xticklabels(dr_labels[::2], rotation=60)
        save_path = os.path.join(fig_path, f"{prefix}time_{freq_str}_{el_outlier}.png")
        plt.savefig(save_path, bbox_inches="tight", dpi=200)
    plt.style.use("default")


def plot_time_account(data_df, deon_acc, phis_acc, figures_path):
    deo_df = data_df.loc[data_df["from_address"].isin(deon_acc)]
    phis_df = data_df.loc[data_df["from_address"].isin(phis_acc)]

    plot_time(data_df=deo_df, fig_path=figures_path, prefix="deo_", title="De-anonymization (All Pairs)")
    plot_time(data_df=phis_df, fig_path=figures_path, prefix="phis_", title="Phishing (All)")


def run():
    figures_path = "figures"
    if not os.path.exists(figures_path):
        os.makedirs(figures_path)

    data_path = os.path.join("data", "eth_data.csv")
    data_df = pd.read_csv(data_path, parse_dates=["block_timestamp"], index_col=0,
                          usecols=['Unnamed: 0', 'hash', 'from_address', 'to_address', 'value', 'block_timestamp'])
    data_df = data_df.set_index("block_timestamp")

    plot_time(data_df, figures_path)

    ens_pair_path = "../EthereumDataset/exp_ENS_pairs.txt"
    deon_acc = []
    with open(ens_pair_path, "r") as f:
        for line in f.readlines():
            pair = line.strip().split(',')
            deon_acc += pair
    deon_acc = set(deon_acc)

    phis_path = "../EthereumDataset/exp_phishing_eoa.txt"
    phis_acc = []
    with open(phis_path, "r") as f:
        for line in f.readlines():
            phis_acc.append(line.strip())
    phis_acc = set(phis_acc)

    plot_time_account(data_df, deon_acc, phis_acc, figures_path)


if __name__ == '__main__':
    run()

