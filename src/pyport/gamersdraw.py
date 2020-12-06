import networkx as nx
import numpy as np
import matplotlib.pyplot as plt


def draw_gamers(gamers, algo="sfdp", color="sub_color", edge_color="#f8f8f2",
                size=32, fig=None, ax=None, **kwargs):
    pos = nx.nx_pydot.graphviz_layout(gamers, prog=algo)
    if fig is None and ax is None:
        fig, ax = plt.subplots(figsize=(20, 20))
    nx.draw_networkx(gamers,
                     pos,
                     with_labels=False,
                     ax=ax,
                     node_size=size,
                     node_color=list(nx.get_node_attributes(gamers,
                                                            color).values())
                         if color[0] != '#' else color,
                     # alpha=0.75,
                     edge_color=list(nx.get_node_attributes(gamers,
                                                            edge_color).values())
                         if edge_color[0] != '#' else edge_color,
                     label=color,
                     **kwargs
                     )
    fig.tight_layout()
    fig.patch.set_facecolor("#282a36")
    ax.patch.set_facecolor("#282a36")
    return fig, ax


def draw_degree_centrality(gamers, offset=10000, color="SysGamGen",
                           edge_color="sub_color", **kwargs):
    """Plot gamers with node sizes determined by degree centrality * offset.

    Parameters
    ----------
    gamers : networkx.Graph
        Graph to plot.
    offset : int, optional
        Value to multiply each degree centrality by to account for small
        values. The default is 10000.
    color : str, optional
        Node color attribute. The default is "SysGamGen."
    edge_color : str, optional
        Edge color attribute. The default is "sub_color."

    Returns
    -------
    (matplotlib.pyplot.figure, matplotlib.pyplot.Axes)
        Figure/ax of plot.
    """

    # deg_cent = [dc * offset for dc in nx.degree_centrality(gamers).values()]
    deg_cent = np.fromiter(nx.degree_centrality(gamers).values(),
                           np.float64)
    return (*draw_gamers(gamers, color=color, edge_color=edge_color,
                         size=deg_cent*offset, **kwargs), deg_cent)


def draw_k_core_decompose(gamers, k_range=range(8, 16), color="SysGamGen",
                          edge_color="sub_color"):
    row = (int(len(k_range)/2)
           if ~(len(k_range) % 2) else 1 + int(len(k_range)/2))
    col = (int(len(k_range)/2)
           if len(k_range) != 2 else 2)

    # I want a large figure because this looks terrible if too small.
    fig, axes = plt.subplots(row, col, figsize=(16, 16))

    for ax, k in zip(axes.flat, k_range):
        decomposed = nx.k_core(gamers, k)

        # Ignoring return values since they're the same fig, ax I passed in.
        draw_gamers(decomposed, color=color, edge_color=edge_color,
                    fig=fig, ax=ax)

    return fig, axes


def draw_diameter_radius(lcc, cent_offset=3000, peri_offset=1000,
                         default_offset=100):
    """Draw the barycenter and periphery of the gamer network.

    Parameters
    ----------
    lcc : networkx.Graph
        Largest connected component of the gamers network projection.
    cent_offset : int
        Size offset for center nodes.
    peri_offset : int
        Size offset for periphery nodes.
    default_offset : int
        Size offset for all other nodes.

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
    size = [cent_offset if node in center
            else peri_offset if node in periphery
            else default_offset
            for node in lcc.nodes()]

    # Plot and return (fig, ax)
    return draw_gamers(lcc, color="CentPeri", edge_color="sub_color",
                       size=size)
