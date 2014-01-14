category = 'analysis'

from neurotrends.config import re
from neurotrends.tagger import RexTagger, MultiRexTagger
from misc import delimiter

fdr = RexTagger(
    'fdr',
    [
        r'false{dlm}discovery{dlm}rate'.format(dlm=delimiter),
        r'\Wfdr\W',
    ]
)

fwe = RexTagger(
    'fwe',
    [
        r'family{dlm}wise{dlm}error'.format(dlm=delimiter),
        r'\Wfwe\w',
    ]
)

rft = RexTagger(
    'rft',
    [
        r'random{dlm}field{dlm}theory'.format(dlm=delimiter),
        r'gaussian{dlm}random{dlm}field'.format(dlm=delimiter),
        r'\Wgrf{dlm}theory'.format(dlm=delimiter),
        r'theory{dlm}of{dlm}random{dlm}fields'.format(dlm=delimiter),
        # Worsley et al., 1992
        r'''
            a{dlm}three{dlm}dimensional{dlm}statistical{dlm}analysis{dlm}
                for{dlm}cbf{dlm}activation{dlm}studies{dlm}in{dlm}human
                {dlm}brain
        '''.format(dlm=delimiter),
        # Friston et al., 1994
        r'''
            assessing{dlm}the{dlm}significance{dlm}of{dlm}focal{dlm}
                activations{dlm}using{dlm}their{dlm}spatial{dlm}extent
        '''.format(dlm=delimiter),
    ]
)

bon = MultiRexTagger(
    'bon',
    [
        r'bonferr?oni',
    ],
    [
        r'activation',
        r'voxel',
        r'spm',
        r'map',
    ],
    separator='[^.,:;?]*'
)

svc = RexTagger(
    'svc',
    [
        r'small{dlm}volume{dlm}correction'.format(dlm=delimiter),
        r'\Wsvc\W',
    ]
)

# Tag AlphaSim separately from general Monte Carlo methods to identify
# incorrect use when applied without smoothness estimation
alphasim = RexTagger(
    'alphasim',
    [
        r'alpha{dlm}sim'.format(dlm=delimiter),
        r'clustsim',
    ]
)

alphasim_context = MultiRexTagger(
    'alphasim',
    [
        r'monte{dlm}carlo'.format(dlm=delimiter),
    ],
    [
        r'rest{dlm}fmri'.format(dlm=delimiter),
        re.compile(r'AFNI'),
        re.compile(r'REST'),
    ]
)

monte = RexTagger(
    'monte',
    [
        r'alpha{dlm}sim'.format(dlm=delimiter),
        r'clustsim',
        r'monte{dlm}carlo{dlm}correct'.format(dlm=delimiter),
    ]
)

monte_context = MultiRexTagger(
    'monte',
    [
        r'monte{dlm}carlo'.format(dlm=delimiter),
    ],
    [
        r'multiple{dlm}comparison'.format(dlm=delimiter),
        r'rest{dlm}fmri'.format(dlm=delimiter),
        r'threshold',
        re.compile(r'AFNI'),
        re.compile(r'REST'),
    ]
)

tfce = RexTagger(
    'tfce',
    [
        r'''
            threshold{dlm}free{dlm}cluster{dlm}enhancement
        '''.format(dlm=delimiter),
        r'\Wtcfe\W',
    ]
)
