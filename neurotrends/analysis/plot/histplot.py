"""

"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def unwind(summary):
    """
    
    """
    values = []

    for key, ids in summary.iteritems():
        if key.date is None and key.version is None:
            values.extend([key.value] * len(ids))

    return values


def hist(summary, bins=10, xlog=False, xlabel=None, outname=None):

    plt.figure()

    values = unwind(summary)

    # Adapted from bit.ly/1cvAsSb
    if xlog:
        # TODO: Handle this in taggers
        values = [v for v in values if v]
        bins = np.logspace(
            np.log10(min(values)),
            np.log10(max(values))
        )
    else:
        bins = bins

    plt.hist(values, bins=bins)

    ax = plt.gca()

    if xlog:
        ax.set_xscale('log')

    # Add y-label
    if xlabel:
        ax.set_xlabel(xlabel)

    if outname:
        plt.savefig(outname + '.pdf', bbox_inches='tight')
