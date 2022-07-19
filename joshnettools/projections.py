import networkx as nx
import pandas as pd
import logging

from networkx import Graph
from gamenetattrs import add_attributes


def project_gamers(gamers_df: pd.DataFrame, top: str, bottom: str) -> Graph:
    """Project top onto bottom for gamers_df.

    Parameters
    ----------
    gamers_df: pandas.DataFrame
        Cleaned network as a DataFrame.
    top: str
        Top nodes (nodes to project).
    bottom: str
        Bottom nodes (nodes to project onto).

    Returns
    -------
    networkx.Graph.
    """
    logging.info(f"Projecting {top} onto {bottom}")
    G: Graph = nx.from_pandas_edgelist(gamers_df, top, bottom, edge_attr=True)

    # NetworkX doesn't check if the graph is bipartite before projection
    # https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.bipartite.projection.weighted_projected_graph.html
    assert nx.bipartite.is_bipartite(G)
    Bnodes: set[str] = set(gamers_df[bottom].to_numpy())
    projection: Graph = nx.bipartite.weighted_projected_graph(G, Bnodes)

    # Add metadata
    add_attributes(projection, gamers_df)
    projection.name = f"Gamers network projection; top: {top} bottom: {bottom}"

    return projection


def project_auth_sub_bsub(gamers_df: pd.DataFrame) -> Graph:
    """Build a bipartite network of Redditor->Subreddit with subs as
    the bottom nodes.

    Parameters
    ----------
    gamers_df: pandas.DataFrame
        Cleaned network as a DataFrame.
    """
    return project_gamers(gamers_df, "author", "subreddit")


def project_auth_sub_bauth(gamers_df: pd.DataFrame) -> Graph:
    """Build a bipartite network of Redditor->Subreddit with Redditors as the
    bottom nodes.

    Parameters
    ----------
    gamers_df: pandas.DataFrame
        Cleaned network as a DataFrame.

    Returns
    -------
    networkx.Graph
        Graph projection.
    """
    return project_gamers(gamers_df, "subreddit", "author")


def project_auth_tops_bauth(gamers_df: pd.DataFrame) -> Graph:
    """Builds a bipartite network of Redditor->Topics with Redditors as the
    bottom nodes.

    Parameters
    ----------
    gamers_df: pandas.DataFrame
        Cleaned network as a DataFrame.

    Returns
    -------
    networkx.Graph
        Graph projection.
    """
    return project_gamers(gamers_df, "permalink", "author")
