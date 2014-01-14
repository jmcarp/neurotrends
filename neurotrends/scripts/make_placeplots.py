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

places = [
    art['place']
    for art in mongo['article'].find(
        {},
        {'place': True}
    )
    if art['place']
]

place_counts = collections.Counter(places)


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

top_places = [
    place[0]
    for place in place_counts.most_common(10)
]

min_prop = 0.1

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

colors = get_colors(plot_frame.columns, PALETTE_NAME)

plot_frame = plot_frame.div(
    1.0 * plot_frame.sum(axis=1),
    axis=0,
)

plot_frame.plot(
    kind='barh', stacked=True,
    color=colors,
)

ax = plt.gca()

# Hack: Remove horizontal line at y=0 inserted by pandas
ax.lines.pop()

ax.invert_yaxis()
ax.set_xlabel('Proportion')

handles, labels = ax.get_legend_handles_labels()
lgd = ax.legend(
    handles, labels,
    loc='upper left', bbox_to_anchor=(1, 1)
)

plt.savefig(
    file_name(['pkg', 'stacked'], path='place') + '.pdf',
    bbox_inches='tight'
)
