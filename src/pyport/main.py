import networkx as nx

from gamenetloader import load
from projections import project_auth_tops_bauth

# Maybe put these in a notebook?
# gamers_df.groupby("author").subreddit.nunique().sort_values(ascending=False)


def deg_cent_metrics(gamers_df, projection):
    """Return a sorted degree centrality dict so I don't have to keep typing
    the line below."""
    dc = sorted(nx.degree_centrality(projection).items(),
                key=lambda x: x[1])
    return dc


def sorted_components(projection):
    return sorted(nx.connected_components(projection), key=len, reverse=True)


def largest_connected_component(projection):
    return nx.subgraph(projection,
                       sorted_components(projection)[0])


def test_small(N):
    """
    Return an N sized DataFrame and projection for testing my code.

    Parameters
    ----------
    N : int
        Size of returned DataFrame.

    Returns
    -------
    (pandas.DataFrame, pandas.DataFrame, networkx.Graph)
        Full DataFrame, small DataFrame of size N, and projection of the small
        DataFrame.
    """
    gamers_full = load()
    assert(N < len(gamers_full))
    gamers_small = gamers_full.sample(N)
    return (gamers_full, gamers_small, project_auth_tops_bauth(gamers_small))
