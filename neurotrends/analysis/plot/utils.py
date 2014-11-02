#!/usr/bin/env python
# encoding: utf-8

import os
import seaborn as sns

from neurotrends import trendpath
from neurotrends.util import mkdir_p


def file_name(parts, dlm='-', path=None, ext=''):
    """Build file name, ensuring directory exists.

    :param list parts: File name parts
    :param str dlm: Delimiter between parts
    :param str path: Optional path to append
    :param str ext: Optional file extension
    :return str: Path to file
    """
    base = trendpath.fig_dir
    if path:
        base = os.path.join(base, path)
    mkdir_p(base)
    return os.path.join(
        base,
        dlm.join(parts)
    ) + ext


reserved_labels = {
    'other': (0.8,) * 3,
    'none': (0.6,) * 3,
}


def get_colors(labels, palette_name):
    """Get color options for a list of labels.

    :param list labels: List of variable labels
    :param str palette_name: Name of color palette (e.g. 'husl', 'Set1')
    :return list: List of RGB tuples
    """
    color_labels = [
        label
        for label in labels
        if label not in reserved_labels
    ]
    palette = sns.color_palette(palette_name, len(color_labels))

    colors = []
    for label in labels:
        if label in reserved_labels:
            colors.append(reserved_labels[label])
        else:
            colors.append(palette.pop(0))

    return colors
