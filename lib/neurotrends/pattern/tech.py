cat = 'analysis'

# Import base
from base import *

# Initialize tags
tags = {}

tags['mkda'] = [
  'multi%slevel%skernel%sdensity%sanalysis' % delimrep(4),
  'multi%slevel%skda' % delimrep(2),
  '\Wmkda\W',
]

priptn_kda = [
  'kernel%sdensity%sanalysis' % delimrep(2),
]
negptn_kda = [
  'multi%slevel' % (delimptn),
]
def checkkda(txt, **conargs):
  return contextsearch(txt, priptn_kda, negptn=negptn_kda, 
    ichar='.', npre=25, npost=0, **conargs)

tags['kda'] = [
  re.compile('\WKDA\W'),
  checkkda,
]

tags['ale'] = [
  'activation%slikelihood%sanalysis' % delimrep(2),
  'ginger%sale' % (delimptn),
]

tags['loc'] = [
  'localizer',
]

tags['conj'] = [
  'conjunction%s(?:analy|mask|map)' % (delimptn),
  'cognitive%sconjunction' % (delimptn),
  'conjunction.{,25}contrast',
  'conjunction.{,25}condition',
  'conjunction.{,25}task',
  ]

tags['roi'] = [
  'regions?%sof%sinterest' % delimrep(2),
  '\Wrois?\W',
]

tags['vox'] = [
  'voxel%swise' % (delimptn),
  'whole%sbrain%sanalysis' % delimrep(2),
  'whole%sbrain%scontrast' % delimrep(2),
  'whole%sbrain%sstatistic' % delimrep(2),
  'whole%sbrain%scomparison' % delimrep(2),
  'whole%sbrain%scorrect' % delimrep(2),
]

tags['ppi'] = [
  'psycho%sphysiologic(?:al)?%sinteraction' % delimrep(2),
  'physio%sphysiologic(?:al)?%sinteraction' % delimrep(2),
  '\Wppi\W',
]

tags['betser'] = [
  'beta%sseries' % (delimptn),
]

tags['dcm'] = [
  'dynamic%scausal%smodel' % delimrep(2),
  '\Wdcm\W',
]

tags['grc'] = [
  'granger%scausal' % (delimptn),
]

tags['sem'] = [
  'structural%sequation%smodel' % delimrep(2),
  # Note: SEM conflicts with standard error of the mean
]

tags['vbm'] = [
  'voxel%sbased%smorphometry' % delimrep(2),
  re.compile('\WVBM\W'),
]

tags['pca'] = [
  'principal%scomponents?%sanalysis' % delimrep(2),
  re.compile('\WPCA\W'),
]

tags['ica'] = [
  'independent%scomponents?%sanalysis' % delimrep(2),
  re.compile('\WICA\W'),
]

tags['pls'] = [
  'partial%sleast%ssquares' % delimrep(2),
  re.compile('\WPLS\W'),
]

tags['mvpa'] = [
  'multi%svariate%spattern' % delimrep(2),
  'multi%svoxel%spattern' % delimrep(2),
  re.compile('\WMVPA\W'),
  'support%svector' % (delimptn),
  re.compile('\WSVM\W'),
]
