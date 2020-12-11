import networkx as nx

# from matplotlib.patches import Patch

from gamenetloader import load
from projections import project_auth_tops_bauth
from gamersdraw import draw_degree_centrality, draw_diameter_radius,\
    draw_k_core_decompose, add_network_leg, draw_lollypop
from randomnet import dispatcher, random_clust, random_density,\
    random_deg_assort, random_assort
from pvalueplots import p_value_plots

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
    # Note to self: subgraph isn't a copy so this breaks.
    # lcc.name = "LCC of {}".format(projection.name)
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


# Lots of duplicated code. Oops. I realized I like how I did it for 790.
def draw_and_save(projection, gamers_df, path="../../assets/",
                  k_range=range(8, 16, 4)):
    print("Drawing graph augmented with degree centrality.")
    fig, ax, _ = draw_degree_centrality(projection, alpha=0.6)

    # Add legend and title
    add_network_leg(fig, ax, "Size = degree centrality",
                    [("#ff79c6", "Systems/consoles"),
                     ("#50fa7b", "Games or game series"),
                     ("#8be9fd", "Miscellaneous")])

    # Save the rendered network.
    fig.savefig(path + "network_degcent.png", bbox_inches="tight")

    # K-core decomposition
    print("Calculating largest connected component.")
    lcc = largest_connected_component(projection)
    print("Drawing diameter and radius.")
    fig, ax = draw_diameter_radius(lcc)
    fig.savefig(path + "network_diarad.png", bbox_inches="tight")

    for k_min in k_range:
        k_max = k_min + 4
        print("Drawing k core for k {} -> {}".format(k_min, k_max))
        fig, ax = draw_k_core_decompose(projection, range(k_min, k_max))
        fig.savefig(path + "network_k_core_{}_{}.png".format(k_min, k_max),
                    bbox_inches="tight")

    print("Calculating average clustering replicates.")
    N_reps = 10000
    processes = 7

    clust_obs = nx.average_clustering(projection, weight="weight")
    clust_reps = dispatcher(gamers_df, random_clust, replicates=N_reps,
                            processes=processes)

    print("Calculating network density replicates.")
    dens_obs = nx.density(projection)
    dens_reps = dispatcher(gamers_df, random_density, replicates=N_reps,
                           processes=processes)

    print("Calculating random degree assortativity replicates.")
    deg_obs = nx.degree_pearson_correlation_coefficient(projection,
                                                        weight="weight")
    deg_reps = dispatcher(gamers_df, random_deg_assort, replicates=N_reps,
                          processes=processes)

    print("Calculating random assortativity replicates.")
    assort_obs = nx.attribute_assortativity_coefficient(projection,
                                                        "SysGamGen")
    assort_reps = dispatcher(gamers_df, random_assort, replicates=N_reps,
                             processes=processes, assort="SysGamGen")

    print("Drawing p-values plots (without p-values though)")
    fig, ax = p_value_plots([clust_obs, dens_obs, deg_obs, assort_obs],
                            [clust_reps, dens_reps, deg_reps, assort_reps],
                            ["Average clustering",
                             "Density",
                             "Degree assortativity",
                             "Assortativity on Systems, Games, & General"],
                            False,
                            False)
    # Suptitle breaks for some reason if bbox_inches isn't set to tight.
    # Also, I have no idea why it works above.
    fig.savefig(path + "metrics_dist.png", bbox_inches="tight")

    fig, ax = p_value_plots([clust_obs, dens_obs, deg_obs, assort_obs],
                            [clust_reps, dens_reps, deg_reps, assort_reps],
                            ["Average clustering",
                             "Density",
                             "Degree assortativity",
                             "Assortativity on Systems, Games, & General"],
                            plot_p=False)
    fig.savefig(path + "metrics_dist_w_obs.png", bbox_inches="tight")


def print_useful_metrics(projection, attributes=None):

    # Using a mutable list is bad default practice, I think.
    if not attributes:
        attributes = ["SysGamGen", "Systems"]

    lcc = largest_connected_component(projection)
    # Avoid recalculating eccentricity
    lcc_ecc = nx.eccentricity(lcc)

    # Standard graph info.
    print("Full:\n{}".format(nx.info(projection)))
    print("LCC:\n{}".format(nx.info(lcc)))

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

    # Density
    print("Density: {}".format(nx.density(projection)))
    print("LCC density: {}".format(nx.density(lcc)))

    # Degree assortativity
    print("Degree assortativity: {}".format(
        nx.degree_assortativity_coefficient(projection, weight="weight")))
    print("LCC degree assortativity: {}".format(
        nx.degree_assortativity_coefficient(lcc, weight="weight")))

    # Attribute assortativity
    for attr in attributes:
        print("{} assortativity: {}".format(
            attr,
            nx.attribute_assortativity_coefficient(projection, attr)))
        print("LCC {} assortativity: {}".format(
            attr,
            nx.attribute_assortativity_coefficient(lcc, attr)))
