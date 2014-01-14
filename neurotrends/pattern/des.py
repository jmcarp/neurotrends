category = 'analysis'

from neurotrends.tagger import RexTagger, MultiRexTagger

from .misc import delimiter

from neurotrends.config import re

event = RexTagger(
    'event',
    [
        r'null{dlm}event'.format(dlm=delimiter),
        r'null{dlm}trial'.format(dlm=delimiter),
        r'fixation{dlm}event'.format(dlm=delimiter),
        r'fixation{dlm}trial'.format(dlm=delimiter),
        r'''
            separating{dlm}processes{dlm}within{dlm}a{dlm}trial{dlm}in{dlm}
                event{dlm}related{dlm}functional{dlm}mri
        '''.format(dlm=delimiter),
        r'''
            a{dlm}trial{dlm}based{dlm}experimental{dlm}design{dlm}for{dlm}fmri
        '''.format(dlm=delimiter),
    ]
)

event_context = MultiRexTagger(
    'event',
    [
        r'event{dlm}related{dlm}design'.format(dlm=delimiter),
        r'event{dlm}related{dlm}analysis'.format(dlm=delimiter),
        r'event{dlm}related{dlm}fmri'.format(dlm=delimiter),
        r'event{dlm}related{dlm}task'.format(dlm=delimiter),
        r'event{dlm}related{dlm}trial'.format(dlm=delimiter),
        r'event{dlm}related{dlm}model'.format(dlm=delimiter),
        r'event{dlm}related{dlm}tatistic'.format(dlm=delimiter),
        r'event{dlm}related{dlm}functional{dlm}mri'.format(dlm=delimiter),
        r'event{dlm}related{dlm}functional{dlm}magnetic'.format(dlm=delimiter),
        r'\Wer{dlm}fmri\W'.format(dlm=delimiter),
        r'single{dlm}event{dlm}design'.format(dlm=delimiter),
        r'event{dlm}of{dlm}interest'.format(dlm=delimiter),
        r'stick{dlm}function'.format(dlm=delimiter),
    ],
    rexes_negative=[
        r'\Wpp\.{dlm}\d+'.format(dlm=delimiter),
        r'\d+[\s-]+\d+',
        r'neuroimage',
        r'neuron',
        r'proceedings',
        r'transactions',
        re.compile(r'Trans[^a-zA-Z]'),
        re.compile(r'Research'),
        r'pnas',
        r'biol(ogical)?{dlm}psych'.format(dlm=delimiter),
        r'j(ournal{dlm}of)?{dlm}neurosci'.format(dlm=delimiter),
        r'arch(ives{dlm}of)?{dlm}gen'.format(dlm=delimiter),
        r'brain{dlm}cogn'.format(dlm=delimiter),
        r'journal',
        r'plos',
        r'frontiers',
    ]
)

block = RexTagger(
    'block',
    [
        r'block[^.]{,25}design',
        r'block(ed)?{dlm}(trial)?{dlm}design'.format(dlm=delimiter),
        r'block(ed)?{dlm}(trial)?{dlm}paradigm'.format(dlm=delimiter),
        r'block(ed)?{dlm}(trial)?{dlm}presentation'.format(dlm=delimiter),
        r'block(ed)?{dlm}(trial)?{dlm}analysis'.format(dlm=delimiter),
        r'epoch(ed)?{dlm}design'.format(dlm=delimiter),
        r'epoch(ed)?{dlm}paradigm'.format(dlm=delimiter),
        r'epoch(ed)?{dlm}related'.format(dlm=delimiter),
        r'epoch(ed)?{dlm}based'.format(dlm=delimiter),
        r'epoch(ed)?{dlm}analysis'.format(dlm=delimiter),
        r'alternating{dlm}block'.format(dlm=delimiter),
        r'interleaved{dlm}block'.format(dlm=delimiter),
        r'separate{dlm}block'.format(dlm=delimiter),
        r'presented{dlm}in{dlm}block'.format(dlm=delimiter),
    ]
)

mixed = RexTagger(
    'mixed',
    [
        r'''
            [^-\w]mixed{dlm}design(?!.{{,50}}?
                (m?anc?ova|analysis of (co)?variance))
        '''.format(dlm=delimiter),
        r'mixed{dlm}block(ed)?[\s\/]event'.format(dlm=delimiter),
    ]
)
