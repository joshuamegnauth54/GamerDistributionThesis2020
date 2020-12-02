import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

from collections.abc import Iterable

def p_value_plots(observed, replicates, labels, figsize=(20, 16)):

    # Replicates needs to be an array of arrays.
    # Observed and labels must be arrays.
    assert(isinstance(observed, Iterable))
    assert(isinstance(replicates, Iterable))
    assert(isinstance(replicates[0], Iterable))
    assert(isinstance(labels, Iterable))

    # P-values are the probability of obtaining results at least as extreme
    # as what was observed. So sum(replicates >= observed)/len(replicates)
    # (which is just the mean as shown below).
    # The replicates were calculated via random graphs so I THINK this is
    # statistically sound.
    p_values = (np.mean(sim_pair[1] >= sim_pair[0])
                for sim_pair in zip(observed, replicates))

    # Equal rows and columns...mostly. We'll have an extra row if the length
    # is odd.
    row = int(len(observed)/2) if ~(len(observed) % 2)\
        else 1 + int(len(observed)/2)
    col = int(len(observed)/2)

    fig, axes = plt.subplots(row, col, figsize=figsize)
    for ax, obs, reps, label in zip(axes.flat, observed, replicates, labels):
        ax.hist(replicates, bins="fd", color="#bd93f9")
        ax.axvline(observed, color="#ff5555")

    return fig, ax