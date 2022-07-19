import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import numpy.typing as npt

from typing import Optional
from collections.abc import Sequence, Iterable
from matplotlib.axes import Subplot
from matplotlib.figure import Figure


def p_value_plots(
    observed: Sequence[np.floating],
    replicates: Sequence[npt.NDArray[np.floating]],
    labels: Sequence[str],
    plot_obs: bool = True,
    plot_p: bool = True,
    figsize: tuple[int, int] = (20, 20),
    suptitle: Optional[str] = None,
) -> tuple[Figure, npt.NDArray[Subplot]]:
    """Plot observed values and replicates for one or more variables.

    Parameters
    ----------
    observed: Sequence[np.floating]
        Observed values.
    replicates: Sequence[npt.NDArray[np.floating]]
        Replicates calculated with the parameters that generated `observed`.
    plot_obs: bool
        Plot the observed values.
    plot_p: bool
        Calculate and plot p-values.
    figsize: tuple[int, int]
        Figure size.
    suptitle: Optional[str]
        Main title for plot.

    Returns
    -------
    tuple[Figure, npt.NDArray[Subplot]]
        Figure and associated subplots for the p-value plots.
    """

    # Replicates needs to be an array of arrays.
    # Observed and labels must be arrays.
    assert isinstance(observed, Iterable)
    assert isinstance(replicates, Iterable)
    assert all(map(lambda rep: isinstance(rep, Iterable), replicates))
    assert isinstance(labels, Sequence)
    assert len(observed) & len(replicates) & (len(observed) == len(replicates))

    # Equal rows and columns...mostly. We'll have an extra row if the length
    # is odd.
    # My process is really messy.
    row: int = (
        int(len(observed) / 2) if ~(len(observed) % 2) else 1 + int(len(observed) / 2)
    )
    col: int = int(len(observed) / 2) if len(observed) != 2 else 2

    fig: Figure
    axes: npt.NDArray[Subplot]
    fig, axes = plt.subplots(row, col, figsize=figsize)
    for ax, obs, reps, label in zip(axes.flat, observed, replicates, labels):
        ax.hist(reps, bins="fd", color="#bd93f9")

        # Add observed value line and p-value
        if plot_obs:
            ax.axvline(obs, color="#ff5555", antialiased=True)
        if plot_p:
            # P-values are the probability of obtaining results at least as
            # extreme as what was observed.
            # So sum(replicates >= observed)/len(replicates)
            # (which is just the mean as shown below).
            # The replicates were calculated via random graphs
            # so I THINK this is statistically sound.
            p_value: np.floating = np.mean(reps >= obs)

        # Labels and aesthetics
        ax.set_title(label, fontsize=22, fontweight="bold", color="#f8f8f2")
        ax.grid(axis="y", color="#8be9fd")
        ax.set_axisbelow(True)
        ax.set_frame_on(False)
        ax.patch.set_facecolor("#282a36")
        ax.tick_params(colors="#8be9fd", labelsize=16)

    # Figure misc. These are better to set after plotting.
    fig.patch.set_facecolor("#282a36")
    fig.tight_layout()
    fig.suptitle(
        suptitle
        if suptitle
        else "Random graph replicates of network measures{}".format(
            " + observed in red" if plot_obs else ""
        ),
        fontsize=36,
        fontweight="bold",
        color="#f8f8f2",
        y=1.05,
    )

    return fig, axes
