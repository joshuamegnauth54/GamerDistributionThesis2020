import networkx as nx
import numpy as np
import numpy.typing as npt
import pandas as pd
import matplotlib.pyplot as plt
import logging

from matplotlib.patches import Patch
from matplotlib.figure import Figure
from matplotlib.axes import Axes, Subplot
from matplotlib.legend import Legend
from networkx.classes.graph import Graph
from typing import Optional
from collections.abc import Sequence, Iterable


def draw_gamers(
    gamers: Graph,
    algo: str = "sfdp",
    color: str = "sub_color",
    edge_color: str = "#f8f8f2",
    size: int | npt.NDArray[np.number] | Sequence[int] = 32,
    fig: Optional[Figure] = None,
    ax: Optional[Axes] = None,
    **kwargs: str | int | float,
) -> tuple[Figure, Axes]:
    """Plot the gamers graph while handling aesthetics.

    This function wraps up boilerplot such as pulling out node and edge
    attributes and keeping the color scheme intact.

    Parameters
    ----------
    gamers: networkx.classes.graph.Graph
        Preprocessed graph of the gamers network data.
    algo: str
        Network drawing algorithm to pass to GraphViz. Must be one of: dot,
        twopi, fdp, sfdp, circo. Defaults to sfdp.
    color: str
        Name of attribute to use for node colors. For example, sub_color will
        retrieve the colors defined by the sub_color attribute.
    edge_color: str
        Color or attribute to use for edge colors.
    size: numpy.typing.NDArray[np.Number] | Sequence[int]
        Size of each plotted node.
    fig: Optional[Figure]
        Plot on this figure. Axes must be provided too.
    ax: Optional[Axes]
        Plot on this Axes. Figure must be provided too.
    **kwargs: str | int | float
        Keyword arguments to pass down to draw_networkx.
    """
    logging.info(
        f"DRAW: Gamers network with the {algo} algorithm, {color} node colors, and {edge_color} edge color."
    )

    # Use GraphViz to calculate node and edge positions rather than the slower
    # NetworkX implementations
    pos: dict[int, tuple[float, float]] = nx.nx_pydot.pydot_layout(gamers, prog=algo)

    # Create a base Figure and Axes if not provided
    if not fig and not ax:
        fig, ax = plt.subplots(figsize=(22, 22))
    elif bool(fig) ^ bool(ax):
        # Raise an error if only one of fig or ax is provided instead of both
        raise ValueError("Either BOTH or NEITHER of fig and ax must be present")

    # Hi mypy. Can you see that fig and ax are not None?
    assert fig is not None
    assert ax is not None

    # Draw network based on calculated positions
    # Text labels are disabled because there are too many nodes
    nx.draw_networkx(
        gamers,
        pos,
        with_labels=False,
        ax=ax,
        node_size=size,
        node_color=list(nx.get_node_attributes(gamers, color).values())
        if color[0] != "#"
        else color,
        # alpha=0.75,
        edge_color=list(nx.get_node_attributes(gamers, edge_color).values())
        if edge_color[0] != "#"
        else edge_color,
        label=color,
        **kwargs,
    )
    fig.tight_layout()

    # Dracula colors for background
    fig.patch.set_facecolor("#282a36")
    ax.patch.set_facecolor("#282a36")
    return fig, ax


def draw_degree_centrality(
    gamers: Graph,
    offset: int = 10000,
    color: str = "SysGamGen",
    edge_color: str = "sub_color",
    **kwargs,
) -> tuple[Figure, Axes, npt.NDArray[np.floating]]:
    """Plot gamers with node sizes determined by degree centrality * offset.

    Parameters
    ----------
    gamers: networkx.Graph
        Graph to plot.
    offset: int, optional
        Value to multiply each degree centrality by to account for small
        values. The default is 10000.
    color: str, optional
        Node color attribute. The default is "SysGamGen."
    edge_color: str, optional
        Edge color attribute. The default is "sub_color."
    **kwargs: str | float | int
        Keyword arguments to pass down to draw_gamers.

    Returns
    -------
    tuple(
        matplotlib.figure.Figure,
        matplotlib.axes.Axes,
        numpy.typing.NDArray[np.floating]
    )
        Figure/ax of plot and degree centrality.
    """
    logging.info(f"DRAW: Degree centrality with {color} and {edge_color} as attributes")

    # deg_cent = [dc * offset for dc in nx.degree_centrality(gamers).values()]
    # nx.degree_centrality returns a dictionary of {node, centrality}, so
    # I need dict.values() for the centralities
    deg_cent: npt.NDArray[np.floating] = np.fromiter(
        nx.degree_centrality(gamers).values(), np.float64
    )
    return (
        *draw_gamers(
            gamers, color=color, edge_color=edge_color, size=deg_cent * offset, **kwargs
        ),
        deg_cent,
    )


