import networkx as nx

from gamenetloader import load
from projections import project_auth_tops_bauth
from gamersdraw import draw_degree_centrality, draw_diameter_radius,\
    draw_k_core_decompose

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
    lcc = nx.subgraph(projection,
                      sorted_components(projection)[0])
    lcc.name = "LCC of {}".format(projection.name)
    return lcc


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


def draw_and_save(projection, path="../../assets/", k_range=range(8, 16, 4)):
    print("Drawing graph augmented with degree centrality.")
    fig, ax = draw_degree_centrality(projection)
    fig.savefig(path + "network_degcent.tiff")

    print("Calculating largest connected component.")
    lcc = largest_connected_component(projection)
    print("Drawing diameter and radius.")
    fig, ax = draw_diameter_radius(lcc)
    fig.savefig(path + "network_diarad.tiff")

    for k_min in k_range:
        k_max = k_min + 4
        print("Drawing k core for k {} -> {}".format(k_min, k_max))
        fig, ax = draw_k_core_decompose(projection, range(k_min, k_max))
        fig.savefig(path + "network_k_core_{}_{}.tiff".format(k_min, k_max))


def p_value_charts(projection):
    pass


def print_useful_metrics(projection):
    lcc = largest_connected_component(projection)
    # Avoid recalculating eccentricity
    lcc_ecc = nx.eccentricity(lcc)

    # Standard graph info. The loader functions set names so these are clear.
    print(nx.info(projection))
    print(nx.info(lcc))

    # Radius and diameter are only valid for connected graphs
    print("Radius: {}".format(nx.radius(lcc, lcc_ecc)))
    print("Diameter: {}".format(nx.diameter(lcc, lcc_ecc)))

    # Number of communities
    print("Number of communities: {}".format(
        len(list(nx.community.asyn_lpa_communities(projection,
                                                   "weight", 314)))))
    print("LCC number of communities: {}".format(
        len(list(nx.community.asyn_lpa_communities(lcc,
                                                   "weight", 314)))))

    # Clustering
    print("Avg. clust: {}".format(
        nx.average_clustering(projection, weight="weight")))
    print("LCC avg. clust: {}".format(
        nx.average_clustering(lcc, weight="weight")))

    # Assortativity
    print("Degree assortativity: {}".format(
        nx.degree_assortativity_coefficient(projection, weight="weight")))
    nx.attribute_assortativity_coefficient(projection, "SysGamGen")
