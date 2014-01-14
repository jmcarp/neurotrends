category = 'tool'

from neurotrends.config import re
from neurotrends.tagger import RexTagger
from misc import delimiter, mni_ptn, spc_ptn

marsbar = RexTagger(
    'marsbar',
    [
        r'mars{dlm}bar'.format(dlm=delimiter),
        r'sourceforge\.net/projects/marsbar',
        r'''
            marseille{dlm}region{dlm}of{dlm}interest{dlm}toolbox
        '''.format(dlm=delimiter),
    ]
)

pickatlas = RexTagger(
    'pickatlas',
    [
        r'\Wpick{dlm}atlas'.format(dlm=delimiter),
    ]
)

surfrend = RexTagger(
    'surfrend',
    [
        r'\Wsurf{dlm}rend'.format(dlm=delimiter),
    ]
)

rest = RexTagger(
    'rest',
    [
        r'resting{dlm}state{dlm}fmri{dlm}data{dlm}analysis{dlm}toolkit'.format(dlm=delimiter),
        r'rest{dlm}(by)?{dlm}song{dlm}xiao'.format(dlm=delimiter),
        r'resting\-fmri\.sourceforge\.net',
        r'sourceforge\.net/projects/resting\-fmri',
        r'restfmri\.net',
    ]
)

aal = RexTagger(
    'aal',
    [
        re.compile(r'\WAAL\W'),
        r'automatic{dlm}anatomic(al)?{dlm}label'.format(dlm=delimiter),
    ]
)

snpm = RexTagger(
    'snpm',
        [
        r'\Wsnpm\W',
        r'statistical{dlm}non{dlm}parametric{dlm}mapping'.format(dlm=delimiter),
    ]
)

spmd = RexTagger(
    'spmd',
        [
        r'\Wspmd\W',
        r'''
            statistical{dlm}parametric{dlm}mapping{dlm}diagnosis
        '''.format(dlm=delimiter),
    ]
)

artrepair = RexTagger(
    'artrepair',
        [
        r'\Wart{dlm}repair'.format(dlm=delimiter),
    ]
)

xjview = RexTagger(
    'xjview',
    [
        r'xjview',
    ]
)

fmripower = RexTagger(
    'fmripower',
    [
        r'fmri{dlm}power'.format(dlm=delimiter),
    ]
)

suit = RexTagger(
    'suit',
    [
        r'spatially{dlm}un{dlm}biased{dlm}infra{dlm}tentorial'.format(dlm=delimiter),
        r'\Wsuit{dlm}toolbox'.format(dlm=delimiter),
    ]
)

gift = RexTagger(
    'gift',
        [
        r'gift{dlm}(toolbox|software|program|package|library)'.format(dlm=delimiter),
        r'group{dlm}ica{dlm}of{dlm}fmri'.format(dlm=delimiter),
    ]
)

daemon = RexTagger(
    'daemon',
    [
        r'talairach{dlm}da?emon'.format(dlm=delimiter),
        r'talairach{dlm}client'.format(dlm=delimiter),
        r'talairach{dlm}app'.format(dlm=delimiter),
    ]
)

mnital = RexTagger(
    'mnital',
    [
        '{mni}{dlm}({spc})?{dlm}(2|to){dlm}tal'.format(
            mni=mni_ptn,
            spc=spc_ptn,
            dlm=delimiter,
        ),
        r'tal(airach)?{dlm}(2|to){dlm}{mni}'.format(
            mni=mni_ptn,
            dlm=delimiter,
        ),
        r'imaging\.mrc\-cbu\.cam\.ac\.uk/imaging/mnitalairach',
    ]
)

mricro = RexTagger(
    'mricron',
    [
        r'\Wmricron?\W',
    ]
)
