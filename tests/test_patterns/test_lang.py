# -*- coding: utf-8 -*-

import pytest

from neurotrends.pattern.lang import taggers

from . import check_taggers


@pytest.mark.parametrize('input, expected', [
    ('matlab', {}),
    ('matlab 2012a', {'version': '7.14'}),
    ('matlab r14sp1', {'version': '7.0.1'}),
    ('matlab r 14 service pack 1', {'version': '7.0.1'}),
])
def test_matlab(input, expected):
    check_taggers([taggers.matlab], input, expected)

