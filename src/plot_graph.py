import os
import random
import shutil

import matplotlib
import networkx as nx
import numpy as np
import pandas as pd
from pyvis.network import Network
from tqdm import tqdm

from create_graph import *


def plot_graph(edges, address_list, task='deanon', mode='label', combine_addresses_flag=False, folder=''):
    '''

    :param edges:
    :param address_list: list (for phish and deanon-pred) or list of list (for deanon-label)
    :param task:
    :param mode:
    :param combine_addresses_flag:
    :return:
    '''

    assert task in ['deanon', 'phish'], 'Invalid task'
    if task == 'deanon':
        if combine_addresses_flag:
            print('Switching to combine_addresses_flag=False because the task is deanonymization')
            combine_addresses_flag = False
        if mode != 'label' and address_list and not isinstance(address_list[0], list):
            print('In deanonymization label/label_pred visualization, provide list of pairs as addresses')
            raise ValueError
        if mode == 'pred' and address_list and isinstance(address_list[0], list):
            print('In deanonymization pred visualization, provide list of addresses (not pairs)')
            raise ValueError

    address_data_path = os.path.join("data", "address_data.csv")
    address_df = pd.read_csv(address_data_path, index_col='id')
    address_df_ = address_df.set_index('address')
    address_df_['id'] = address_df.index

    preds = None
    if mode == 'pred' or mode == 'label-pred':
        if task == 'deanon':
            preds = pd.read_csv(os.path.join('../EthereumDataset', 'AIC_ENS_pred_similarity_proba_PSBERT.txt'), sep=',')
            preds['query_addr'] = preds['query_addr'].map(address_df_['id'].to_dict(), na_action='ignore')
            preds['cand_addr'] = preds['cand_addr'].map(address_df_['id'].to_dict()).astype(int)
            preds.dropna(inplace=True)
            preds['query_addr'] = preds['query_addr'].astype(int)
            preds.set_index(['query_addr', 'cand_addr'], inplace=True)
        else:
            preds = pd.read_csv(os.path.join('../EthereumDataset', 'AIC_eoa_pred_phishing_proba_BERT4ETH.txt'), sep=',')
            preds['address'] = preds['address'].map(address_df_['id'].to_dict(), na_action='ignore')
            preds.dropna(inplace=True)
            preds['address'] = preds['address'].astype(int)
            preds.set_index('address', inplace=True)

    html_path_list = []

    if combine_addresses_flag:  # can be True only in phish task
        combined_ego_graph = nx.DiGraph()
        for address in address_list:
            ego_graph = get_subgraph(edges, address)
            combined_ego_graph = nx.compose(ego_graph, combined_ego_graph)
            print(combined_ego_graph)
        graph = combined_ego_graph
        tag = f"{task}_{mode}_{'_'.join(address_list)}"
        html_path = plot_graph_helper(graph, address_df, task, mode, address_list, preds, tag, folder)
        html_path_list.append(html_path)
    else:
        if task == 'phish' or mode == 'pred':
            for address in tqdm(address_list):
                tag = f"{task}_{mode}_{address}"
                ego_graph = get_subgraph(edges, address)
                html_path = plot_graph_helper(ego_graph, address_df, task, mode, [address], preds, tag, folder)
                html_path_list.append(html_path)
        else:  # deanon label or deanon label-pred
            for pair in tqdm(address_list):
                combined_ego_graph = nx.DiGraph()
                for address in pair:
                    ego_graph = get_subgraph(edges, address)
                    combined_ego_graph = nx.compose(ego_graph, combined_ego_graph)
                tag = f"{task}_{mode}_{pair[0]}_{pair[1]}"
                html_path = plot_graph_helper(combined_ego_graph, address_df, task, mode, pair, preds, tag, folder)
                html_path_list.append(html_path)

    return html_path_list


