"""

"""

import collections
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from neurotrends.config import mongo
from neurotrends.analysis.plot.utils import file_name
from neurotrends.analysis.plot.utils import get_colors
from neurotrends import pattern

PALETTE_NAME = 'Set1'
MIN_PROP = 0.1


def crosstab(collection, xkey, xvals, ykey, yvals):
    """

    """
    data = []

    for xval in xvals:
        xrow = {}
        for yval in yvals:
            query = {
                xkey: xval,
                ykey: yval,
            }
            count = collection.find(query).count()
            xrow[yval] = count
        data.append(xrow)

    return data

def plot_tags_by_place(frame, stacked, outname=None):
    """

    """
    # Get colors
    colors = get_colors(frame.columns, PALETTE_NAME)

    # Draw initial plot
    frame.plot(
        kind='barh', stacked=stacked,
        color=colors,
    )
    ax = plt.gca()

    # Hack: Remove horizontal line at y=0 inserted by pandas
    ax.lines.pop()

    # Adjust axes
    ax.invert_yaxis()
    ax.set_xlabel('Proportion')

    # Draw legend
    handles, labels = ax.get_legend_handles_labels()
    lgd = ax.legend(
        handles, labels,
        loc='upper left', bbox_to_anchor=(1, 1)
    )
    lgd.get_frame().set_facecolor('none')

    # Save figure
    if outname:
        plt.savefig(outname + '.pdf', bbox_inches='tight')

# TODO: Split into smaller functions
def plot_places(min_prop=MIN_PROP):

    place_counts = collections.Counter([
        art['place']
        for art in mongo['article'].find(
            {},
            {'place': True}
        )
        if art['place']
    ])

    top_places = [
        place[0]
        for place in place_counts.most_common(10)
    ]

    data = crosstab(
        mongo['article'],
        'place',
        top_places,
        'tags.label',
        pattern.tag_groups['pkg'].labels
    )

    frame = pd.DataFrame(
        data,
        index=top_places,
        columns=pattern.tag_groups['pkg'].labels,
    )

    min_count = min_prop * frame.sum().sum()

    sum0 = frame.sum()
    plot_frame = frame.ix[:, sum0 >= min_count]
    plot_frame['other'] = frame.ix[:, sum0 < min_count].sum(axis=1)

    plot_frame = plot_frame.div(
        1.0 * plot_frame.sum(axis=1),
        axis=0,
    )

    # Make plots
    plot_tags_by_place(
        plot_frame, stacked=True,
        outname=file_name(['pkg', 'stacked'], path='place')
    )
    plot_tags_by_place(
        plot_frame, stacked=False,
        outname=file_name(['pkg', 'adjacent'], path='place')
    )

plot_places()