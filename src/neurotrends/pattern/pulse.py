cat = 'tool'

# Import base
from base import *

# Check spiral
priptn_spiral = [
  'spiral',
]
secptn_spiral = [
  'mri',
  'bold',
  'imag',
  'scan',
  'data',
  'pulse',
  'acqui',
  'sequence',
]
def checkspiral(txt, **conargs):
  return contextsearch(txt, priptn_spiral, secptn_spiral, ichar='.', **conargs)


tags = {}

# Structural
tags['mprage'] = [
  '\Wmp%srage\W' % (delimptn),
]

tags['spgr'] = [
  '\Wspgr\W',
]

# Trajectory
tags['epi'] = [
  'echo%splanar' % (delimptn),
  re.compile('EPI'),
]

tags['spiral'] = [
  'spiral%sin\W' % (delimptn),
  'spiral%sout\W' % (delimptn),
  checkspiral,
]

# Sequence
tags['gradient'] = [
  'gradient%secho' % (delimptn),
  'gradient%srecall(?:ed)?' % (delimptn),
]

tags['spin'] = [
  'spin%secho' % (delimptn),
]

tags['grase'] = [
  re.compile('GRASE'),
]

# Acceleration method
tags['sense'] = [
  re.compile('SENSE'),
  'sensitivity%sencoded' % (delimptn),
]

tags['grappa'] = [
  re.compile('GRAPPA'),
]

tags['presto'] = [
  re.compile('PRESTO'),
]

tags['smash'] = [
  re.compile('SMASH'),
]
