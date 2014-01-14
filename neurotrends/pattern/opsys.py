category = 'tool'

from neurotrends.config import re

from neurotrends.tagger import RexTagger, MultiRexTagger
from misc import delimiter

os_secondary_ptn = [
    r'\Wpc\W',
    r'\Wos\W',
    r'operating',
    r'platform',
    r'environment',
    r'workstation',
]

mac = RexTagger(
    'mac',
    [
        re.compile(r'OS[-/\s]*X'),
        r'\Wmac{dlm}os\W'.format(dlm=delimiter),
        r'spss{dlm}for{dlm}mac'.format(dlm=delimiter),
    ]
)

mac_context = MultiRexTagger(
    'mac',
    [
        r'apple',
        r'mac(intosh)?',
    ],
    os_secondary_ptn,
    separator='[^.,:;?]*'
)

windows_context = MultiRexTagger(
    'windows',
    [
        r'windows',
    ],
    [
        # Windows versions
        r'\W95\W',
        r'\W98\W',
        r'\W2000\W',
        r'\W7\W',
        r'\W8\W',
        r'\Wnt\W',
        r'\Wme\W',
        r'\Wxp\W',
        r'\Wmillenn?ium\W',
        r'\Wvista\W',
        # Captures e.g. "SPSS for Windows"
        r'spss',
    ] + os_secondary_ptn,
    separator='[^.,:;?]*'
)

linux = RexTagger(
    'linux',
    [
        r'unix',
        r'linux',
        r'centos',
        r'debian',
        r'ubuntu',
        r'knoppix',
        re.compile(r'SUSE'),
        r'solaris',
        r'\Wsunos\W',
    ]
)
