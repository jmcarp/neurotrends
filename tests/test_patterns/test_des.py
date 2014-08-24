# -*- coding: utf-8 -*-

import pytest

from neurotrends.pattern import des

from . import check_taggers


@pytest.mark.parametrize('input, expected', [
    # Positives
    ('block design', {}),
    ('blocked paradigm', {}),
    ('epoch based', {}),
    ('epoched analysis', {}),
    # PMID 21625502
    ('we used a blocked factorial design', {}),
])
def test_block(input, expected):
    check_taggers([des.block], input, expected)

