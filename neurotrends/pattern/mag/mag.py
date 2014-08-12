# -*- coding: utf-8 -*-

from neurotrends.config import re
from neurotrends.tagger import RexTagger, MultiRexTagger
from ..misc import delimiter

ge = RexTagger(
    'ge',
    [
        r'general{dlm}electric'.format(dlm=delimiter),
    ]
)

# Use MultiRexTagger for GE to disambiguate names: e.g. GE Smith
ge_context = MultiRexTagger(
    'ge',
    [
        re.compile(r'\bGE\b'),
    ],
    [
        r'mri',
        r'scan',
        r'tesla',
    ]
)

siemens = RexTagger(
    'siemens',
    [r'siemens']
)

philips = RexTagger(
    'philips',
    [r'philips']
)

bruker = RexTagger(
    'bruker',
    [r'bruker']
)

varian = RexTagger(
    'varian',
    [r'varian\W']
)
shimazdu = RexTagger(
    'shimadzu',
    [r'shimazdu']
)

marconi = RexTagger(
    'marconi',
    [r'marconi']
)

