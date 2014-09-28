# -*- coding: utf-8 -*-

category = 'tool'

import os

from neurotrends.config import re
from neurotrends.tagger import Looks, RexTagger, RexComboVersionTagger
from neurotrends.pattern.misc import delimiter, version_separator
from neurotrends import trendpath

from .matlab_utils import get_versions, get_version_regexes

python = RexTagger(
    'python', [r'python']
)

java = RexTagger(
    'java',
    [
        r'java(?!{dlm}script)'.format(dlm=delimiter),
    ]
)

rlang = RexTagger(
    'rlang',
    [
        r'\Wr{dlm}project'.format(dlm=delimiter),
        r'\Wr{dlm}development{dlm}(core)?{dlm}team'.format(dlm=delimiter),
        r'''
            \Wr{dlm}foundation{dlm}for{dlm}statistical{dlm}computing
        '''.format(dlm=delimiter),
        r'''
            (software|programming){dlm}(language|environment){dlm}r(?!\w)
        '''.format(dlm=delimiter),
        r'''
            \Wr{dlm}(software|programming){dlm}(language|senvironment)
        '''.format(dlm=delimiter),
        r'\Wr{dlm}statistical'.format(dlm=delimiter),
        r'\Wr{dlm}software'.format(dlm=delimiter),
        r'\Wr{dlm}library'.format(dlm=delimiter),
    ]
)

idl = RexTagger(
    'idl',
    [
        r'\Widl\W',
        r'interactive{dlm}data{dlm}language'.format(dlm=delimiter),
    ]
)

fortran = RexTagger(
    'fortran', [r'fortran']
)

octave = RexTagger(
    'octave', [r'octave']
)

matlab_versions = get_versions()
matlab_regexes = get_version_regexes(matlab_versions)

matlab = RexComboVersionTagger(
    'matlab',
    [
        r'matlab',
    ],
    version_separator,
    # Only match against complete versions; e.g., don't confuse "matlab r14"
    # with "matlab r1"
    looks=Looks(negahead=r'''(
        \d
        |
        \.[1-9]
        |
        st|nd|rd|th
        |
        \s*(sp|service)
    )'''),
    versions=matlab_regexes,
)

