import json
import os
import pickle as pkl
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pyvis.network import Network


def plot_graph():
    add_json_path = os.path.join("data", "add2id.json")
    edges_path = os.path.join("data", "edges.csv")

    with open(add_json_path, "r") as f:
        add2id = json.load(f)

    edges = pd.read_csv(edges_path)
    edges['value'] = (np.log10(edges.value).clip(0) + 1).astype(int)  # for width
    edges = list(edges[['from_address', 'to_address', 'value']].itertuples(index=False, name=None))[:500]
    edges = [(e[0], e[1], {'width': e[-1]}) for e in edges]

    graph = nx.DiGraph()
    graph.add_edges_from(edges)

    adds = list(add2id.keys())
    labels = dict([(i, adds[i]) for i in graph.nodes])
    nx.set_node_attributes(graph, labels, 'title')

    nt = Network(height="1000px", width="1000px", select_menu=True, directed=True)
    nt.from_nx(graph)
    # set_graph_options(nt)
    nt.show_buttons(filter_=['physics', 'nodes'])
    # nt.toggle_physics(False)
    nt.repulsion()
    nt.show('nx.html')


def set_graph_options(nt):
    options_text_path = os.path.join("data", "options.txt")
    with open(options_text_path, "r") as f:
        nt.set_options(f.read())


if __name__ == '__main__':
    plot_graph()
