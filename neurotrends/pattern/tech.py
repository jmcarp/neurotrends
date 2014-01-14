category = 'analysis'

from neurotrends.config import re
from neurotrends.tagger import RexTagger, MultiRexTagger
from misc import delimiter

kda = RexTagger(
    'kda',
    [
        re.compile(r'\WKDA\W'),
    ]
)

kda_context = MultiRexTagger(
    'kda',
    [
        r'kernel{dlm}density{dlm}analysis'.format(dlm=delimiter),
    ],
    [
        r'multi{dlm}level'.format(dlm=delimiter),
    ],
    separator='[^.,:;?]*'
)

mkda = RexTagger(
    'mkda',
    [
        r'''
            multi{dlm}level{dlm}kernel{dlm}density{dlm}analysis
        '''.format(dlm=delimiter),
        r'multi{dlm}level{dlm}kda'.format(dlm=delimiter),
        r'\Wmkda\W',
    ]
)

ale = RexTagger(
    'ale',
    [
        r'activation{dlm}likelihood{dlm}analysis'.format(dlm=delimiter),
        r'ginger{dlm}ale'.format(dlm=delimiter),
    ]
)

loc = RexTagger(
    'localizer',
    [
        r'localizer',
    ]
)

conj = RexTagger(
    'conj',
    [
        r'conjunction{dlm}(analy|mask|map)'.format(dlm=delimiter),
        r'cognitive{dlm}conjunction'.format(dlm=delimiter),
        r'conjunction.{,25}contrast',
        r'conjunction.{,25}condition',
        r'conjunction.{,25}task',
    ]
)

roi = RexTagger(
    'roi',
    [
        r'regions?{dlm}of{dlm}interest'.format(dlm=delimiter),
        r'\Wrois?\W',
    ]
)

vox = RexTagger(
    'vox',
    [
        r'voxel{dlm}wise'.format(dlm=delimiter),
        r'whole{dlm}brain{dlm}analysis'.format(dlm=delimiter),
        r'whole{dlm}brain{dlm}contrast'.format(dlm=delimiter),
        r'whole{dlm}brain{dlm}statistic'.format(dlm=delimiter),
        r'whole{dlm}brain{dlm}comparison'.format(dlm=delimiter),
        r'whole{dlm}brain{dlm}correct'.format(dlm=delimiter),
    ]
)

ppi = RexTagger(
    'ppi',
    [
        r'psycho{dlm}physiologic(al)?{dlm}interaction'.format(dlm=delimiter),
        r'physio{dlm}physiologic(al)?{dlm}interaction'.format(dlm=delimiter),
        r'\Wppi\W',
    ]
)

betser = RexTagger(
    'betser',
    [
        r'beta{dlm}series'.format(dlm=delimiter),
    ]
)

dcm = RexTagger(
    'dcm',
    [
        r'dynamic{dlm}causal{dlm}model'.format(dlm=delimiter),
        r'\Wdcm\W',
    ]
)

grc = RexTagger(
    'grc',
    [
        r'granger{dlm}causal'.format(dlm=delimiter),
    ]
)

sem = RexTagger(
    'sem',
        [
        # Note: SEM conflicts with standard error of the mean
        r'structural{dlm}equation{dlm}model'.format(dlm=delimiter),
    ]
)

vbm = RexTagger(
    'vbm',
        [
        r'voxel{dlm}based{dlm}morphometry'.format(dlm=delimiter),
        re.compile(r'\WVBM\W'),
    ]
)

pca = RexTagger(
    'pca',
        [
        r'principal{dlm}components?{dlm}analysis'.format(dlm=delimiter),
        re.compile(r'\WPCA\W'),
    ]
)

ica = RexTagger(
    'ica',
        [
        r'independent{dlm}components?{dlm}analysis'.format(dlm=delimiter),
        re.compile(r'\WICA\W'),
    ]
)

pls = RexTagger(
    'pls',
        [
        'partial{dlm}least{dlm}squares'.format(dlm=delimiter),
        re.compile('\WPLS\W'),
    ]
)

mvpa = RexTagger(
    'mvpa',
    [
        r'multi{dlm}variate{dlm}pattern'.format(dlm=delimiter),
        r'multi{dlm}voxel{dlm}pattern'.format(dlm=delimiter),
        re.compile(r'\WMVPA\W'),
        r'support{dlm}vector'.format(dlm=delimiter),
        re.compile(r'\WSVM\W'),
    ]
)
