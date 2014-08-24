# -*- coding: utf-8 -*-

import pytest

from neurotrends.pattern.mag.mag import ge, ge_context, varian
from neurotrends.pattern.mag.est_field_strength import field_strength

from . import check_taggers


@pytest.mark.parametrize('input, expected', [
    # Positives
    ('field strength of 3.0 tesla', {'value': 3.0}),
    ('field strength of 3.0 T', {'value': 3.0}),
    # Negatives
    ('field strength of 3.0 Tinkerbells', None),
    ('field strength of 100 tesla', None),
])
def test_field_strength(input, expected):
    check_taggers([field_strength], input, expected)


@pytest.mark.parametrize('input, expected', [
    # Positives
    ('general electric', {}),
    ('GE scanner', {}),
    # Negatives
    ('GE Hoffman', None),
])
def test_ge(input, expected):
    check_taggers([ge, ge_context], input, expected)


@pytest.mark.parametrize('input, expected', [
    # Positives
    ('varian scanner', {}),
    # Negatives
    ('analysis of variance', None),
])
def test_varian(input, expected):
    check_taggers([varian], input, expected)

