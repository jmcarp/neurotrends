cat = 'analysis'

# Import base
from base import *

# Check Monte Carlo correction
priptn_monte = [
  'monte%scarlo' % (delimptn),
]
secptn_monte = [
  'multiple%scomparison' % (delimptn),
]
def checkmonte(txt, **conargs):
  return contextsearch(txt, priptn_monte, secptn_monte, ichar='.', **conargs)

# Initialize tags
tags = {}

tags['fdr'] = [
  'false%sdiscovery%srate' % delimrep(2),
  '\Wfdr',
]

tags['fwe'] = [
  'family%swise%serror' % delimrep(2),
  '\Wfwe',
]

tags['rft'] = [
  'random%sfield%stheory' % delimrep(2),
  'gaussian%srandom%sfield' % delimrep(2),
  '\Wgrf%stheory' % (delimptn),
  'theory%sof%srandom%sfields' % delimrep(3),
  # Worsley et al., 1992
  ('a%sthree%sdimensional%sstatistical%sanalysis%s' + \
    'for%scbf%sactivation%sstudies%sin%shuman%sbrain') % \
    delimrep(11),
  # Friston et al., 1994
  ('assessing%sthe%ssignificance%sof%sfocal%sactivations%s' + \
    'using%stheir%sspatial%sextent') % delimrep(9),
]

tags['bon'] = [
  'bonferroni',
]

tags['svc'] = [
  'small%svolume%scorrection' % delimrep(2),
  '\Wsvc\W',
]

tags['monte'] = [
  'alpha%ssim' % (delimptn),
  'monte%scarlo%scorrect' % delimrep(2),
  checkmonte,
]

tags['tfce'] = [
  'threshold%sfree%scluster%senhancement' % delimrep(3),
  '\Wtcfe\W',
]
