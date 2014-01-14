category = 'tool'

from neurotrends.config import re
from neurotrends.tagger import RexComboVersionTagger
from misc import version_separator

spss = RexComboVersionTagger(
    'spss',
    [
        r'\bSPSS\b',
        r'\bPASW\b',
    ],
    version_separator,
    flags=re.VERBOSE,
    arbitrary_rex=r'(?P<version>\d+(\.\d+){0,2})',
    post_proc=lambda v: re.sub(r'\.0?$', '', v),
)

statistica = RexComboVersionTagger(
    'statistica',
    [
        r'statistica\b(?!\s+l)(?!.{,50}?sinica)',
    ],
    version_separator,
    flags=re.VERBOSE,
    arbitrary_rex=r'(?P<version>\d+(\.\d+){,1})',
    post_proc=lambda v: re.sub(r'\.0?$', '', v),
)

sas = RexComboVersionTagger(
    'sas',
    [
        r'\bSAS\b',
    ],
    version_separator,
    flags=re.VERBOSE,
    arbitrary_rex=r'(?P<version>\d+(\.\d+){,1})',
    post_proc=lambda v: re.sub(r'\.0?$', '', v),
)

stata = RexComboVersionTagger(
    'stata',
    [
        r'\bSTATA\b',
    ],
    version_separator,
    flags=re.VERBOSE,
    arbitrary_rex=r'(?P<version>\d+(\.\d+){,1})',
    post_proc=lambda v: re.sub(r'\.0?$', '', v),
)

systat = RexComboVersionTagger(
    'systat',
    [
        r'\bsystat\b',
    ],
    version_separator,
    flags=re.VERBOSE,
    arbitrary_rex=r'(?P<version>\d+(\.\d+){,1})',
    post_proc=lambda v: re.sub(r'\.0?$', '', v),
)

sigmastat = RexComboVersionTagger(
    'sigmastat',
    [
        r'\bsigmastat\b',
    ],
    version_separator,
    flags=re.VERBOSE,
    arbitrary_rex=r'(?P<version>\d+(\.\d+){,1})',
    post_proc=lambda v: re.sub(r'\.0?$', '', v),
)
