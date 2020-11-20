import networkx as nx
import matplotlib.pyplot as plt


def draw_gamers(gamers, algo="sfdp", color="sub_color", edge_color="#282a36",
                size=32):
    pos = nx.nx_pydot.graphviz_layout(gamers, prog=algo)
    fig, ax = plt.subplots(figsize=(16, 16))
    nx.draw_networkx(gamers,
                     pos,
                     with_labels=False,
                     ax=ax,
                     node_size=size,
                     node_color=list(nx.get_node_attributes(gamers,
                                                            color).values()),
                     # alpha=0.75,
                     edge_color=list(nx.get_node_attributes(gamers,
                                                            edge_color).values()),
                     label=color
                     )
    fig.tight_layout()
    fig.patch.set_facecolor("#282a36")
    ax.patch.set_facecolor("#282a36")
    return (fig, ax)


def draw_degree_centrality(gamers):
    deg_cent = [dc * 10000 for dc in nx.degree_centrality(gamers).values()]
    return draw_gamers(gamers, color="SysGamGen", edge_color="sub_color",
                       size=deg_cent)


def draw_diameter_radius(lcc):
    """Draw the barycenter and periphery of the gamer network.

    Parameters
    ----------
    lcc : networkx.Graph
        Largest connected component of the gamers network projection.

    Returns
    -------
    (matplotlib.pyplot.figure, matplotlib.pyplot.Axes)
        Figure/ax of plot.
    """
    # Barycenter centrality is normalized by accounting for the total network.
    center = nx.barycenter(lcc, weight="weight")
    periphery = nx.periphery(lcc)

    # Nodes outside of the radius/diameter are pink. The center is red and
    # the periphery is yellow.
    nx.set_node_attributes(lcc, {node: "#ff5555" if node in center
                                 else "#f1fa8c" if node in periphery
                                 else "#ff79c6"
                                 for node in lcc.nodes()},
                           "CentPeri")

    # Figuring out a decent size is extraordinarily difficult.
    # I'd like for both center nodes as well as periphery nodes to stand out.
    size = [3000 if node in center
            else 1000 if node in periphery
            else 100
            for node in lcc.nodes()]

    # Plot and return (fig, ax)
    return draw_gamers(lcc, color="CentPeri", edge_color="sub_color",
                       size=size)

def draw_k_cores(projection, k_range):
    pass
