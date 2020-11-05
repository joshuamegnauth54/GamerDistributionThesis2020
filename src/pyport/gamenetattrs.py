import networkx as nx
import pandas as pd

import subcolors


def parse_author_edges(gamers_df, first, second):
    """
    Parameters
    ----------
    gamers_df : pandas.DataFrame
        DataFrame consisting of this data:
        https://github.com/joshuamegnauth54/GamerDistributionThesis2020/blob/master/data/gamers_reddit_medium_2020.csv
    first : str
        First author/Redditor.
    second : str
        Second author/Redditor.

    Returns
    -------
    A color based on the intersection of subs first and second posted on if
    they only share one sub or a default.
    """
    # Filter to pull the subreddits that "first" and "second" post on.
    first_subs = set(gamers_df.loc[gamers_df.author == first,
                                   "subreddit"].values)

    second_subs = set(gamers_df.loc[gamers_df.author == second,
                                   "subreddit"].values)

    # The intersection may be one or multiple subs.
    # Subcolors handles both situations.
    intersects = first_subs.intersection(second_subs)

    return subcolors.subreddit_colors(intersects)


def author_edge_colors(G, gamers_df):

    # This looks a bit messy but essentially it's:
    # {(edge): {"color": color}}
    # generated in a dictionary comprehension.
    nx.set_edge_attributes(G,
                           {(first, second):
                            {"color": parse_author_edges(gamers_df,
                                                         first,
                                                         second)}
                            for first, second in G.edges()})


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
    author_edge_colors(projection, gamers_df)
    return projection


def project_auth_sub_bsub(gamers_df: pd.DataFrame):
    """Builds a bipartite network of Redditor->Subreddit with subs as
    the bottom nodes."""
    projection = project_gamers(gamers_df, "author", "subreddit")

    return projection


def project_auth_sub_bauth(gamers_df: pd.DataFrame):
    """Builds a bipartite network of Redditor->Subreddit with Redditors as the
    bottom nodes."""
    projection = project_gamers(gamers_df, "subreddit", "author")


def project_auth_tops_btopics(gamers_df: pd.DataFrame):
    """Builds a bipartite network of Redditor->Topics with Redditors as the
    bottom nodes."""
    projection = project_gamers(gamers_df, "permalink", "author")