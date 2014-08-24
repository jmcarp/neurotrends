# -*- coding: utf-8 -*-

import pytest

from neurotrends.model.utils import get_institution


@pytest.mark.parametrize('input, expected', [
    (
        'Department of Psychology, University of Michigan, Ann Arbor, MI, USA.',
        'University of Michigan',
    ),
    (
        'Imaging Research Center, University of Texas at Austin, Austin, TX '
            '78712. malecek@utexas.edu poldrack@utexas.edu www.poldracklab.org.',
        'University of Texas at Austin',
    ),
    (
        'University of Illinois at Urbana-Champaign, USA. Electronic address: '
            'mfabiani@illinois.edu.',
        'University of Illinois at Urbana-Champaign',
    ),
    (
        'Department of Psychology, University of Victoria, Victoria, '
            'British Columbia, V8W 3P5, Canada. holroyd@uvic.ca '
            'http://web.uvic.ca/~lccl/',
        'University of Victoria',
    ),
    (
        'Department of Pharmacology, Graduate Program University of Virginia '
            'School of Medicine, Charlottesville, Virginia, U.S.A',
        'University of Virginia',
    ),
])
def test_get_institution(input, expected):
    assert get_institution(input) == expected

