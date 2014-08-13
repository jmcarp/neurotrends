"""

"""

import unittest
from nose.tools import *

import os
import seaborn as sns

from neurotrends import trendpath
from neurotrends.analysis.plot import utils

class TestFileName(unittest.TestCase):

    def test_defaults(self):
        assert_equal(
            utils.file_name(['foo', 'bar']),
            os.path.join(trendpath.fig_dir, 'foo-bar')
        )

    def test_delim(self):
        assert_equal(
            utils.file_name(['foo', 'bar'], dlm='_'),
            os.path.join(trendpath.fig_dir, 'foo_bar')
        )

    def test_path(self):
        assert_equal(
            utils.file_name(['foo', 'bar'], path='bob'),
            os.path.join(trendpath.fig_dir, 'bob', 'foo-bar')
        )


class TestGetColors(unittest.TestCase):

    def test_no_reserved(self):
        assert_equal(
            utils.get_colors(['foo', 'bar', 'baz'], 'husl'),
            sns.color_palette('husl', n_colors=3)
        )

    def test_reserved(self):
        colors = utils.get_colors(['foo', 'other', 'bar', 'baz'], 'husl')
        sns_colors = sns.color_palette('husl', n_colors=3)
        sns_colors.insert(1, utils.reserved_labels['other'])
        assert_equal(
            colors,
            sns_colors
        )
