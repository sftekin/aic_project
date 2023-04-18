import pandas as pd
import numpy as np
import pickle as pkl
from tqdm import tqdm
from numpy import dot
from numpy.linalg import norm


def euclidean_dist(a, b):
    return np.sqrt(np.sum(np.square(a - b)))


def cosine_dist(a, b):
    return 1 - dot(a, b) / (norm(a) * norm(b))  # notice, here need 1-


def cosine_dist_multi(a, b):
    num = dot(a, b.T)
    denom = norm(a) * norm(b, axis=1)
    res = num / denom
    return -1 * res


def euclidean_dist_multi(a, b):
    return np.sqrt(np.sum(np.square(b - a), axis=1))


def get_neighbors(X, idx, metric="cosine", include_idx_mask=[]):
    a = X[idx, :]
    indices = list(range(X.shape[0]))
    if metric == "cosine":
        # dist = np.array([cosine_dist(a, X[i, :]) for i in indices])
        dist = cosine_dist_multi(a, X)
    elif metric == "euclidean":
        dist = euclidean_dist_multi(a, X)
    else:
        raise ValueError("Distance Metric Error")
    sorted_df = pd.DataFrame(list(zip(indices, dist)), columns=["idx", "dist"]).sort_values("dist")
    sorted_df = sorted_df.drop(index=idx)  # exclude self distance
    indices = list(sorted_df["idx"])
    distances = list(sorted_df["dist"])

    if len(include_idx_mask) > 0:
        # filter indices
        indices_tmp = []
        distances_tmp = []
        for i, res_idx in enumerate(indices):
            if res_idx in include_idx_mask:
                indices_tmp.append(res_idx)
                distances_tmp.append(distances[i])
        indices = indices_tmp
        distances = distances_tmp
    return indices, distances


def query_topk(query_address, top_k):
    embedding_input_file = "./data/ts_embedding_bert4eth_1M_min3_dup_seq100_mask80_shared_zipfan1000_72000.npy"
    X = np.load(embedding_input_file)

    address_input_file = "./data/ts_address_bert4eth_1M_min3_dup_seq100_mask80_shared_zipfan1000_72000.npy"
    address_list = np.load(address_input_file)

    # map address to int
    cnt = 0
    address_to_idx = {}
    idx_to_address = {}
    for address in address_list:
        address_to_idx[address] = cnt
        idx_to_address[cnt] = address
        cnt += 1

    query_idx = address_to_idx[query_address]

    indices, distances = get_neighbors(X, query_idx, "euclidean")
    top_address_list = list(map(lambda x: idx_to_address[x], indices[:top_k]))
    top_distance_list = distances[:top_k]

    return top_address_list, top_distance_list


def load_embedding():
    embeddings = np.load("./data/ts_embedding_bert4eth_1M_min3_dup_seq100_mask80_shared_zipfan1000_72000.npy")
    address_for_embedding = np.load("./data/ts_address_bert4eth_1M_min3_dup_seq100_mask80_shared_zipfan1000_72000.npy")
    return embeddings, address_for_embedding
