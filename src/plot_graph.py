import json
import os
import pickle as pkl
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network


def plot_graph():
    add_json_path = os.path.join("data", "add2id.json")
    edges_path = os.path.join("data", "edges.pkl")

    with open(add_json_path, "r") as f:
        json_object = json.load(f)

    with open(edges_path, "rb") as f:
        edges = pkl.load(f)

    node_ids = list(json_object.values())
    node_labels = list(json_object.keys())

    # # Uncomment this to run pyvis
    # net = Network(notebook=False, height="750px", width="100%")
    # net.add_nodes(node_ids, label=node_labels)
    # net.add_edges(edges)
    # net.show("edges2.html")

    # # Uncomment this to run Networkx
    graph = nx.Graph()
    graph.add_edges_from(edges)

    for node in node_ids:
        graph.add_node(node)

    print("plotting")
    fig, ax = plt.subplots(figsize=(20, 20))
    nx.draw(graph, node_size=50, width=0.5, ax=ax)
    plt.savefig("graph2.png", dpi=200, bbox_inches="tight")


if __name__ == '__main__':
    plot_graph()
