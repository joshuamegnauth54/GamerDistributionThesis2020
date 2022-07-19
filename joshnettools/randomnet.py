import networkx as nx
import numpy as np
import numpy.typing as npt
import pandas as pd
import logging
import multiprocessing

from numpy.random import Generator
from networkx import Graph
from multiprocessing import Process, Value
from multiprocessing.queues import Queue
from multiprocessing.sharedctypes import Synchronized
from ctypes import c_bool
from typing import Any, Optional, Mapping
from collections.abc import Callable


def random_graph(top_n: int, bottom_n: int, edge_n: int) -> Graph:
    """Generate a random bipartite graph and return its projection.

    Parameters
    ----------
    top_n: int
        Number of top nodes.
    bottom_n: int
        Number of bottom nodes (nodes to project on).
    edge_n: Number of edges between the node sets.

    Returns
    -------
    Graph
        Projected random bipartite graph.
    """
    # Generate a random graph using the parameters of a previously created
    # graph
    G: Graph = nx.bipartite.generators.gnmk_random_graph(top_n, bottom_n, edge_n)

    # Sanity check. Useless sanity check.
    assert nx.bipartite.is_bipartite(G)
    # The bottom/right nodes are set as 1 under the "bipartite" attribute.
    # So, I pull out those nodes using a set comprehension to pass to
    # bipartite.weighted_projected_graph.
    bnodes: set[int] = {
        node
        for node, value in nx.get_node_attributes(G, "bipartite").items()
        if value == 1
    }
    return nx.bipartite.weighted_projected_graph(G, bnodes)


def random_clust(
    queue: Queue[np.floating],
    keep_going: Synchronized[c_bool],
    top_n: int,
    bottom_n: int,
    edge_n: int,
    _unused: Optional[int],
) -> None:
    """Generate average clustering replicates.

    Parameters
    ----------
    queue: multiprocessing.queues.Queue[numpy.floating]
        Queue to push calculated replicates.
    keep_going: multiprocessing.sharedctypes.Synchronized[ctypes.c_bool]
        Wrapped c_bool which is synchronized between threads.
    top_n: int
        Node counts for the top or left set.
    bottom_n: int
        Node counts for the bottom or right set. Top nodes are projected onto
        bottom nodes.
    edge_n: int
        Edge counts between top and bottom.
    """
    while keep_going.value:
        # print(i)
        G: Graph = random_graph(top_n, bottom_n, edge_n)
        queue.put(nx.average_clustering(G, weight="weight"))


def random_density(
    queue: Queue[np.floating],
    keep_going: Synchronized[c_bool],
    top_n: int,
    bottom_n: int,
    edge_n: int,
    _unused: Optional[int],
) -> None:
    """Generate density replicates.

    Parameters
    ----------
    queue: multiprocessing.queues.Queue[numpy.floating]
        Queue to push calculated replicates.
    keep_going: multiprocessing.sharedctypes.Synchronized[ctypes.c_bool]
        Wrapped c_bool which is synchronized between threads.
    top_n: int
        Node counts for the top or left set.
    bottom_n: int
        Node counts for the bottom or right set. Top nodes are projected onto
        bottom nodes.
    edge_n: int
        Edge counts between top and bottom.
    """
    while keep_going.value:
        G: Graph = random_graph(top_n, bottom_n, edge_n)
        # Density is the actual edges/possible edges
        queue.put(nx.density(G))


def random_deg_cent(
    queue: Queue[np.floating],
    keep_going: Synchronized[c_bool],
    top_n: int,
    bottom_n: int,
    edge_n: int,
    _unused: Optional[int],
) -> None:
    """Generate random degree centrality replicates.


    Parameters
    ----------
    queue: multiprocessing.queues.Queue[numpy.floating]
        Queue to push calculated replicates.
    keep_going: multiprocessing.sharedctypes.Synchronized[ctypes.c_bool]
        Wrapped c_bool which is synchronized between threads.
    top_n: int
        Node counts for the top or left set.
    bottom_n: int
        Node counts for the bottom or right set. Top nodes are projected onto
        bottom nodes.
    edge_n: int
        Edge counts between top and bottom.
    """
    while keep_going.value:
        G: Graph = random_graph(top_n, bottom_n, edge_n)
        queue.put(np.mean(np.fromiter(nx.degree_centrality(G).values(), np.float64)))


def random_deg_assort(
    queue: Queue[np.floating],
    keep_going: Synchronized[c_bool],
    top_n: int,
    bottom_n: int,
    edge_n: int,
    _unused: Optional[int],
) -> None:
    """Generate degree assortativity replicates.

    Parameters
    ----------
    queue: multiprocessing.queues.Queue[numpy.floating]
        Queue to push calculated replicates.
    keep_going: multiprocessing.sharedctypes.Synchronized[ctypes.c_bool]
        Wrapped c_bool which is synchronized between threads.
    top_n: int
        Node counts for the top or left set.
    bottom_n: int
        Node counts for the bottom or right set. Top nodes are projected onto
        bottom nodes.
    edge_n: int
        Edge counts between top and bottom.
    """
    while keep_going.value:
        G: Graph = random_graph(top_n, bottom_n, edge_n)
        queue.put(nx.degree_pearson_correlation_coefficient(G, weight="weight"))


