cat = 'analysis'

# Import base
from base import *

# Check for event-related design
priptn_event = [
  'event%srelated%sdesign' % delimrep(2),
  'event%srelated%sanalysis' % delimrep(2),
  'event%srelated%sfmri' % delimrep(2),
  'event%srelated%stask' % delimrep(2),
  'event%srelated%strial' % delimrep(2),
  'event%srelated%smodel' % delimrep(2),
  'event%srelated%statistic' % delimrep(2),
  'event%srelated%sfunctional%smri' % delimrep(3),
  'event%srelated%sfunctional%smagnetic' % delimrep(3),
  '\Wer%sfmri\W' % (delimptn),
  'single%sevent%sdesign' % delimrep(2),
  'event%sof%sinterest' % delimrep(2),
  'stick%sfunction' % (delimptn),
]
negptn_event = [
  '\Wpp\.%s\d+' % (delimptn),
  '\d+[\s-]+\d+',
  'neuroimage',
  'neuron',
  'proceedings',
  'transactions',
  re.compile('Trans[^a-zA-Z]'),
  re.compile('Research'),
  'pnas',
  'biol(?:ogical)?%spsych' % (delimptn),
  'j(?:ournal%sof)?%sneurosci' % delimrep(2),
  'arch(?:ives%sof)?%sgen' % delimrep(2),
  'brain%scogn' % (delimptn),
  'journal',
  'plos',
  'frontiers',
]
def checkevent(txt, **conargs):
  return contextsearch(txt, priptn_event, negptn=negptn_event, ichar='.', **conargs)

# Initialize tags
tags = {}

tags['event'] = [
  checkevent,
  'null%sevent' % (delimptn),
  'null%strial' % (delimptn),
  'fixation%sevent' % (delimptn),
  'fixation%strial' % (delimptn),
  'separating%sprocesses%swithin%sa%strial%sin%sevent%srelated%sfunctional%smri' % delimrep(9),
  'a%strial%sbased%sexperimental%sdesign%sfor%sfmri' % delimrep(6),
]

tags['block'] = [
  'block[^.]{,25}design',
  'block(?:ed)?%s(?:trial)?%sdesign' % (delimptn, delimptn),
  'block(?:ed)?%s(?:trial)?%sparadigm' % (delimptn, delimptn),
  'block(?:ed)?%s(?:trial)?%spresentation' % (delimptn, delimptn),
  'block(?:ed)?%s(?:trial)?%sanalysis' % (delimptn, delimptn),
  'epoch(?:ed)?%sdesign' % (delimptn),
  'epoch(?:ed)?%sparadigm' % (delimptn),
  'epoch(?:ed)?%srelated' % (delimptn),
  'epoch(?:ed)?%sbased' % (delimptn),
  'epoch(?:ed)?%sanalysis' % (delimptn),
  'alternating%sblock' % (delimptn),
  'interleaved%sblock' % (delimptn),
  'separate%sblock' % (delimptn),
  'presented%sin%sblock' % delimrep(2),
]

tags['mixed'] = [
  '[^-\w]mixed%sdesign(?!.{,50}?(m?anc?ova|analysis of (co)?variance))' % (delimptn),
  'mixed%sblock(?:ed)?[\s\/]event' % (delimptn),
]
