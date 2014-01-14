category = 'analysis'

from neurotrends.config import re

from neurotrends.tagger import RexTagger, MultiRexTagger
from misc import delimiter

syn_ptn = r'(spm|canonical|standard|synthetic|reference|(proto)?typical)'
hrf_ptn = r'(hrf|hdr|ha?emodynamic{dlm}(impulse)?{dlm}response)'.format(
    dlm=delimiter
)

selavg = RexTagger(
    'selavg',
    [
        r'selective(ly)?{dlm}averag'.format(dlm=delimiter),
    ]
)

hrf = RexTagger(
    'hrf',
    [
        syn_ptn + delimiter + hrf_ptn,
        r'''
            convol(ved?|ution){dlm}with{dlm}(an?|the){dlm}
                {syn}?{dlm}{hrf}
        '''.format(
            syn=syn_ptn,
            hrf=hrf_ptn,
            dlm=delimiter,
        ),
        r'gamma{dlm}{hrf}'.format(
            hrf=hrf_ptn,
            dlm=delimiter,
        ),
        r'(single|first|positive){dlm}gamma{dlm}function'.format(dlm=delimiter),
        r'(double|second){dlm}gamma'.format(dlm=delimiter),
        r'gamma{dlm}variate'.format(dlm=delimiter),
        r'delayed{dlm}gamma{dlm}function'.format(dlm=delimiter),
        r'(hrf|hdr){dlm}convol'.format(dlm=delimiter),
    ]
)

hrf_context = MultiRexTagger(
    'hrf',
    [
        r'convol',
    ],
    [
        r'\Whrf\W',
        r'\Whdr\W',
        r'ha?emodynamic{dlm}response'.format(dlm=delimiter),
        r'double{dlm}gamma'.format(dlm=delimiter),
        r'gamma{dlm}variate'.format(dlm=delimiter),
        r'gamma{dlm}function'.format(dlm=delimiter),
        r'variate{dlm}function'.format(dlm=delimiter),
    ],
    separator='[^.,:;?]*'
)

tmpdrv = RexTagger(
    'tmpdrv',
    [
        'temporal{dlm}(and{dlm}dispersion)?{dlm}derivative'.format(dlm=delimiter),
        'time{dlm}(and{dlm}dispersion)?{dlm}derivative'.format(dlm=delimiter),
    ]
)

tmpdrv_context = MultiRexTagger(
    'tmpdrv',
    [
        r'(hrf|hdr|ha?emodynamic{dlm}response)'.format(dlm=delimiter),
    ],
    [
        r'first{dlm}derivative'.format(dlm=delimiter),
    ],
    separator='[^.,:;?]*'
)

dspdrv = RexTagger(
    'dspdrv',
    [
        r'dispersion{dlm}derivative'.format(dlm=delimiter),
    ]
)

fir = RexTagger(
    'fir',
    [
        re.compile(r'\WFIR\W'),
        r'\Wfir{dlm}\)?(basis|set)'.format(dlm=delimiter),
        r'finite{dlm}impulse{dlm}response'.format(dlm=delimiter),
    ]
)

fir_context = MultiRexTagger(
    'fir',
    [
        r'not?{dlm}assum'.format(dlm=delimiter),
        r'not{dlm}make{dlm}(any)?{dlm}assum'.format(dlm=delimiter),
        r'ma[dk](es?|ing)?{dlm}no{dlm}assum'.format(dlm=delimiter),
    ],
    [
        hrf_ptn,
        r'response{dlm}shape'.format(dlm=delimiter),
        r'shape{dlm}of{dlm}(the)?{dlm}response'.format(dlm=delimiter),
        r'time{dlm}cource'.format(dlm=delimiter),
    ],
    separator='[^.,:;?]*'
)

fir_stick_context = MultiRexTagger(
    'fir',
    [
        r'se(t|ries){dlm}of{dlm}(delta|stick){dlm}function'.format(dlm=delimiter),
    ],
    [
        r'convol',
    ],
    separator='[^.,:;?]*'
)

rfx = RexTagger(
    'rfx',
    [
        r'random{dlm}effect'.format(dlm=delimiter),
        re.compile(r'\WRFX\W'),
    ]
)

ffx = RexTagger(
    'ffx',
    [
        r'fixed{dlm}effect'.format(dlm=delimiter),
        re.compile(r'\WFFX\W'),
    ]
)
