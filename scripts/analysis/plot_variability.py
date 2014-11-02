from __future__ import division

import numpy as np
from scipy import interpolate
import matplotlib.pyplot as plt

from neurotrends.config import mongo, DATES
from neurotrends.model.utils import verified_mongo
from neurotrends.analysis import pipeline
from neurotrends.analysis.plot.utils import file_name

SPLINE_SMOOTHNESS = 2

query = {
    'date': {'$ne': None}
}
query.update(verified_mongo)
articles = mongo['article'].find(query)

count, count_year, total_year = pipeline.count_pipelines(articles)

def plot_pipelines(dates, pipelines, totals=None, title=None, xlabel=None,
                   ylabel=None, outname=None):
    """Plot variability in pipelines over time.

    :param list dates: Years to plot
    :param dict pipelines: Pipeline counts; see `count_pipelines`
    :param dict totals: Total article count per year; if provided, normalize
        pipeline counts by totals
    :param str title: Plot title
    :param str xlabel: Plot x-label
    :param str ylabel: Plot y-label
    :param str outname: Output file name; file saved if provided

    """
    if totals:
        counts = [
            len(pipelines[date]) / totals[date]
            for date in dates
        ]
    else:
        counts = [
            len(pipelines[date])
            for date in dates
        ]
    fit = interpolate.splrep(dates, counts, s=SPLINE_SMOOTHNESS)

    x_interp = np.arange(
        dates[0] - 0.1,
        dates[-1] + 0.2,
        0.1,
    )

    plt.figure()

    plt.plot(
        dates, counts, 'o',
        x_interp, interpolate.splev(x_interp, fit), '-',
    )

    ax = plt.gca()

    ax.set_xlim((dates[0] - 1, dates[-1] + 1))

    if title:
        ax.set_title(title)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)

    if outname:
        plt.savefig(outname + '.pdf', bbox_inches='tight')

    plt.close()

for group in pipeline.variance_groups:

    plot_pipelines(
        DATES, count_year[group], ylabel='Count',
        outname=file_name(['count-{0}'.format(group)], path='pipelines')
    )

    plot_pipelines(
        DATES, count_year[group], totals=total_year, ylabel='Proportion',
        outname=file_name(['prop-{0}'.format(group)], path='pipelines')
    )
