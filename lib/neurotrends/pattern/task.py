cat = 'tool'

# Import base
from base import *

###############
# Define tags #
###############

tags = {}

tags['eprime'] = {
  'bool' : [
    '\We%sprime' % (delimptn),
  ],
}

tags['presentation'] = {
  'bool' : [
    'neuro%sbs' % (delimptn),
    'neuro%sbehavioral%ssystems' % delimrep(2),
  ],
}

tags['ptb'] = [
    'psychtoolbox',
    'psychophysics%stoolbox' % (delimptn),
]

tags['psychopy'] = [
  '\Wpsychopy\W',
]

tags['visionegg'] = [
  'vision%segg' % (delimptn),
]

tags['directrt'] = [
  'directrt',
]

tags['stim'] = [
  '\Wstim\W.{,50}neuro%sscan' % (delimptn),
]

tags['inquisit'] = [
  'inquisit[^a-z]',
]

tags['cogent'] = [
  'cogent.{,50}(?:vislab|wellcome)',
  'cogent.{,50}(?<!\w)fil(?!\w)',
  'cogent(?:_2000)?\.(?:html|php)',
  'cogent%s2000' % (verfill),
]

tags['psyscope'] = [
  'psyscope',
]

tags['superlab'] = [
  'superlab',
]

################
# Add versions #
################

# Add E-Prime versions
eprimevers = ['1', '1.1', '1.2', '2']
tags['eprime'] = makever('eprime', tags['eprime'], eprimevers,
  escchars='.', negahead='(\w|\.[1-9])')
