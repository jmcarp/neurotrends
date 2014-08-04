"""

"""

import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns

from neurotrends.analysis import tabulate
from .utils import file_name, get_colors

MIN_PROP = 0.01
PALETTE_NAME = 'husl'

mpl.rcParams['legend.handlelength'] = 0.7

mpl_opts = {
    'figsize': [6, 6],
}


def plot_values(values, labels, ylabel=None, outname=None,
                label_formatter=None, **opts):
    """Plot overall values (counts or proportions).

    """
    series = pd.Series(values, index=labels)
    if labels and label_formatter:
        series.index = [
            label_formatter(label)
            for label in labels
        ]

    colors = get_colors(labels, PALETTE_NAME)

    opts.update(mpl_opts)
    ax = series.plot(kind='bar', color=colors, legend=False, **opts)

    #
    if ylabel:
        ax.set_ylabel(ylabel)

    # Rotate x-tick labels
    _, tick_labels = plt.xticks()
    plt.setp(tick_labels, rotation=45)

    # Hack: Remove horizontal line at y=0 inserted by pandas
    ax.lines.pop()

    # Optionally save
    if outname:
        plt.savefig(outname + '.pdf', bbox_inches='tight')
        plt.close()


def plot_values_by_year(values, dates, labels=None, ylabel=None,
                        label_formatter=None, outname=None, **opts):
    """Plot values (counts or proportions) by year.

    """
    # Build data frame
    df = pd.DataFrame(
        [
            values[date]
            for date in dates
        ],
        index=dates, columns=labels
    )
    if labels and label_formatter:
        df.columns = [
            label_formatter(label)
            for label in labels
        ]

    colors = get_colors(labels, PALETTE_NAME) if labels else None

    # Build plot
    opts.update(mpl_opts)
    ax = df.plot(
        kind='bar', stacked=True, legend=labels is not None, color=colors,
        **opts
    )

    #
    if ylabel:
        ax.set_ylabel(ylabel)

    # Hack: Remove horizontal line at y=0 inserted by pandas
    ax.lines.pop()

    # Add legend
    if labels is not None:
        handles, labels = ax.get_legend_handles_labels()
        lgd = ax.legend(
            handles[::-1], labels[::-1],
            loc='upper left', bbox_to_anchor=(1, 1)
        )
        lgd.get_frame().set_facecolor('none')

    # Optionally save
    if outname:
        kwargs = {}
        if labels is not None:
            kwargs['bbox_extra_artists'] = (lgd,)
        plt.savefig(outname + '.pdf', bbox_inches='tight', **kwargs)
        plt.close()


def plot_tag_by_year(values, dates, ylabel=None, outname=None, **opts):
    """Plot one value (count or proportion) by year.

    """

    df = pd.DataFrame(
        [
            values[date]
            for date in dates
        ],
        index=dates,
    )

    opts.update(mpl_opts)

    ax = df.plot(kind='bar', legend=False, **opts)

    if ylabel:
        ax.set_ylabel(ylabel)

    # Hack: Remove horizontal line at y=0 inserted by pandas
    ax.lines.pop()

    # Optionally save
    if outname:
        plt.savefig(outname + '.pdf', bbox_inches='tight')
        plt.close()


def tags_by_year(name, summary, label, dates):

    # Analyze summary data
    counts, _, _, date_counts, _ = tabulate.tag_group_year(
        summary, [label], dates,
    )
    values = tabulate.norm_counts(counts, date_counts)

    # Plot count using tag by date
    parts = [name, 'year']
    plot_tag_by_year(
        counts, dates, ylabel='Count',
        outname=file_name(parts, path='tag'),
    )

    # Plot proportion using tag by date
    parts.append('norm')
    plot_tag_by_year(
        values, dates, ylabel='Proportion',
        outname=file_name(parts, path='tag'),
    )


def groups_by_year(name, summary, labels, dates, min_prop=MIN_PROP, include_none=False,
                   none_mode='missing', sorted_labels=None, sort_key=None, label_formatter=None,
                   query=None):
    """

    """
    #
    counts, display_labels = tabulate.tag_group(
        summary, labels, sorted_labels=sorted_labels, sort_key=sort_key, min_prop=min_prop, query=query,
    )

    parts = [name, 'total']
    plot_values(
        counts, display_labels, outname=file_name(parts, path='tag'),
        ylabel='Count', label_formatter=label_formatter,
    )

    # Analyze summary data
    counts, any_counts, dates, date_counts, display_labels = tabulate.tag_group_year(
        summary, labels, dates, sorted_labels=sorted_labels, sort_key=sort_key, include_none=include_none, none_mode=none_mode, min_prop=min_prop, query=query,
    )

    # Normalize counts
    values = tabulate.norm_counts(counts)
    any_values = tabulate.norm_any_counts(any_counts, date_counts)

    # Plot count using tag by date
    parts = [name, 'year']
    plot_values_by_year(
        counts, dates, display_labels, ylabel='Count',
        label_formatter=label_formatter, outname=file_name(parts, path='group'),
    )

    # Plot proportion using tag by date
    parts.append('norm')
    plot_values_by_year(
        values, dates, display_labels, outname=file_name(parts, path='group'), ylim=(0,1),
        ylabel='Proportion', label_formatter=label_formatter,
    )

    # Plot proportion using any tag by date
    parts = [name, 'year', 'any', 'norm']
    plot_values_by_year(
        any_values, dates, ylabel='Proportion', outname=file_name(parts, path='group'),
        label_formatter=label_formatter,
    )
