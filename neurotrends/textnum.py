import re

# From text2num.py @ https://github.com/ghewgill/text2num/blob/master/text2num.py #

Small = {
  'zero': 0,
  'one': 1,
  'two': 2,
  'three': 3,
  'four': 4,
  'five': 5,
  'six': 6,
  'seven': 7,
  'eight': 8,
  'nine': 9,
  'ten': 10,
  'eleven': 11,
  'twelve': 12,
  'thirteen': 13,
  'fourteen': 14,
  'fifteen': 15,
  'sixteen': 16,
  'seventeen': 17,
  'eighteen': 18,
  'nineteen': 19,
  'twenty': 20,
  'thirty': 30,
  'forty': 40,
  'fifty': 50,
  'sixty': 60,
  'seventy': 70,
  'eighty': 80,
  'ninety': 90
}

Magnitude = {
  'thousand':     10 ** 3,
  'million':      10 ** 6,
  'billion':      10 ** 9,
  'trillion':     10 ** 12,
  'quadrillion':  10 ** 15,
}

class NumberException(Exception):
  def __init__(self, msg):
    Exception.__init__(self, msg)

def text2num(s):
  a = re.split(r"[\s-]+", s)
  n = 0
  g = 0
  for w in a:
    x = Small.get(w, None)
    if x is not None:
      g += x
    elif w == "hundred":
      g *= 100
    else:
      x = Magnitude.get(w, None)
      if x is not None:
        n += g * x
        g = 0
      else:
        raise NumberException("Unknown number: "+w)
  return n + g

# Josh's code #

# 
delimptn = '[\s\-,]'
numwords = Small.keys() + Magnitude.keys() + ['hundred(?:%s+and)' % (delimptn)]
nwptn = '(?:' + '|'.join(numwords) + ')'
numptn = '(?<!\w)(%s(?:%s+%s)*)(?!\w)' % (nwptn, delimptn, nwptn)
numptn = re.compile(numptn, re.I)

def match2num(match):

  mtxt = match.group(0)
  if mtxt.strip():
    mtxt = re.sub('\s+and\s+', ' ', mtxt)
    mtxt = re.sub(',', '', mtxt)
    mtxt = mtxt.strip()
  
  try:
    return str(text2num(mtxt))
  except:
    return mtxt

def subnum(txt):
  
  return re.sub(numptn, match2num, txt)
