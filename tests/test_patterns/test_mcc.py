# -*- coding: utf-8 -*-

import pytest

from neurotrends.pattern.mcc import monte, monte_context

from . import check_taggers


@pytest.mark.parametrize('input, expected', [
    # Positives
    ('alpha sim', {}),
    ('monte carlo correction', {}),
    ('clustsim', {}),
    ('3dclustsim', {}),
    # From PMID 23178958
    ('This extent threshold was computed using a Monte Carlo simulation', {}),
    # From PMID 19158105
    ('In a Monte Carlo simulation within the AFNI software package', {}),
    # Negatives
    ('monte carlo simulation', None)
])
def test_mcc(input, expected):
    check_taggers([monte, monte_context], input, expected)

