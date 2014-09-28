# -*- coding: utf-8 -*-

import functools

from neurotrends.config import re


delimiter = r'\s*'
float_ptn = u'[-+]?\d*\.?\d+'
mov_ptn = 'mo(tion|vement)'
cor_ptn = '(correct|adjust|compensate?)(ed|ing|ion|ment)?'

# MNI pattern
mni_ptn = '(mni|montreal{dlm}neurological{dlm}institute)'.format(dlm=delimiter)
mni_num_ptn = mni_ptn + delimiter + '\d*'

# Space pattern
spc_ptn = r'''
    (probabilistic)?{dlm}(brain)?{dlm}
        (space|atlas|template|co\-?ordinates?|standard|brain|image)
'''.format(dlm=delimiter)

version_separator = r'''
    (
        [{skip}]
        |
        \([^)]{{,150}}\)
        |
        software
        |
        v(ersion)?
        |
        library
    )*?
'''.format(
    skip=re.escape(',;:-(') + '\s'
)


def clean_unicode(text):
    """Replace unicode characters with similar ASCII characters.
    """
    return text.replace(
        u'\u2044', '/'
    ).replace(
        u'\u2212', '-'
    )


def clean_delimiters(text):
    return re.sub(r'[\s\-,]+', ' ', text)


def compose(*funcs):
    return functools.reduce(
        lambda f, g: lambda x: g(f(x)),
        funcs,
    )

clean = compose(clean_unicode, clean_delimiters)