def random_assort(
    queue: Queue[np.floating],
    keep_going: Synchronized[c_bool],
    top_n: int,
    bottom_n: int,
    edge_n: int,
    unique_attr: Optional[int],
) -> None:
    """Generate attribute assortativity replicates.

    Parameters
    ----------
    queue: multiprocessing.queues.Queue[numpy.floating]
        Queue to push calculated replicates.
    keep_going: multiprocessing.sharedctypes.Synchronized[ctypes.c_bool]
        Wrapped c_bool which is synchronized between threads.
    top_n: int
        Node counts for the top or left set.
    bottom_n: int
        Node counts for the bottom or right set. Top nodes are projected onto
        bottom nodes.
    edge_n: int
        Edge counts between top and bottom.
    unique_attr: int
        Number of unique values for the assortativity attribute.
    """
    # Use unique_attr to generate unique (i.e. 0 to unique_attr) classes
    # for an attribute, attr_name
    # attr: npt.NDArray[np.int_] = np.arange(0, unique_attr, 1)
    assert unique_attr is not None
    attr_name: str = "attribute"
    rng: Generator = np.random.default_rng()

    while keep_going.value:
        G: Graph = random_graph(top_n, bottom_n, edge_n)
        # Generate a random attribute value for attr_name
        nx.set_node_attributes(
            G,
            {node: rng.integers(0, unique_attr) for node in G.nodes()},
            attr_name,
        )
        queue.put(nx.attribute_assortativity_coefficient(G, attr_name))


def dispatcher(
    gamers_df: pd.DataFrame,
    func: Callable[
        [Queue[np.floating], Synchronized[c_bool], int, int, int, Optional[int]], None
    ],
    top: str = "permalink",
    bottom: str = "author",
    replicates: int = 100000,
    processes: int = 6,
    timeout: int = 60,
    assort: Optional[str] = None,
) -> npt.NDArray[np.floating]:
    """Calculate replicates from random graphs.

    Parameters
    ----------
    gamers_df: pandas.DataFrame
        A data set with a bipartite structure.
    func: Callable[Queue[np.floating], Value[c_bool], int, int, int, Optional[int]], None]
        The function should take in a Queue, thread safe bool, as well as the
        number of nodes in the two node sets. Calculating attribute assortativity
        requires an additional integer for the amount of values present in and
        attribute.
    top: str, optional
        Top nodes in gamers_df (nodes to project). The default is "permalink".
    bottom: str, optional
        Bottom nodes (nodes to project onto). The default is "author".
    replicates: int, optional
        Amount of replicates to generate. The default is 100000.
    processes: int, optional
        Amount of processes to launch. The value isn't checked for
        reasonableness. The default is 6.
    timeout: int, optional
        Timeout to wait for each single replicate and joining processes.
        Replicates may take a long time to calculate each in which case
        timeout is a failsafe mechanism to quit. A timeout is also useful
        if processes misbehave in some way. The default is 60 (seconds).
    assort: str, optional
        The top parameter is used to calculate the random attribute for
        random_assort. You may override top using assort.

    Returns
    -------
    reps_buff: npt.NDArray[np.floating]
        Calculated replicates from func. The array is the size of "replicates"
        with type numpy.float64.
    """
    # Parameters of the random network.
    # We need the size of the two node sets as well as the edges between
    # them.
    top_n: int = gamers_df[top].nunique()
    bottom_n: int = gamers_df[bottom].nunique()
    # The projection's edge length is different from the bipartite graph's
    # edges. We'll need to remake the graph as a bipartite but NOT
    # projected graph.
    edge_n: int = len(nx.from_pandas_edgelist(gamers_df, top, bottom).edges)

    # The keyword unique_attr is simply the count of unique possible
    # attributes.
    kwargs: Mapping[str, Any] = (
        {"unique_attr": gamers_df[assort or top].nunique()}
        if func is random_assort
        else {}
    )

    # Multiprocessing stuff.
    # A threadsafe Queue is easier than sharing a memory mapped buffer since
    # we're simply receiving floats.
    queue: Queue[np.floating] = multiprocessing.Queue()
    # Synch value. The processes exit when keep_going is False.
    keep_going: Synchronized[c_bool] = Value(c_bool)
    keep_going.value = c_bool(True)

    # Next, let's make and launch our processes.
    handles: list[Process] = []
    try:
        for i in range(processes):
            proc: Process = Process(
                target=func,
                name="randomnet_{}".format(i),
                args=(queue, keep_going, top_n, bottom_n, edge_n),
                kwargs=kwargs,
            )
            proc.start()
            handles.append(proc)

        # Now we await our data.
        # Reps_buff shall hold all of the replicates.
        reps_buff: npt.NDArray[np.floating] = np.zeros(replicates)
        for j in range(replicates):
            if not j % 100:
                print(f"{j} replicates calculated.")

            # The Queue may hang if the processes implode in some way without
            # throwing an exception.
            # Let's check to make sure the processes are running in case they
            # imploded.

            if not all(map(lambda proc: proc.is_alive(), handles)):
                logging.critical(f"All processes are dead. Iter: {j}")
                raise RuntimeError("All processes are dead. RIP.")

            # No single replicate should take more than a minute.
            # A few seconds, really. Timeout is a good failsafe for
            # replicates taking forever to calculate and/or process crashes.
            reps_buff[j] = queue.get(block=True, timeout=timeout)
    finally:
        # Stop processes by setting keep_going to False.
        # Join handles to allow processes to exit gracefully.
        logging.info("Closing down processes.")
        keep_going.value = c_bool(False)
        for proc in handles:
            # See above. Processes shouldn't take long to exit.
            proc.join(timeout=timeout)
            if proc.is_alive():
                logging.warning(f"{proc.name} is taking too long to stop.")
                proc.kill()

    return reps_buff
