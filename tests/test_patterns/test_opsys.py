# -*- coding: utf-8 -*-

import pytest

from neurotrends.pattern import opsys

from . import check_taggers


@pytest.mark.parametrize('input, expected', [
    # Positives
    ('windows xp', {}),
    ('windows operating system', {}),
    # Negatives
    ('time windows', None),
    # Shouldn't match "nt" within another word
    ('windows untested', None),
])
def test_windows(input, expected):
    check_taggers([opsys.windows_context], input, expected)

