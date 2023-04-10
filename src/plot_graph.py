import json
import os
import pickle as pkl
import networkx as nx
import matplotlib.pyplot as plt


def plot_graph():
    add_json_path = os.path.join("data", "add2id.json")
    edges_path = os.path.join("data", "edges.pkl")

    with open(add_json_path, "r") as f:
        json_object = json.load(f)

    with open(edges_path, "rb") as f:
        edges = pkl.load(f)

    print()
    graph = nx.Graph()
    graph.add_edges_from(edges)
    labels = list(json_object.values())

    print("plotting")
    fig, ax = plt.subplots()
    nx.draw(graph, node_size=500, labels=labels, with_labels=True, ax=ax)
    plt.show()


if __name__ == '__main__':
    plot_graph()
