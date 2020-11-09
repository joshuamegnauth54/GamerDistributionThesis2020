import networkx as nx
import pandas as pd

import subcolors


def parse_auth_attr(gamers_df, node, attr):
    most_posted = gamers_df\
                            .loc[gamers_df.author == node, attr]\
                            .value_counts()\
                            .idxmax()

    return subcolors.subreddit_colors([most_posted])


def parse_edge_attr(gamers_df, first, second, attr):
    """Return a color based on attribute first/second share in common.

    Parameters
    ----------
    gamers_df : pandas.DataFrame
        DataFrame consisting of this data:
        https://github.com/joshuamegnauth54/GamerDistributionThesis2020/blob/master/data/gamers_reddit_medium_2020.csv
    first : str
        First author/Redditor.
    second : str
        Second author/Redditor.
    attr : str
        Attribute such as subreddit, SysGamGen, System, et cetera.

    Returns
    -------
    A color based on the intersection of attrs for first and second if
    they only share one of said attr or a default.
    """
    # Filter to pull the subreddits that "first" and "second" post on.
    first_attrs = set(gamers_df.loc[gamers_df.author == first,
                                   attr].values)

    second_attrs = set(gamers_df.loc[gamers_df.author == second,
                                   attr].values)

    # The intersection may be one or multiple subs.
    # Subcolors handles both situations.
    intersects = first_subs.intersection(second_attrs)
    # print("({}) ∩ ({}) = {}".format(first, second, intersects))

    return subcolors.subreddit_colors(intersects)


def author_edge_colors(G, gamers_df):

    # This looks a bit messy but essentially it's:
    # {(edge): {"color": color}}
    # generated in a dictionary comprehension.
    nx.set_edge_attributes(G,
                           {(first, second):
                            {"sub_color": parse_author_edges(gamers_df,
                                                             first,
                                                             second,
                                                             "subreddit")}
                            for first, second in G.edges()
                            })

    nx.set_node_attributes(G,
                           {node:
                            {"max_sub_col": parse_auth_attr(gamers_df,
                                                            node,
                                                            "subreddit"),
                             "SysGamGen": parse_auth_attr(gamers_df,
                                                          node,
                                                          "SysGamGen"),
                             "Systems": parse_auth_attr(gamers_df,
                                                        node,
                                                        "Systems")}
                            for node in G.nodes()
                            })