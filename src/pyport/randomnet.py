import networkx as nx
import numpy as np

def random_test(gamers_df, projection, top="permalink", bottom="author"):
    G = nx.bipartite.generators.gnmk_random_graph(gamers_df[top].nunique(),
                                                  gamers_df[bottom].nunique(),
                                                  len(projection.edges()))

    # Sanity check. Useless sanity check.
    assert(nx.bipartite.is_bipartite(G))
    bnodes = {node for node, value in
              nx.get_node_attributes(G, "bipartite").items()
              if value == 1}
    return nx.bipartite.weighted_projected_graph(G, bnodes)

def random_clust(gamers_df, projection, top="permalink", bottom="author",
                 replicates=100000):
    rep_buff = np.zeros(replicates)

    for i in range(replicates):
        # print(i)
        G = random_test(gamers_df, projection, top, bottom)
        rep_buff[i] = nx.average_clustering(G, weight="weight")

    return rep_buff