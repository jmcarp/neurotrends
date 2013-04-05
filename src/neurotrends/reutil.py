import re

############
# Patterns #
############

floatptn = u'[-+]?\d*\.?\d+'    # Floating point number
eqptn = u'[<=>\u2264\u2265]+'   # (In)equality
delimptn = u'[\s\-]*?'          # Delimiters
#delimptn = u'[\s\-]*'           # Delimiters

# Pattern for Roman numerals
# http://ccn.ucla.edu/tutorials/diveintopython/regular_expressions/verbose.html
romanparts = [
  'M{0,4}',              # thousands - 0 to 4 M's
  '(CM|CD|D?C{0,3})',    # hundreds - 900 (CM), 400 (CD), 0-300 (0 to 3 C's),
                         #            or 500-800 (D, followed by 0 to 3 C's)
  '(XC|XL|L?X{0,3})',    # tens - 90 (XC), 40 (XL), 0-30 (0 to 3 X's),
                         #        or 50-80 (L, followed by 0 to 3 X's)
  '(IX|IV|V?I{0,3})',    # ones - 9 (IX), 4 (IV), 0-3 (0 to 3 I's),
                         #        or 5-8 (V, followed by 0 to 3 I's)
]
romanptn = ''.join(romanparts)

#############
# Functions #
#############

def tuprep(txt, nrep):
  return (txt,) * nrep

def delimrep(nrep):
  return tuprep(delimptn, nrep)

def getcontext(match=None, txt=None, ptn=None, ncharpre=150, ncharpost=150):

  if not match:
    match = flexsearch(ptn, txt)

  if match:
    span = list(match.span())
    span[0] = max(0, span[0] - ncharpre)
    span[1] = min(span[1] + ncharpost, len(txt))
    return txt[span[0]:span[1]]

  return ''

def flexsearch(ptn, txt, fun=re.search, flags=re.I, pad=True):
  
  # Get type of compiled regex
  retype = type(re.compile(''))

  # Get search arguments
  searchargs = {}

  # Pattern
  searchargs['pattern'] = ptn

  # Text
  if pad:
    searchargs['string'] = ' ' + txt + ' '
  else:
    searchargs['string'] = txt

  # Flags
  if type(ptn) != retype:
    searchargs['flags'] = flags
  
  # Search
  return fun(**searchargs)

def contextsearch(txt, priptn, secptn=[], negptn=[], ichar='', 
    npre=150, npost=150):

  for pri in priptn:

    # Search for primary pattern
    matches = re.finditer(pri, txt, re.I)

    if matches:

      for match in matches:

        # Get context
        context = getcontext(match=match, txt=txt,
          ncharpre=npre, ncharpost=npost)
        
        # Skip if negative match
        if any([flexsearch(ptn, context) for ptn in negptn]):
          continue

        # Return results
        if not secptn:
          return [(True, context)]

        for sec in secptn:

          # Build context patterns
          conptn = []

          if ichar:
            # Ignore characters between primary 
            # and secondary patterns
            iptn = '[^%s]*' % (ichar)
            conptn.append(pri + iptn + sec)
            conptn.append(sec + iptn + pri)

          else:
            
            # Search for secondary pattern
            conptn.append(sec)

          # Search for context patterns
          for ptn in conptn:
            # Return results
            if flexsearch(ptn, context):
              return [(True, context)]
  
  # No results found
  return [(False, '')]
