cat = 'analysis'

from neurotrends.tagger import RexTagger
from misc import delimiter, mni_ptn, mni_num_ptn, spc_ptn

mni = RexTagger(
    'mni',
    [
        mni_num_ptn + delimiter + spc_ptn,
        r'{spc}{dlm}of{dlm}the{dlm}{mni}'.format(
            spc=spc_ptn,
            mni=mni_ptn,
            dlm=delimiter,
        ),
    ]
)

tal = RexTagger(
    'tal',
    [
        r'talairach{dlm}{spc}'.format(
            spc=spc_ptn,
            dlm=delimiter,
        ),
    ]
)
