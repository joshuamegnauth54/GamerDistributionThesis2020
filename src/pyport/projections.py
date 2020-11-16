import networkx as nx
import pandas as pd

from gamenetattrs import add_attributes

def project_gamers(gamers_df, top, bottom):
    """Projects top onto bottom for gamers_df.

    Parameters
    ----------
    gamers_df: pandas.DataFrame
        Cleaned network as a DataFrame.
    top: string
        Top nodes (nodes to project).
    bottom: string
        Bottom nodes (nodes to project onto).

    Returns
    -------
    networkx.Graph.
    """
    G = nx.from_pandas_edgelist(gamers_df, top, bottom, edge_attr=True)
    assert(nx.bipartite.is_bipartite(G))
    Bnodes = set(gamers_df[bottom].values)
    projection = nx.bipartite.weighted_projected_graph(G, Bnodes)
    add_attributes(projection, gamers_df)
    return projection


def project_auth_sub_bsub(gamers_df: pd.DataFrame):
    """Build a bipartite network of Redditor->Subreddit with subs as
    the bottom nodes."""
    projection = project_gamers(gamers_df, "author", "subreddit")

    return projection


def project_auth_sub_bauth(gamers_df: pd.DataFrame):
    """Builds a bipartite network of Redditor->Subreddit with Redditors as the
    bottom nodes."""
    projection = project_gamers(gamers_df, "subreddit", "author")


def project_auth_tops_bauth(gamers_df: pd.DataFrame):
    """Builds a bipartite network of Redditor->Topics with Redditors as the
    bottom nodes."""
    projection = project_gamers(gamers_df, "permalink", "author")

    return projection