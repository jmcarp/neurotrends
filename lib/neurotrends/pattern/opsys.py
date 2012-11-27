cat = 'tool'

# Import base
from base import *

# Initialize tags
tags = {}

secptn_os = [
  'pc',
  'os',
  'operating',
  'platform',
  'environment',
  'workstation',
]
priptn_mac = [
  'apple',
  'mac(?:intosh)',
]
secptn_mac = [].extend(secptn_os)
def checkmac(txt, **conargs):
  return contextsearch(txt, priptn_mac, secptn_mac, ichar='.')

priptn_windows = [
  'windows'
]
secptn_windows = [
  '95',
  '98',
  '2000',
  '7',
  '8',
  'nt',
  'me',
  'millenn?ium',
  'vista',
].extend(secptn_os)
def checkwindows(txt, **conargs):
  return contextsearch(txt, priptn_windows, secptn_windows, ichar='.')

tags['mac'] = {
  'bool' : [
    checkmac,
    re.compile('OS[-/\s]*X'),
  ],
}

tags['win'] = {
  'bool' : [
    checkwindows,
  ],
}

tags['linux'] = [
  'unix',
  'linux',
  'centos',
  'debian',
  'ubuntu',
  'knoppix',
  re.compile('SUSE'),
  'solaris',
  '\Wsunos\W',
]
