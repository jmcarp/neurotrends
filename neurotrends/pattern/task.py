category = 'tool'

from neurotrends.tagger import Looks, RexTagger, RexComboVersionTagger

from .misc import delimiter, version_separator

# Ignore alphanumeric characters or a dot followed by a number after version
# to avoid e.g. counting "eprime 1.1" as both eprime 1 and eprime 1.1
eprime = RexComboVersionTagger(
    'eprime',
    [
        r'\We{dlm}prime'.format(dlm=delimiter),
    ],
    version_separator,
    looks=Looks(negahead=r'(\w|\.[1-9])'),
    versions=[
        '1', '1.1', '1.2', '2',
    ],
)

presentation = RexTagger(
    'presentation',
    [
        r'neuro{dlm}bs'.format(dlm=delimiter),
        r'neuro{dlm}behavioral{dlm}systems'.format(dlm=delimiter),
    ]
)

psychtoolbox = RexTagger(
    'psychtoolbox',
    [
        r'psychtoolbox',
        r'psychophysics{dlm}toolbox'.format(dlm=delimiter),
    ]
)

psychopy = RexTagger(
    'psychopy',
    [
        r'\Wpsychopy\W',
    ]
)

visionegg = RexTagger(
    'visionegg',
    [
        r'vision{dlm}egg'.format(dlm=delimiter),
    ]
)

directrt = RexTagger(
    'directrt',
    [
        r'directrt',
    ]
)

stim = RexTagger(
    'stim',
    [
        r'\Wstim\W.{{,50}}neuro{dlm}scan'.format(dlm=delimiter),
    ]
)

inquisit = RexTagger(
    'inquisit',
    [
        r'inquisit[^a-z]',
    ]
)

cogent = RexTagger(
    'cogent',
    [
        r'cogent.{{,50}}(?:vislab|wellcome)',
        r'cogent.{{,50}}(?<!\w)fil(?!\w)',
        r'cogent(?:_2000)?\.(?:html|php)',
        r'cogent{ver}2000'.format(ver=version_separator),
    ]
)

psyscope = RexTagger(
    'psyscope',
    [
        r'psyscope',
    ]
)

superlab = RexTagger(
    'superlab',
    [
        r'superlab',
    ]
)
