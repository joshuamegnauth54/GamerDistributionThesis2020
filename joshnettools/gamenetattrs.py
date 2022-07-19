import networkx as nx
import pandas as pd
import logging
from networkx.classes.graph import Graph
from typing import Optional

import subcolors


def parse_auth_attr(gamers_df: pd.DataFrame, node: str, attr: str) -> str:
    """Return a color based on an author's (node) most posted attribute.

    An attribute may be a subreddit or even systems.

    Parameters
    ----------
    gamers_df: pandas.DataFrame
        Gamers network data.
    node: str
        Node (author) to check.
    attr: str
        Attribute to check for most posted.

    Returns
    -------
    str
        Color for most posted attribute for author.
    """

    # Some attributes preclude some subreddits entirely. Thus, I must check
    # for a ValueError here.
    # (The above isn't accurate anymore, but I don't have time to modify
    # the function in case I break it.)
    most_posted: Optional[str] = None
    try:
        most_posted = (
            gamers_df.loc[gamers_df.author == node, attr].value_counts().idxmax()
        )
    except ValueError:
        logging.debug(f"Attribute not found: node: {node} and attr: {attr}")
    finally:
        return subcolors.subreddit_colors(most_posted)


def parse_edge_attr(gamers_df: pd.DataFrame, first: str, second: str, attr: str) -> str:
    """Return a color based on attribute first/second share in common.

    Parameters
    ----------
    gamers_df: pandas.DataFrame
        DataFrame consisting of this data:
        https://github.com/joshuamegnauth54/GamerDistributionThesis2020/blob/master/data/gamers_reddit_medium_2020.csv
    first: str
        First author/Redditor.
    second: str
        Second author/Redditor.
    attr: str
        Attribute such as subreddit, SysGamGen, System, et cetera.

    Returns
    -------
    str
        A color based on the intersection of attrs for first and second if
        they only share one of said attr or a default.
    """
    # Filter to pull the subreddits that "first" and "second" post on.
    first_attrs: set[str] = set(
        gamers_df.loc[gamers_df.author == first, attr].to_numpy()
    )
    second_attrs: set[str] = set(
        gamers_df.loc[gamers_df.author == second, attr].to_numpy()
    )

    # The intersection may be one or multiple subs.
    # Subcolors handles both situations.
    intersects: set[str] = first_attrs.intersection(second_attrs)
    logging.debug(f"({first}) ∩ ({second}) = {intersects}")

    return subcolors.subreddit_colors(intersects)


def add_attributes(G: Graph, gamers_df: pd.DataFrame) -> None:
    """Add attributes to gamers network.

    Parameters
    ----------
    G: networkx.classes.graph.Graph
        NetworkX graph from gaming network data.
    gamers_df: pandas.DataFrame
        DataFrame used to construct network G.

    Returns
    -------
    None
    """
    logging.info("Adding edge attributes to network")

    # This looks a bit messy but essentially it's:
    # {(edge): {"color": color}}
    # generated in a dictionary comprehension.
    nx.set_edge_attributes(
        G,
        {
            (first, second): {
                "sub_color": parse_edge_attr(gamers_df, first, second, "subreddit"),
                "SysGamGen": parse_edge_attr(gamers_df, first, second, "SysGamGen"),
            }
            for first, second in G.edges()
        },
    )

    logging.info("Adding node attributes to network")
    # Likewise as above but for nodes
    nx.set_node_attributes(
        G,
        {
            node: {
                "sub_color": parse_auth_attr(gamers_df, node, "subreddit"),
                "SysGamGen": parse_auth_attr(gamers_df, node, "SysGamGen"),
                "Systems": parse_auth_attr(gamers_df, node, "Systems"),
            }
            for node in G.nodes()
        },
    )
