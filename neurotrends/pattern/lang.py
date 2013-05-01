'''

'''

cat = 'tool'

# Imports
import os
import shelve

# Project imports
from neurotrends import trendpath

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

import requests
from BeautifulSoup import BeautifulSoup as BS

def get_matlab_versions(overwrite=False):
    '''Get MATLAB versions from Wikipedia.

    Args:
        overwrite (bool) : Overwrite existing data
    Returns:
        Dictionary of MATLAB versions
        
    '''
    
    # Get version file
    version_file = '%s/matlab-versions.shelf' % (trendpath.data_dir)

    # Used saved versions if version file exists and not overwrite
    if os.path.exists(version_file) and not overwrite:
        shelf = shelve.open(version_file)
        versions = shelf['versions']
        shelf.close()
        return versions

    # Open Wikipedia page
    req = requests.get('http://en.wikipedia.org/wiki/MATLAB')
    soup = BS(req.text)

    # Find Release History table
    histtxt = soup.find(text=re.compile('release history', re.I))
    histspn = histtxt.findParent('span')
    histtab = histspn.findNext('table', {'class' : 'wikitable'})
    histrow = histtab.findAll('tr')
    
    # Initialize Matlab versions
    versions = {}

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

        # Add to versions
        versions[vernum] = [vernum]
        if vernam:
            versions[vernum].append(vernam)
    
    # Save results to version file
    shelf = shelve.open(version_file)
    shelf['versions'] = versions
    shelf.close()

    # Return versions
    return versions

# Add Matlab versions
matvers = get_matlab_versions()
matnegahead = '(\d|\.[1-9]|st|nd|rd|th)'
#matnegahead = '(a-z|\.[1-9])'
tags['matlab'] = makever('matlab', tags['matlab'], matvers,
    escchars='.', negahead=matnegahead)
