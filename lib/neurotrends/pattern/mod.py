cat = 'analysis'

# Import base
from base import *

# Check HRF
priptn_hrf = [
  'convol',
]
secptn_hrf = [
  '\Whrf\W',
  '\Whdr\W',
  'ha?emodynamic%sresponse' % (delimptn),
  'double%sgamma' % (delimptn),
  'gamma%svariate' % (delimptn),
  'gamma%sfunction' % (delimptn),
  'variate%sfunction' % (delimptn),
]
def checkhrf(txt, **conargs):
  return contextsearch(txt, priptn_hrf, secptn_hrf, **conargs)

# Check temporal derivative
priptn_tmpdrv = [
  '(?:hrf|hdr|ha?emodynamic%sresponse)' % (delimptn),
]
secptn_tmpdrv = [
  'first%sderivative' % (delimptn),
]
def checktmpdrv(txt, **conargs):
  return contextsearch(txt, priptn_tmpdrv, secptn_tmpdrv, ichar='.', **conargs)

synptn = '(?:spm|canonical|standard|synthetic|reference|(?:proto)?typical)'
hrfptn = '(?:hrf|hdr|ha?emodynamic%s(?:impulse)?%sresponse)' % delimrep(2)

# Check FIR
priptn_fir = [
  'not?%sassum' % (delimptn),
  'not%smake%s(?:any)?%sassum' % delimrep(3),
  'ma[dk](?:es?|ing)?%sno%sassum' % delimrep(2),
]
secptn_fir = [
  hrfptn,
  'response%sshape' % (delimptn),
  'shape%sof%s(?:the)?%sresponse' % delimrep(3),
  'time%scource' % (delimptn),
]
def checkfir(txt, **conargs):
  return contextsearch(txt, priptn_fir, secptn_fir, ichar='.', npre=0)

# Check stick function
priptn_stick = [
  'se(?:t|ries)%sof%s(?:delta|stick)%sfunction' % delimrep(3),
]
negptn_stick = [
  'convol',
]
def checkstick(txt, **conargs):
  return contextsearch(txt, priptn_stick, negptn=negptn_stick, 
    ichar='.', **conargs)

# Initialize tags
tags = {}

tags['selavg'] = [
  'selective(?:ly)?%saverag' % (delimptn),
]

tags['hrf'] = [
  synptn + delimptn + hrfptn,
  'convol(?:ved?|ution)%swith%s(?:an?|the)' + \
    delimptn + synptn + '?' + delimptn + hrfptn,
  'gamma%s%s' % (delimptn, hrfptn),
  '(?:single|first|positive)%sgamma%sfunction' % delimrep(2),
  '(?:double|second)%sgamma' % (delimptn),
  'gamma%svariate' % (delimptn),
  'delayed%sgamma%sfunction' % delimrep(2),
  '(?:hrf|hdr)%sconvol' % (delimptn),
  checkhrf,
]

tags['tmpdrv'] = [
  'temporal%s(?:and%sdispersion)?%sderivative' % delimrep(3),
  'time%s(?:and%sdispersion)?%sderivative' % delimrep(3),
  checktmpdrv,
]

tags['dspdrv'] = [
  'dispersion%sderivative' % (delimptn),
]

tags['fir'] = [
  re.compile('\WFIR\W'),
  '\Wfir%s\)?(?:basis|set)' % delimrep(1),
  'finite%simpulse%sresponse' % delimrep(2),
  checkfir,
  checkstick,
]

tags['rfx'] = [
    'random%seffect' % (delimptn),
    re.compile('\WRFX\W'),
]

tags['ffx'] = [
  'fixed%seffect' % (delimptn),
  re.compile('\WFFX\W'),
]
