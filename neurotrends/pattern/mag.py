cat = 'tool'

# Import base
from base import *

# Magnet attributes
vendptn = 'siemens|philips|general%selectric|\Wge\W' % (delimptn)
scanptn = 'magnet|scan(?:ner)?|mri|field|system'
magptn = '(?:%s|%s)' % (vendptn, scanptn)

tesptn = '(?:tesla|t(?!\w|%s=|%s\d+|\())' % (delimptn, delimptn)
numptn = '[\s\(](\d{1,2}\.?\d{,2})(?!=\d)'

fieldptn = [
  numptn + delimptn + tesptn,
]

fieldptn = [re.compile(ptn, srcflags) for ptn in fieldptn]

sigptn = 'p%s[<=>]+%s\d?\.\d+' % delimrep(2)
sigptn = re.compile(sigptn, srcflags)

def estfield(txt):

  field = []
  gstrs = []

  for ptn in fieldptn:
    matches = re.finditer(ptn, txt)
    if matches:
      for match in matches:
        shortcon = getcontext(match=match, txt=txt, ncharpre=50, ncharpost=50)
        if not re.search(magptn, shortcon, re.I):
          continue
        postcon = getcontext(match=match, txt=txt, ncharpre=0, ncharpost=50)
        if re.search(sigptn, postcon):
          continue
        try:
          gfloat = float(match.groups()[0])
          gstr = str(gfloat)
          context = getcontext(match=match, txt=txt)
          context = UnicodeDammit(context).unicode
          if minfield <= gfloat <= maxfield and gstr not in gstrs:
            field.append((gstr, context))
            gstrs.append(gstr)
        except:
          pass
  
  return field

tags = {}

# Field strength
tags['field'] = [estfield]

# Vendors
tags['ge'] = [
  re.compile('\WGE\W'),
  'general%selectric' % (delimptn),
]

tags['siemens'] = [
  'siemens'
]

tags['philips'] = [
  'philips',
]

tags['bruker'] = [
  'bruker',
]

tags['varian'] = [
  'varian',
]

tags['shimadzu'] = [
  'shimadzu',
]

tags['marconi'] = [
    'marconi',
]
