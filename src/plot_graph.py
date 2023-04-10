import os
import random

import matplotlib
import networkx as nx
import numpy as np
import pandas as pd
from pyvis.network import Network


def plot_graph(mode='deanon'):
    address_data_path = os.path.join("data", "address_data.csv")
    edges_path = os.path.join("data", "edges.csv")

    address_df = pd.read_csv(address_data_path, index_col='id')
    edges = pd.read_csv(edges_path)
    edges['value'] = (np.log10(edges.value).clip(0) + 1).astype(int)  # for width
    edges = list(edges[['from_address', 'to_address', 'value']].itertuples(index=False, name=None))[-1000:]
    edges = [(e[0], e[1], {'width': e[-1]}) for e in edges]

    num_phish = sum([address_df.loc[e[0]]['phish_flag'] for e in edges])
    num_deanon = sum([address_df.loc[e[0]]['pair_idx'] != -1 for e in edges])
    print(f'Number of phishing flagged addresses: {num_phish}')
    print(f'Number of addresses participated in de-anonymization: {num_deanon}')

    graph = nx.DiGraph()
    graph.add_edges_from(edges)

    labels = dict([(i, address_df.loc[i]['address']) for i in graph.nodes])
    nx.set_node_attributes(graph, labels, 'title')

    if mode == 'phish':
        colors = dict([(i, 'tab:blue') if address_df.loc[i]['phish_flag'] else (i, 'tab:red') for i in graph.nodes])
    elif mode == 'deanon':
        color_list = get_colors()
        colors = {}
        for i in graph.nodes:
            pair_idx = address_df.loc[i]['pair_idx']
            if pair_idx != -1:
                colors[i] = color_list[pair_idx % len(color_list)]
        # colors = dict([(i, 'tab:blue') if address_df.loc[i]['pair_idx'] == -1 else (i, 'tab:red') for i in graph.nodes])
    else:
        raise NotImplementedError
    nx.set_node_attributes(graph, colors, 'color')

    nt = Network(height="1000px", width="1000px", select_menu=True, directed=True)
    nt.from_nx(graph)
    # set_graph_options(nt)
    nt.show_buttons(filter_=['physics'])
    # nt.toggle_physics(False)
    nt.repulsion()
    nt.show('nx.html')


def set_graph_options(nt):
    options_text_path = os.path.join("data", "options.txt")
    with open(options_text_path, "r") as f:
        nt.set_options(f.read())


def get_colors():
    colors = [c for c in matplotlib.colors.cnames.keys()]
    random.shuffle(colors)
    return colors

if __name__ == '__main__':
    plot_graph()
