"""

"""
import os
import subprocess

import pandas as pd
from vincent import StackedBar, ValueRef, PropertySet, AxisProperties
from vincent.legends import Legend, LegendProperties

import analyze
from neurotrends import trendpath, pattern

class PlotError(Exception): pass

def save_plot(plot, outjson, outimg=None):
    """Save plot to JSON and optionally to image.

    :param plot: Plot to be saved
    :param outjson: Path to JSON output file
    :param outimg: Path to image output file; must have .svg or .png extension

    """
    # Save JSON
    plot.to_json(outjson)

    # Convert JSON to image
    if outimg is not None:
        outfmt = outimg.split('.')[-1]
        if outfmt == 'svg':
            cmd = 'vg2svg'
        elif outfmt == 'png':
            cmd = 'vg2png'
        else:
            raise PlotError('Format must be "svg" or "png"')
    subprocess.call([cmd, outjson, outimg])


def plot_values(values, labels, show=False, outjson=None, outimg=None):
    """Plot overall values (counts or proportions).

    """
    pass

def plot_values_by_year(values, dates, labels, show=False, outjson=None, outimg=None):
    """Plot values (counts or proportions) by year.

    """
    # Build data frame
    df = pd.DataFrame(values, index=dates, columns=labels)

    # Build Vincent plot
    plot = StackedBar(df, height=600, width=600)

    # Configure colors
    plot.colors(brew='Set1')

    # Configure legends
    plot.legends.append(Legend(values=labels[::-1], fill='color'))
    plot.legends[0].properties = LegendProperties(
        size=ValueRef(value=18)
    )

    # Configure axes
    plot.axes[0].properties = AxisProperties(labels=PropertySet(
        angle=ValueRef(value=-45),
        dx=ValueRef(value=-20),
        font_size=ValueRef(value=18)
    ))
    plot.scales['y'].domain = [0, 1]

    # Optionally display
    if show:
        plot.display()

    # Optionally save
    save_plot(plot, outjson, outimg)

    return plot


def plot_one_value_by_year():
    """Plot one value (count or proportion) by year.

    """
    pass


def plot_any_value_by_year(values, dates, show=True, outjson=None, outimg=None):
    """

    """
    # Build data frame
    df = pd.DataFrame(values, index=dates)

    # Build Vincent plot
    plot = StackedBar(df, height=600, width=600)

    # Configure axes
    plot.scales['y'].domain = [0, 1]

    # Optionally display
    if show:
        plot.display()

    # Optionally save
    save_plot(plot, outjson=outjson, outimg=outimg)

    return plot

def file_name(parts, fmt, dlm='-'):
    return os.path.join(
        trendpath.fig_dir,
        '{}.{}'.format(
            dlm.join(parts),
            fmt,
        )
    )

def plots(name, summary, labels):

    counts = tabulate.plot_tag_groups(summary, labels)


def plot_tag_group(summary, tag_group):

    counts = {}

    for label in tag_group.labels:
        #result = database['mr_all'].find_one({'_id': {'label': label}})
        #counts[label] = result['value'] if result else 0.0
        counts[label] = float(len(summary.get((label,), [])))
    return counts


def plots_by_year(name, summary, labels, dates, include_none, min_prop):

    # Analyze summary data
    counts, any_counts, dates, date_counts, labels = analyze.plot_tag_group_year(
        summary, labels, dates, include_none=include_none, min_prop=min_prop,
    )

    # Normalize counts
    values = analyze.norm_counts(counts)
    any_values = analyze.norm_any_counts(counts, date_counts)

    parts = [name, 'year']
    plot_values_by_year(counts, dates, labels, outjson=file_name(parts, 'json'), outimg=file_name(parts, 'svg'))
    parts.append('norm')
    plot_values_by_year(values, dates, labels, outjson=file_name(parts, 'json'), outimg=file_name(parts, 'svg'))

    parts = [name, 'year', 'any']
    plot_any_value_by_year(any_counts, dates, outjson=file_name(parts, 'json'), outimg=file_name(parts, 'svg'))
    parts.append('norm')
    plot_any_value_by_year(any_values, dates, outjson=file_name(parts, 'json'), outimg=file_name(parts, 'svg'))
