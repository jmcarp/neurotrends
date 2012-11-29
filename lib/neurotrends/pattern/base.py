# Import modules
import re
import copy

#########
# Rules #
#########

delimptn = u'[\s\-]*?'

def tuprep(txt, nrep):
  return (txt,) * nrep

def delimrep(nrep):
  return tuprep(delimptn, nrep)

floatptn = u'[-+]?\d*\.?\d+'    # Floating point number
corptn = '(?:correct|adjust)(?:ed|ing|ion|ment)?'
movptn = 'mo(?:tion|vement)'
# MNI pattern
mniptn = '(?:mni|montreal%sneurological%sinstitute)' % delimrep(2)
mninumptn = mniptn + delimptn + '\d*'
# Space pattern
spcptn = ('(?:probabilistic)?%s(?:brain)?%s' + \
  '(?:space|atlas|template|co\-?ordinates?|standard|brain|image)') \
  % (delimptn, delimptn)

verchar = ',;:-s('
verchar = '[' + ''.join(['\\' + c for c in verchar]) + ']'
verfill = '(?:' + verchar + '|\([^)@]{,150}\)|software|v(?:ersion)?|library)*'

minfield = 0.5
maxfield = 12

srcflags = re.I | re.U

#############
# Functions #
#############

def makever(pkgname, pkgdict, vers, escchars='', 
    posbehind='', negbehind='', posahead='', negahead='', 
    arbptn=None):
  
  # Copy old versions
  newdict = copy.deepcopy(pkgdict)
  
  # Build looks
  if posbehind:
    posbehind = '(?<=' + posbehind + ')'
  if negbehind:
    negbehind = '(?<!' + negbehind + ')'
  if posahead:
    posahead = '(?=' + posahead + ')'
  if negahead:
    negahead = '(?!' + negahead + ')'
  behind = posbehind + negbehind
  ahead = posahead + negahead
      
  for boolptn in newdict['bool']:

    # Build boolean pattern
    pkgptn = '(?:' + boolptn + ')'
  
    # Add known versions
    for ver in vers:
      
      # Add escape characters
      if type(vers) == dict:
        escver = '(' + '|'.join(vers[ver]) + ')'
      else:
        escver = ver
      for escchar in escchars:
        escver = escver.replace(escchar, '\\' + escchar)

      # Assemble version pattern
      verptn = pkgptn + verfill + behind + escver + ahead

      # Add pattern to dictionary
      if ver not in newdict:
        newdict[ver] = [verptn]
      else:
        newdict[ver].append(verptn)
  
    # Add arbitrary version
    if arbptn:
      if 'arbit' not in newdict:
        newdict['arbit'] = [pkgptn + verfill + behind + arbptn + ahead]
      else:
        newdict['arbit'].append(pkgptn + verfill + behind + arbptn + ahead)

  return newdict

def comptag(tag):
  
  if type(tag) == dict:
    for key in tag:
      arbit = key == 'arbit'
      tag[key] = comprules(tag[key], arbit)
  elif type(tag) == list:
    tag = comprules(tag)
  
  return tag

def comprules(rules, arbit=False):
  
  crules = []

  for rule in rules:
    
    rule = Rule(rule, arbit=arbit)
    crules.append(rule)

  return crules

def getcontext(match=None, txt=None, ptn=None, 
    ncharpre=150, ncharpost=150):

  if not match:
    match = flexsearch(ptn, txt)

  if match:
    span = list(match.span())
    span[0] = max(0, span[0] - ncharpre)
    span[1] = min(span[1] + ncharpost, len(txt))
    return txt[span[0] : span[1]]

  return ''

from BeautifulSoup import UnicodeDammit
class Rule():
  
  def __init__(self, rule, arbit=False):
    self.string, self.regex, self.fun = (None, None, None)
    if type(rule) in [str, unicode]:
      self.string = rule
      self.regex = re.compile(rule, srcflags)
      self.arbit = arbit
    elif hasattr(rule, 'pattern'):
      self.string = rule.pattern
      self.regex = rule
      self.arbit = arbit
    elif hasattr(rule, '__call__'):
      self.fun = rule

  def apply(self, txt):
    if self.fun is not None:
      result = self.fun(txt)
      if result:
        return result
      return [(False, '')]
    if self.regex:
      if self.arbit:
        return flexsearch(self.regex, txt, fun=re.findall)
      result = flexsearch(self.regex, txt)
      if result:
        context = getcontext(match=result, txt=txt)
        context = UnicodeDammit(context).unicode
        return [(True, context)]
      return [(False, '')]

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
