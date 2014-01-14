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
