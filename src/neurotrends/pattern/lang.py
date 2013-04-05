cat = 'tool'

# Import base
from base import *

# Initialize tags
tags = {}

tags['matlab'] = {
  'bool' : [
    'matlab',
  ],
}

tags['python'] = [
  'python',
]

tags['java'] = [
  'java(?!%sscript)' % (delimptn),
]

tags['r'] = [
  '\Wr%sproject' % (delimptn),
  '\Wr%sdevelopment%s(?:core)?%steam' % delimrep(3),
  '\Wr%sfoundation%sfor%sstatistical%scomputing' % delimrep(4),
  '(?:software|programming)%s(?:language|environment)%sr(?!\w)' % delimrep(2),
  '\Wr%s(?:software|programming)%s(?:language|senvironment)' % delimrep(2),
  '\Wr%sstatistical' % (delimptn),
  '\Wr%ssoftware' % (delimptn),
  '\Wr%slibrary' % (delimptn),
]

tags['idl'] = [
  '\Widl\W',
  'interactive%sdata%slanguage' % delimrep(2),
]

tags['fortran'] = [
  'fortran',
]

################
# Add versions #
################

import mechanize
from BeautifulSoup import BeautifulSoup as BS

def getmatvers(verbose=True):
  
  if verbose:
    print 'Getting MATLAB versions from Wikipedia...'

  # Set up browser
  br = mechanize.Browser()
  br.addheaders = [('User-Agent',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT)')]

  # Read Wikipedia page
  br.open('http://en.wikipedia.org/wiki/MATLAB')

  # Parse HTML
  html = br.response().read()
  soup = BS(html)

  # Find Release History table
  histtxt = soup.find(text=re.compile('release history', re.I))
  histspn = histtxt.findParent('span')
  histtab = histspn.findNext('table', {'class' : 'wikitable'})
  histrow = histtab.findAll('tr')
  
  # Initialize Matlab versions
  matvers = {}

  for row in histrow[1:]:
    
    # Get <td> elements
    tds = row.findAll('td')

    # Get version number
    vernum = tds[0].text
    vernum = re.sub('matlab\s+', '', vernum, flags=re.I)

    # Get version name
    vernam = tds[1].text
    vernam = re.sub('r', 'r?', vernam, flags=re.I)
    vernam = re.sub('sp', '%s(?:sp|service pack)%s' % delimrep(2), \
      vernam, flags=re.I)

    # Add to <matvers>
    matvers[vernum] = [vernum]
    if vernam:
      matvers[vernum].append(vernam)
  
  if verbose:
    print 'Finished getting MATLAB versions...'

  # Return
  return matvers

# Add Matlab versions
matvers = getmatvers()
matnegahead = '(\d|\.[1-9]|st|nd|rd|th)'
#matnegahead = '(a-z|\.[1-9])'
tags['matlab'] = makever('matlab', tags['matlab'], matvers,
  escchars='.', negahead=matnegahead)
