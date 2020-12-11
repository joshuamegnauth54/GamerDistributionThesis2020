import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

from matplotlib.patches import Patch


def draw_gamers(gamers, algo="sfdp", color="sub_color", edge_color="#f8f8f2",
                size=32, fig=None, ax=None, **kwargs):
    pos = nx.nx_pydot.graphviz_layout(gamers, prog=algo)
    if fig is None and ax is None:
        fig, ax = plt.subplots(figsize=(22, 22))
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
                          edge_color="sub_color", **kwargs):
    row = (int(len(k_range)/2)
           if ~(len(k_range) % 2) else 1 + int(len(k_range)/2))
    col = (int(len(k_range)/2)
           if len(k_range) != 2 else 2)

    # I want a large figure because this looks terrible if too small.
    fig, axes = plt.subplots(row, col, figsize=(22, 22))

    for ax, k in zip(axes.flat, k_range):
        decomposed = nx.k_core(gamers, k)

        # Ignoring return values since they're the same fig, ax I passed in.
        draw_gamers(decomposed, color=color, edge_color=edge_color,
                    fig=fig, ax=ax, **kwargs)

    return fig, axes


def draw_diameter_radius(lcc, cent_offset=4096, peri_offset=1024,
                         default_offset=32):
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


def draw_lollypop(counts_df, suptitle):
    fig, ax = plt.subplots(figsize=(20, 20))

    # Horizontal lines are the lollypop "sticks"
    ax.hlines(counts_df.index, xmin=0, xmax=counts_df, color="#8be9fd")
    # Dots are the lollypops themselves
    ax.plot(counts_df, counts_df.index, "o", color="#ff5555")

    # Labels and customization
    # The axis labels will likely be clear from the title.
    ax.set_xlabel("")
    ax.set_ylabel("")
    # X axis helps with distinguishing points. Y does not.
    ax.grid(axis='x', color="#44475a")
    ax.set_axisbelow(True)
    ax.set_frame_on(False)
    ax.patch.set_facecolor("#282a36")
    ax.tick_params(colors="#8be9fd", labelsize=16)

    # Figure stuff
    fig.suptitle(suptitle,
                 fontsize=32,
                 color="#f8f8f2",
                 fontweight="bold",
                 y=1.01)
    fig.patch.set_facecolor("#282a36")
    fig.tight_layout()

    return fig, ax


def add_network_leg(fig, ax, title, col_labels, loc="upper left"):
    """ Convenience function to add a legend and title to the network plots.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure associated with ax.
    ax : matplotlib.axes._subplots.AxesSubplot
        Axes associated with fig.
    title : str
        Title to set for ax.
    col_labels : (str, str)
        Tuple of (color, label) for each legend item.
    loc : str, optional
        Location of the legend. Check matplotlib's docs.
        The default is "upper left".

    Returns
    -------
    None.

    """

    # The frame looks nice for subplots but yucky and weird with the title.
    ax.set_frame_on(False)
    ax.set_title(title,
                 fontdict={"fontsize": 24,
                           "color": "#f8f8f2",
                           "fontweight": "bold"})
    # Manual legend creation
    # Patches are used to represent each color present
    handles = []
    for pair in col_labels:
        patch = Patch(color=pair[0])
        patch.set_label(pair[1])
        handles.append(patch)

    # Upper left is a good default for the legend
    ax.legend(handles=handles,
              loc=loc,
              fontsize=14,
              facecolor="#282a36",
              edgecolor="#44475a",
              frameon=False)

    # Manually setting the font color for the legend as the default is too
    # dark
    legend = ax.get_legend()
    for lab in legend.get_texts():
        lab.set_color("#f8f8f2")
