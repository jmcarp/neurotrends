category = 'tool'

from neurotrends.config import re
from neurotrends.tagger import RexTagger, MultiRexTagger

from misc import delimiter

### Sequences ###

mprage = RexTagger(
    'mprage',
    [
        r'\Wmp{dlm}rage\W'.format(dlm=delimiter),
    ]
)

spgr = RexTagger(
    'spgr',
    [
        r'\Wspgr\W',
    ]
)

### Trajectories ###

epi = RexTagger(
    'epi',
    [
        r'echo{dlm}planar'.format(dlm=delimiter),
        re.compile(r'EPI'),
    ]
)

spiral = RexTagger(
    'spiral',
    [
        r'spiral{dlm}in'.format(dlm=delimiter),
        r'spiral{dlm}out'.format(dlm=delimiter),
    ]
)

spiral_context = MultiRexTagger(
    'spiral',
    [
        r'spiral',
    ],
    [
        r'mri',
        r'bold',
        r'imag',
        r'scan',
        r'data',
        r'pulse',
        r'acqui',
        r'sequence',
    ],
    separator='[^.,:;?]*'
)

### Sequences ###

gradient = RexTagger(
    'gradient',
    [
        r'gradient{dlm}echo'.format(dlm=delimiter),
        r'gradient{dlm}recall'.format(dlm=delimiter),
    ]
)

spin = RexTagger(
    'spin',
    [
        r'spin{dlm}echo'.format(dlm=delimiter),
    ]
)

grase = RexTagger(
    'grase',
    [
        re.compile(r'GRASE'),
    ]
)
### Acceleration methods ###

sense = RexTagger(
    'sense',
    [
        re.compile(r'SENSE'),
        r'sensitivity{dlm}encoded'.format(dlm=delimiter),
    ]
)

grappa = RexTagger(
    'grappa',
    [
        re.compile(r'GRAPPA'),
    ]
)

presto = RexTagger(
    'presto',
    [
        re.compile(r'PRESTO'),
    ]
)

smash = RexTagger(
    'smash',
    [
        re.compile(r'SMASH'),
    ]
)
