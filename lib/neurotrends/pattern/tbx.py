cat = 'tool'

# Import base
from base import *

# Initialize tags
tags = {}

tags['marsbar'] = [
  'mars%sbar' % (delimptn),
  'sourceforge\.net/projects/marsbar',
  'marseille%sregion%sof%sinterest%stoolbox' % delimrep(4),
]

tags['pickatlas'] = [
  '\Wpick%satlas' % (delimptn),
]

tags['surfrend'] = [
  '\Wsurf%srend' % (delimptn),
]

tags['rest'] = [
  'resting%sstate%sfmri%sdata%sanalysis%stoolkit' % delimrep(5),
  'rest%s(?:by)?%ssong%sxiao' % delimrep(3),
  'resting\-fmri\.sourceforge\.net',
  'sourceforge\.net/projects/resting\-fmri',
  'restfmri\.net',
]

tags['aal'] = [
  re.compile('\WAAL\W'),
  'automatic%sanatomic(?:al)?%slabel' % delimrep(2),
]

tags['snpm'] = [
  '\Wsnpm\W',
  'statistical%snon%sparametric%smapping' % delimrep(3),
]

tags['spmd'] = [
  '\Wspmd\W',
  'statistical%sparametric%smapping%sdiagnosis' % delimrep(3),
]

tags['artrepair'] = [
  '\Wart%srepair' % (delimptn),
]

tags['xjview'] = [
  'xjview',
]

tags['fmripower'] = [
  'fmri%spower' % (delimptn),
]

tags['suit'] = [
    'spatially%sun%sbiased%sinfra%stentorial' % delimrep(4),
    '\Wsuit%stoolbox' % (delimptn),
]

tags['gift'] = [
  'gift%s(?:toolbox|software|program|package|library)' % (delimptn),
  'group%sica%sof%sfmri' % delimrep(3),
]

tags['daemon'] = [
    'talairach%sda?emon' % (delimptn),
    'talairach%sclient' % (delimptn),
    'talairach%sapp' % (delimptn),
]

tags['mnital'] = [
  '%s%s(?:%s)?%s(?:2|to)%stal' 
    % (mniptn, delimptn, spcptn, delimptn, delimptn),
  'tal(?:airach)?%s(?:2|to)%s%s' % (delimptn, delimptn, mniptn),
  'imaging\.mrc\-cbu\.cam\.ac\.uk/imaging/mnitalairach',
]

tags['mricro'] = [
  '\Wmricron?\W',
]