def plot_graph_helper(graph, address_df, task, mode, address_list, preds=None, tag='', folder=''):
    # hover titles
    labels = dict([(i, address_df.loc[i]['address']) for i in graph.nodes])
    nx.set_node_attributes(graph, labels, 'title')

    if mode == 'label' or mode == 'label-pred':
        if task == 'phish':
            colors = dict([(i, 'orangered') for i in graph.nodes if address_df.loc[i]['phish_flag']])

        elif task == 'deanon':
            # color_list = get_colors()
            colors = {}
            for i in graph.nodes:
                if i in address_list:
                    colors[i] = 'orangered'
                # pair_idx = address_df.loc[i]['pair_idx']
                # if pair_idx != -1:
                #     colors[i] = color_list[pair_idx % len(color_list)]
        else:
            raise NotImplementedError

        if mode == 'label-pred':
            colors[address_list[0]] = 'black'

            labels = {}
            for i in graph.nodes:
                if task == 'phish':
                    try:
                        val = float(preds.loc[i].pred_phishing_proba)
                    except:
                        val = 0.

                else:
                    try:
                        val = float(preds.loc[address_list[0], i].pred_score)
                    except:
                        val = 0.

                if val > 0.1:
                    labels[i] = f'{val:.3f}'
            nx.set_node_attributes(graph, labels, 'label')

    else:
        colors = {}
        for i in graph.nodes:
            if task == 'phish':
                try:
                    val = float(preds.loc[i].pred_phishing_proba)
                except:
                    val = 0.

                colors[i] = matplotlib.colors.to_hex(matplotlib.colormaps['Reds'](val))

            else:
                try:
                    val = float(preds.loc[address_list[0], i].pred_score)
                except:
                    val = 0.

                colors[i] = matplotlib.colors.to_hex(matplotlib.colormaps['Reds'](val ** 5))

    nx.set_node_attributes(graph, colors, 'color')

    shapes = {}
    for i in graph.nodes:
        if address_df.loc[i]['node_type'] == 0:  # contract
            shapes[i] = 'square'
        else:  # user
            shapes[i] = 'dot'
    nx.set_node_attributes(graph, shapes, 'shape')

    # colors
    nt = Network(height="1000px", width="1000px", select_menu=True, directed=True)
    nt.from_nx(graph)
    set_graph_options(nt)

    # nt.show_buttons(filter_=['physics'])
    # nt.show_buttons()

    # nt.toggle_physics(False)
    # nt.repulsion()
    # nt.show('{tag}.html.html')

    if folder:
        html_path = os.path.join(folder, f'{tag}.html')
    else:
        html_path = f'{tag}.html'

    nt.write_html(html_path, local=True)
    # time.sleep(20)
    return html_path


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
    # one_hops = list(set(nodes_to.to_list() + nodes_from.to_list()))   # to + from

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


def get_colors(cmap='Dark2'):
    if cmap == 'random':
        colors = [c for c in matplotlib.colors.cnames.keys()]
        random.shuffle(colors)
    elif cmap in matplotlib.colormaps:
        colors = [matplotlib.colors.to_hex(c) for c in matplotlib.colormaps[cmap].colors]
    else:
        raise NotImplementedError
    return colors


if __name__ == '__main__':

    start_date = "2017-06-22"  # "2017-06-22"
    end_date = "2022-03-01"    # "2022-03-01"
    task = 'phish'  # deanon or phish
    mode = 'label-pred'   # label or pred or label-pred

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

    if task == 'phish':
        address_list = list(address_df[address_df.phish_flag == True].index)
    elif task == 'deanon':
        if mode == 'label':
            address_list = [list(address_df[address_df.pair_idx == i].index) for i in range(167)]
            address_list = [pair for pair in address_list if len(pair) == 2]
        elif mode == 'label-pred':
            address_list = [list(address_df[address_df.pair_idx == i].index) for i in range(167)]
            address_list = [pair for pair in address_list if len(pair) == 2] + \
                           [list(reversed(pair)) for pair in address_list if len(pair) == 2]
        else:
            address_list = address_df[address_df.pair_idx != -1].index.tolist()
    else:
        raise NotImplementedError

    folder = os.path.join('outputs', f'{task}_{mode}')
    if not os.path.exists(folder):
        os.makedirs(folder)

    html_path_list = plot_graph(edges, address_list=address_list, task=task, mode=mode, combine_addresses_flag=False, folder=folder)
    shutil.copytree('lib', os.path.join(folder, 'lib'))

    print(html_path_list)