def draw_k_core_decompose(
    gamers: Graph,
    k_range: range = range(8, 16),
    color: str = "SysGamGen",
    edge_color: str | Iterable[str] = "sub_color",
    **kwargs,
) -> tuple[Figure, npt.NDArray[Subplot]]:
    """Draw the k core of gamers through k_range.

    Parameters
    ----------
    gamers: networkx.Graph
        Graph to plot.
    k_range: range, optional
        Range of k to plot. The default is range(8, 16).
    color: str, optional
        Color attribute of gamers or hex color. The default is "SysGamGen".
    edge_color: str | Iterable[str], optional
        Color attribute of gamers or hex color or list of either. If a list is
        passed then the length must match k as each k will be associated with
        a list element.
        The default is "sub_color".
    **kwargs: str | int | float
        Keyword arguments to pass down the stack to draw_gamers.

    Returns
    -------
    fig: matplotlib.figure.Figure
        Figure for k-core plots.
    axes: numpy.typing.NDArray[matplotlib.axes.Subplot]
        Subplots of each k-core plot.
    """
    logging.info("DRAW: k-core decomposition")

    # Row/col thingy is broken.
    row: int = (
        int(len(k_range) / 2) if ~(len(k_range) % 2) else 1 + int(len(k_range) / 2)
    )
    col: int = int(len(k_range) / 2) if len(k_range) != 2 else 2

    # I want a large figure because this looks terrible if too small.
    fig: Figure
    axes: npt.NDArray[Subplot]
    fig, axes = plt.subplots(row, col, figsize=(22, 22))

    if isinstance(edge_color, str):
        edge_color = np.repeat(edge_color, len(k_range))

    for ax, k, ecolor in zip(axes.flat, k_range, edge_color):
        decomposed: Graph = nx.k_core(gamers, k)

        # Ignoring return values since they're the same fig, ax I passed in.
        draw_gamers(
            decomposed, color=color, edge_color=ecolor, fig=fig, ax=ax, **kwargs
        )

    return fig, axes


def draw_diameter_radius(
    lcc: Graph,
    cent_offset: int = 2048,
    peri_offset: int = 1024,
    default_offset: int = 128,
    edge_color: str = "sub_color",
    barycenter: bool = True,
) -> tuple[Figure, Axes]:
    """Draw the barycenter and periphery of the gamer network.

    Parameters
    ----------
    lcc: networkx.Graph
        Largest connected component of the gamers network projection.
    cent_offset: int, optional
        Size offset for center nodes. Default is 2048.
    peri_offset: int, optional
        Size offset for periphery nodes. Default is 1024.
    default_offset: int, optional
        Size offset for all other nodes. Default is 128.
    edge_color: str, optional
        Attribute containing edge color or the color itself. Default is
        sub_color.
    barycenter: boolean, optional
        Whether to use the barycenter algorithm for radius or the default
        algo. Default is True.

    Returns
    -------
    tuple[matplotlib.figure.Figure, matplotlib.axes.Axes]
        Figure/ax of plot.
    """
    logging.info("DRAW: Center and periphery")

    # Avoid recalculating eccentricity. We'll need an eccentricity dictionary
    # at least once.
    logging.info("Calculating eccentricity.")
    lcc_ecc: dict[int, int] = nx.eccentricity(lcc)

    if barycenter:
        # Barycenter centrality is normalized by accounting for the total
        # network.
        logging.info("Calculating barycenter")
        center: list[int] = nx.barycenter(lcc, weight="weight")
    else:
        logging.info("Calculating center")
        center = nx.center(lcc, lcc_ecc)
    logging.info("Calculating periphery")
    periphery: list[int] = nx.periphery(lcc, lcc_ecc)

    # Nodes outside of the radius/diameter are green. The center is red and
    # the periphery is yellow.
    nx.set_node_attributes(
        lcc,
        {
            node: "#ff5555"
            if node in center
            else "#f1fa8c"
            if node in periphery
            else "#8be9fd"
            for node in lcc.nodes()
        },
        "CentPeri",
    )

    # Figuring out a decent size is extraordinarily difficult.
    # I'd like for both center nodes as well as periphery nodes to stand out.
    size: list[int] = [
        cent_offset
        if node in center
        else peri_offset
        if node in periphery
        else default_offset
        for node in lcc.nodes()
    ]

    # Plot and return (fig, ax)
    return draw_gamers(
        lcc, color="CentPeri", edge_color=edge_color, size=size, alpha=0.6
    )


