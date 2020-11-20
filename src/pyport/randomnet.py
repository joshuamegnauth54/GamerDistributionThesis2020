import networkx as nx
import numpy as np
from multiprocessing import Process, Queue, Value
from ctypes import c_bool


def random_graph(top_n, bottom_n, edge_n):
    G = nx.bipartite.generators.gnmk_random_graph(top_n,
                                                  bottom_n,
                                                  edge_n,
                                                  seed=314)

    # Sanity check. Useless sanity check.
    assert(nx.bipartite.is_bipartite(G))
    bnodes = {node for node, value in
              nx.get_node_attributes(G, "bipartite").items()
              if value == 1}
    return nx.bipartite.weighted_projected_graph(G, bnodes)


def random_clust(queue, keep_going,top_n, bottom_n, edge_n):
    while keep_going.value:
        # print(i)
        G = random_graph(top_n, bottom_n, edge_n)
        queue.put(nx.average_clustering(G, weight="weight"))

def random_deg_cent(queue, keep_going, top_n, bottom_n, edge_n):
    while keep_going.value:
        G = random_graph(top_n, bottom_n, edge_n)
        queue.put(nx.degree_centrality(G))


def dispatcher(gamers_df, projection, func, top="permalink", bottom="author",
               replicates=100000, processes=4):
    """Calculate replicates from random graphs.

    Parameters
    ----------
    gamers_df : pandas.DataFrame
        The data set used to generate `projection`.
    projection : nx.Graph
        Graph projection based on a bipartite representation of `gamers_df`.
    func : function
        The function should take in a Queue, thread safe bool, as well as the
        number of nodes in the two node sets.
    top : str, optional
        Top nodes in projection (nodes to project). The default is "permalink".
    bottom : str, optional
        Bottom nodes (nodes to project onto). The default is "author".
    replicates : int, optional
        Amount of replicates to generate. The default is 100000.
    processes : int, optional
        Amount of processes to launch. The default is 4.

    Returns
    -------
    reps_buff : numpy.ndarray
        Calculated replicates.
    """
    # Parameters of the random network.
    # We need the size of the two node sets as well as the edges between
    # them.
    top_n = gamers_df[top].nunique()
    bottom_n = gamers_df[bottom].nunique()
    edge_n = len(projection.edges())

    # Multiprocessing stuff.
    # A threadsafe Queue is easier than sharing a memory mapped buffer since
    # we're simply receiving floats.
    queue = Queue()
    # Synch value. The processes exit when keep_going is False.
    keep_going = Value(c_bool)
    keep_going.value = True

    # Next, let's make and launch our processes.
    handles = []
    for i in range(processes):
        proc = Process(target=func,
                       name="randomnet_{}".format(i),
                       args=(queue, keep_going, top_n, bottom_n, edge_n))
        proc.start()
        handles.append(proc)

    # Now we await our data.
    # Reps_buff shall hold all of the replicates.
    reps_buff = np.zeros(replicates)
    for j in range(replicates):
        # The Queue may hang if the threads implode in some way without
        # throwing an exception.
        reps_buff[j] = queue.get()

    # Stop processes by setting keep_going to False.
    # Join handles to allow processes to exit gracefully.
    keep_going.value = False
    for proc in handles:
        proc.join()

    return reps_buff

