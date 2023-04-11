import os
import random

import matplotlib
import networkx as nx
import numpy as np
import pandas as pd
from pyvis.network import Network
from tqdm import tqdm
import time


def plot_graph_helper(graph, address_df, tag=''):
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
                # colors[i] = 'red'
        # colors = dict([(i, 'tab:blue') if address_df.loc[i]['pair_idx'] == -1 else (i, 'tab:red') for i in graph.nodes])
    else:
        raise NotImplementedError
    nx.set_node_attributes(graph, colors, 'color')

    nt = Network(height="1000px", width="1000px", select_menu=True, directed=True)
    nt.from_nx(graph)
    # set_graph_options(nt)

    # nt.show_buttons(filter_=['physics'])
    nt.show_buttons()

    # nt.toggle_physics(False)
    # nt.repulsion()
    # nt.show('{tag}.html.html')
    nt.write_html(f'{tag}.html', local=False)
    # time.sleep(20)


def plot_graph(address_list=[], mode='deanon', combine_addresses_flag=False):

    assert mode in ['deanon', 'phish'], 'Invalid mode'
    if mode == 'deanon':
        if combine_addresses_flag:
            print('Switching to combine_addresses_flag=False because the mode is deanonymization')
            combine_addresses_flag = False
        if address_list and not isinstance(address_list[0], list):
            print('In deanonymization, provide list of pair lists as addresses')
            raise ValueError

    address_data_path = os.path.join("data", "address_data.csv")
    edges_path = os.path.join("data", "edges.csv")

    address_df = pd.read_csv(address_data_path, index_col='id')
    edges = pd.read_csv(edges_path)

    if address_list:
        if combine_addresses_flag:  # can be True only in phish mode
            combined_ego_graph = nx.DiGraph()
            for address in address_list:
                ego_graph = get_subgraph(edges, address)
                combined_ego_graph = nx.compose(ego_graph, combined_ego_graph)
                print(combined_ego_graph)
            graph = combined_ego_graph
            tag = f"{mode}_{'_'.join(address_list)}"
            plot_graph_helper(graph, address_df, tag)
        else:
            if mode == 'phish':
                for address in tqdm(address_list):
                    tag = f"{mode}_{address}"
                    ego_graph = get_subgraph(edges, address)
                    plot_graph_helper(ego_graph, address_df, tag)
            else:
                for pair in tqdm(address_list):
                    combined_ego_graph = nx.DiGraph()
                    for address in pair:
                        ego_graph = get_subgraph(edges, address)
                        combined_ego_graph = nx.compose(ego_graph, combined_ego_graph)
                    tag = f"{mode}_{pair[0]}_{pair[1]}"
                    plot_graph_helper(combined_ego_graph, address_df, tag)

    else:
        graph = nx.DiGraph()
        graph.add_edges_from(set_edge_width(edges))

        tag = f"{mode}_all"
        plot_graph_helper(graph, address_df, tag)


def set_edge_width(edges):
    edges['value'] = (np.log10(edges.value).clip(0) + 1).astype(int)  # for width
    edges = list(edges[['from_address', 'to_address', 'value']].itertuples(index=False, name=None))
    edges = [(e[0], e[1], {'width': e[-1]}) for e in edges]
    return edges


def get_subgraph(edges, node, n=2):
    if n != 2:
        raise NotImplementedError

    edges_from = edges[edges.from_address == node]
    edges_to = edges[edges.to_address == node]
    edges_list = [edges_from, edges_to]
    nodes_to = edges_from.to_address
    nodes_from = edges_to.from_address
    one_hops = list(set(nodes_to.to_list()))   # to
    one_hops = list(set(nodes_to.to_list() + nodes_from.to_list()))   # to + from

    for _node in one_hops:
        _to = edges[edges.from_address == _node]  # to
        # _from = edges[edges.to_address == _node]  # from
        edges_list.append(pd.concat([_to]))

    edges_two_hop = pd.concat(edges_list)
    edges_two_hop.drop_duplicates(inplace=True)
    edges_two_hop = set_edge_width(edges_two_hop)

    subgraph = nx.DiGraph()
    subgraph.add_edges_from(edges_two_hop)
    return subgraph


def set_graph_options(nt):
    options_text_path = os.path.join("data", "options.txt")
    with open(options_text_path, "r") as f:
        nt.set_options(f.read())


def get_colors(mode='Dark2'):
    if mode == 'random':
        colors = [c for c in matplotlib.colors.cnames.keys()]
        random.shuffle(colors)
    elif mode in matplotlib.colormaps:
        colors = [matplotlib.colors.to_hex(c) for c in matplotlib.colormaps['Dark2'].colors]
    else:
        raise NotImplementedError
    return colors


if __name__ == '__main__':
    mode = 'deanon'
    address_data_path = os.path.join("data", "address_data.csv")
    address_df = pd.read_csv(address_data_path, index_col='id')
    if mode == 'phish':
        address_list = list(address_df[address_df.phish_flag is True].index)
        print(len(address_list))
    elif mode == 'deanon':
        address_list = [list(address_df[address_df.pair_idx == i].index) for i in range(167)]
        address_list = [pair for pair in address_list if len(pair) == 2]
        print(len(address_list))
    else:
        raise NotImplementedError
    plot_graph(address_list=address_list, mode=mode, combine_addresses_flag=False)