def draw_lollypop(counts_df: pd.Series, suptitle: str) -> tuple[Figure, Subplot]:
    """Draw a lollypop plot of counts_df.

    Parameters
    ----------
    counts_df: pandas.Series
        Series where index is the names and the values are something we'd want
        to turn into a lollypop.
    suptitle: str
        Suptitle of plot.

    Returns
    -------
    fig: matplotlib.figure.Figure
        Figure associated with ax.
    ax: matplotlib.axes.Subplot
        Axes associated with fig.
    """
    logging.info("DRAW: lollypop plot")

    fig: Figure
    ax: Subplot
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
    ax.grid(axis="x", color="#44475a")
    ax.set_axisbelow(True)
    ax.set_frame_on(False)
    ax.patch.set_facecolor("#282a36")
    ax.tick_params(colors="#8be9fd", labelsize=16)

    # Figure stuff
    fig.suptitle(suptitle, fontsize=32, color="#f8f8f2", fontweight="bold", y=1.01)
    fig.patch.set_facecolor("#282a36")
    fig.tight_layout()

    return fig, ax


def add_network_leg(
    fig: Figure,
    ax: Subplot,
    title: Optional[str] = None,
    suptitle: Optional[str] = None,
    col_labels: Optional[Sequence[tuple[str, str]]] = None,
    loc: str = "upper left",
    legend: bool = True,
) -> None:
    """Convenience function to add a legend and title to the network plots.

    Parameters
    ----------
    fig: matplotlib.figure.Figure
        Figure associated with ax.
    ax: matplotlib.axes.AxesSubplot
        Axes associated with fig.
    title: Optional[str]
        Title to set for ax.
    suptitle: Optional[str]
        Title to set for figure.
    col_labels: Optional[Sequence[tuple[str, str]]]
        Tuple of (color, label) for each legend item. Required for legend.
    loc: str, optional
        Location of the legend. Check matplotlib's docs.
        The default is "upper left".
    legend: bool, optional
        Add a legend. Requires col_labels.

    Returns
    -------
    None.
    """
    # The frame looks nice for subplots but yucky and weird with the title.
    ax.set_frame_on(False)

    if suptitle:
        fig.suptitle(suptitle, fontsize=32, color="#f8f8f2", fontweight="bold")

    if title:
        ax.set_title(
            title, fontdict={"fontsize": 24, "color": "#f8f8f2", "fontweight": "bold"}
        )

    if legend and col_labels is not None:
        # Manual legend creation
        # Patches are used to represent each color present
        handles: list[Patch] = []
        for pair in col_labels:
            patch: Patch = Patch(color=pair[0])
            patch.set_label(pair[1])
            handles.append(patch)

        # Upper left is a good default for the legend
        net_leg: Legend = ax.legend(
            handles=handles,
            loc=loc,
            fontsize=14,
            facecolor="#282a36",
            edgecolor="#44475a",
            frameon=False,
        )

        # Manually setting the font color for the legend as the default is too
        # dark
        # legend = ax.get_legend()
        for lab in net_leg.get_texts():
            lab.set_color("#f8f8f2")
