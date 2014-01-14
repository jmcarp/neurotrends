category = 'tool'

from neurotrends.config import re

from neurotrends.tagger import Looks, RexTagger, RexComboVersionTagger
from misc import delimiter, version_separator

def post_proc(value):
    return re.sub(r'\.[\.0]+$', '', value)

spm = RexComboVersionTagger(
    'spm',
    [
        r'(?<!\w)spm(?!s)',
        r'statistical{dlm}parametric{dlm}mapping'.format(dlm=delimiter),
    ],
    version_separator,
    looks=Looks(negbehind=r':\s', negahead=r'[\w\-]'),
    versions=[
        '96', '96b', '97', '99', '99b',
        '2', '2b', '5', '5b', '8', '8b',
    ],
)

fsl = RexComboVersionTagger(
    'fsl',
    [
        r'fsl',
        r"fmrib'?s?{dlm}software{dlm}library".format(dlm=delimiter),
    ],
    version_separator,
    arbitrary_rex=r'(?P<version>\d(\.\d){1,2})',
    post_proc=post_proc,
)

afni = RexComboVersionTagger(
    'afni',
    [
        r'afni',
        r'analysis{dlm}of{dlm}functional{dlm}neuroimages'.format(dlm=delimiter),
    ],
    version_separator,
    arbitrary_rex=r'''
        (?P<version>
            (\d\.\d{1,2}[a-z]?)
            |
            (afni_)?(\d{4}_\d{2}_\d{2}_\d{4})
        )
    ''',
    post_proc=post_proc,
)

surfer = RexComboVersionTagger(
    'surfer',
    [
        r'free{dlm}surfer'.format(dlm=delimiter),
    ],
    version_separator,
    arbitrary_rex=r'(?P<version>\d(\.\d)+)',
    post_proc=post_proc,
)

voyager = RexComboVersionTagger(
    'voyager',
    [
        r'brain{dlm}voyager{dlm}(2000|qx)?'.format(dlm=delimiter)
    ],
    version_separator,
    arbitrary_rex=r'(?P<version>\d\.\d)',
    post_proc=post_proc,
)

suma = RexTagger(
    'suma',
    [
        r'\Wsuma\W',
    ],
)

medx = RexTagger(
    'medx',
    [
        r'\Wmedx[^a-z]',
    ],
)

caret = RexTagger(
    'caret',
    [
        r'caret',
        r'surefit',
        r'''
            computerized{dlm}anatomical{dlm}reconstruction{dlm}
                and{dlm}editing{dlm}tool{dlm}kit
        '''.format(dlm=delimiter)
    ],
)

voxbo = RexTagger(
    'voxbo',
    [
        r'voxbo',
    ],
)

nipy = RexTagger(
    'nipy',
    [
        r'nipy(pe)?',
    ],
)

pymvpa = RexTagger(
    'pymvpa',
    [
        r'pymvpa',
    ],
)

cchips = RexTagger(
    'cchips',
    [
        r'cchips',
        r'''
            cincinnati{dlm}children's{dlm}hospital{dlm}
                image{dlm}processing{dlm}software
        '''.format(dlm=delimiter)
    ],
)

lipsia = RexTagger(
    'lipsia',
    [
        r'lipsia',
        r'''
            leipzig{dlm}image{dlm}processing{dlm}and{dlm}
                statistical{dlm}inference{dlm}algorithm
        '''.format(dlm=delimiter)
    ],
)

fmristat = RexTagger(
    'fmristat',
    [
        r'fmristat\W',
    ],
)

fmrlab = RexTagger(
    'fmrlab',
    [
        r'fmrlab',
    ],
)

fiasco = RexTagger(
    'fiasco',
    [
        r'fiasco',
        r'''
            functional{dlm}imaging{dlm}
                analysis{dlm}software'
        '''.format(dlm=delimiter),
    ],
)

fidl = RexTagger(
    'fidl',
    [
        r'fidl',
    ],
)

fiswidgets = RexTagger(
    'fiswidgets',
    [
        r'fiswidgets',
    ],
)

itk = RexTagger(
    'itk',
    [
        re.compile(r'\bITK\b'),
        r'itk\.org',
        r'insight{dlm}tool{dlm}kit'.format(dlm=delimiter),
    ],
)
