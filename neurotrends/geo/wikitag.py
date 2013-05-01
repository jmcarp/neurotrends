# -*- coding: latin-1 -*-

# Imports
import os
import re
import shelve
import urllib

import Queue

import requests
from pyquery import PyQuery
from BeautifulSoup import BeautifulSoup as BS
from BeautifulSoup import UnicodeDammit

import HTMLParser
parser = HTMLParser.HTMLParser()

# Project imports
from neurotrends import trendpath

# Geo imports
from neurotrends.geo import geotools

_base_url = 'http://en.wikipedia.org/wiki'

institutes = [
    'university', 'college', 'hospital', 
    'inserm', 'laboratory', 'laboratoire',
]

depts = [
    'journalism',
    'communication',
    'inserm',
    'information science',
    'computation',
    'speech',
]

def states_from_wikipedia(overwrite=False):
    '''Get list of sovereign states from Wikipedia.

    Args:
        overwrite (bool) : Overwrite existing data
    Returns:
        List of states

    '''
    
    # Get state file
    state_file = '%s/states.shelf' % (trendpath.data_dir)

    # 
    if os.path.exists(state_file) and not overwrite:
        state_shelf = shelve.open(state_file)
        states = state_shelf['states']
        state_shelf.close()
        return states

    html = _wiki_load('List of sovereign states')
    soup = BS(html)

    statespan = soup.find(
        'span',
        {'id' : 'List_of_states'}
    )

    statetable = statespan.findNext('table')
    
    staterows = statetable.findAll('tr')

    states = []

    for row in staterows[1:]:
        
        col = row.find('td')
        if col.find(style='display:none'):
            continue
        coltext = col.text
        if re.search(u'\u2192', coltext):
            continue
        coltext = coltext.replace('&#160;', '')
        coltext = re.sub('\[.*?\]', '', coltext)
        colstates = [state.strip() for state in coltext.split(u'\u2013')]
        states.extend(colstates)
    
    # Write states to shelf
    state_shelf = shelve.open(state_file)
    state_shelf['states'] = states
    state_shelf.close()

    # Return list of states
    return states

def nih_from_wikipedia(overwrite=False):
    '''Get list of NIH institutes from Wikipedia.

    Args:
        overwrite (bool) : Overwrite existing data
    Returns:
        List of institutes

    '''
    
    # Get NIH file
    nih_file = '%s/nih-institutes.shelf' % (trendpath.data_dir)

    # 
    if os.path.exists(nih_file) and not overwrite:
        nih_shelf = shelve.open(nih_file)
        insts = nih_shelf['insts']
        nih_shelf.close()
        return insts

    html = _wiki_load('National Institutes of Health')
    soup = BS(html)

    instspan = soup.find(
        'span',
        {'id' : 'Institutes'}
    )
    
    insttable = instspan.findNext('table')

    instrows = insttable.findAll('tr')

    insts = []
    for row in instrows[1:]:
        instcols = row.findAll('td')
        insts.append({
            'full' : instcols[0].text,
            'abbr' : instcols[1].text,
        })
    
    # Write institutes to shelf
    nih_shelf = shelve.open(nih_file)
    nih_shelf['insts'] = insts
    nih_shelf.close()

    # Return list of institutes
    return insts

states = states_from_wikipedia()

nih_inst = nih_from_wikipedia()
nih_ptn = []
for inst in nih_inst:
    full = inst['full']
    full = re.sub('Institute', 'Institutes?', full, flags=re.I)
    full = re.sub('Disorder', 'Disorders?', full, flags=re.I)
    nih_ptn.append(re.compile(full, re.I))
    nih_ptn.append(re.compile('(?<!\w)' + inst['abbr'] + '(?!\w)'))

non_places = [
    'general hospital', 'teaching hospital', 'institute of medicine', 
    'college of medicine', 'medical school',
]

wiki_variants = [
    ('-', ' '),
    ('\sat\s', ' '),
    ('\(.*?\)', ''),
    ('(?<=\s)(?:and|&amp;)(?=\s).*', ''),
]

contingent_skip_patterns = [
    'division',
    '(?<!\w)unit(?!\w)',
    '(?<!medical )(?<!health )center',
]

_no_cap = ['of', 'for', 'at',]

def _prep_query(query):
    '''Prepare query for Wikipedia. Queries must capitalize (most)
    words, must be in unicode, and must not contain characters with
    accents (ü). For example, the query http://en.wikipedia.org/wiki/Olga_Kurylenko works, 
    but the query http://en.wikipedia.org/wiki/olga_kurylenko does not.

    Args:
        query (str) : Original query
    Returns:
        Wikipedia-formatted query
    
    '''

    # Ensure unicode
    query = UnicodeDammit(query).unicode

    # Replace accents (ü -> u)
    query = geotools.strip_accents(query)
    
    # Split and capitalize query terms
    terms = map(
        lambda s: s.capitalize() if s not in _no_cap else s,
        query.lower().split(' ')
    )
    
    # Join query terms
    query = ' '.join(terms)

    # Return completed query
    return query
    
_not_found = 'wikipedia does not have an article with this exact name'
_disambig = '<b>.*?</b> may (?:also )?refer to'
    
def _wiki_load(query):
    '''Load page from Wikipedia. Returns HTML if page is found.
    
    Args:
        query (str) : Wikipedia page to get (e.g. 'Roger Federer')
    Returns:
        Wikipedia HTML, or None if page not found

    '''
    
    # Load Wikipedia
    url = '%s/%s' % (_base_url, urllib.quote(query))
    req = requests.get(url)

    # Quit if no results
    if re.search(_not_found, req.text, re.I) or \
            re.search(_disambig, req.text, re.I):
        return

    # Return HTML
    return req.text

_exclude_ptns = [
    # Places
    'countries', 'villages', 'streets',
    '\w+_arrondissement', 'states_of',
    'provinces', 'cities_in', 'capitals_in',
    'communes_of', 'prefectures_of',
    'neighborhoods', 'populated',
    # Departments
    'psychiatry', 'social_sciences',
    'subjects_taught', 'medical_specialties',
    'public_university_system',
    # Miscellaneous
    'school_types', 'greek_loanwords',
    # Scientific terms
    'biology', 'branches_of_biology',
    'chemistry', 'biochemistry',
    'molecular', 'cognition', 'human',
]

def _category_filter(html):
    '''Check Wikipedia HTML for bad categories.

    Args:
        html (str): Wikipedia HTM
    Returns:
        True / False
    
    '''
    # Quit if city
    
    return geotools.any_match(_exclude_ptns, html)

_skip_char = [u'\xa0']
_skip_ptn = '[' + ''.join(_skip_char) + ']*'

def _wiki_place(html):
    '''Extract place information (lat / lon) from Wikipedia HTML.

    Args:
        html (str) : Wikipedia HTML
    Returns:
        Dictionary of place information

    '''
    
    # Initialize info
    info = {}

    # Parse HTML
    qhtml = PyQuery(html)

    # Get heading text
    heading_text = qhtml('#firstHeading').text()
    if heading_text:
        info['heading'] = heading_text
    
    # Get location description
    locations = []

    # Check different location types
    for location_type in ['locality', 'region', 'country-name']:

        # Find location span
        location_span = qhtml('span.%s' % (location_type))
        
        # Filter to child elements with text
        for location in location_span('*').filter(lambda: this.text):

            # Get text
            location = location.text

            # Unescape HTML entities
            location = parser.unescape(location)

            # Skip bad patterns
            location = re.sub(_skip_ptn, '', location, re.I)

            # Strip whitespace
            location = location.strip()

            # Add to list
            if location:
                locations.append(location)
     
    # Save concatenated location info
    if locations:
        info['loc'] = ', '.join(locations)
    
    # Find possible coordinates
    coords = qhtml('span.geo')

    # Loop over coordinates
    for coord in coords:

        # Split text by semicolon
        coord_split = PyQuery(coord).text().split(';')

        # Quit if not pair
        if len(coord_split) != 2:
            continue
        
        # Attempt to convert coordinates to float
        try:
            info['lat'] = float(coord_split[0])
            info['lon'] = float(coord_split[1])
            # Quit if successful
            break
        except ValueError:
            pass
    
    # Return info
    return info

def wiki_to_place(query):
    
    # Prepare query for Wikipedia
    query = _prep_query(query)
    
    # Load Wikipedia HTML
    html = _wiki_load(query)

    # Extract place information from HTML
    info = _wiki_place(html)

    # Return place information
    return info

_query_variants = [
    ('-', ' '),
    ('\sat\s', ' '),
    ('\(.*?\)', ''),
    ('(?<=\s)(?:and|&amp;)(?=\s).*', ''),
]

_contingent_skip_patterns = [
    'division', '(?<!\w)unit(?!\w)',
    '(?<!medical )(?<!health )center',
]
_institute_patterns = [
    'university', 'college', 'hospital', 
    'inserm', 'laboratory', 'laboratoire',
]
_department_patterns = [
    'journalism',
    'communication',
    'inserm',
    'information science',
    'computation',
    'speech',
]

#def wiki_to_place_main(query, queue=Queue.Queue(), recurse=False, verbose=True):
def tag(query, queue=Queue.Queue(), recurse=False, verbose=True):
    '''

    '''

    wikiinfo = {}
    
    # Add variants to queue
    for variant in _query_variants:
        if re.search(variant[0], query):
            queue.put(re.sub(variant[0], variant[1], query))
    
    #split_query = [part.strip() for part in query.split(',')]
    split_query = geotools.geo_prep(query)
    wikiinfo['orig_query'] = ', '.join(split_query)
    wikiinfo['orig_n_parts'] = len(split_query)
    
    clean_query = []
    for part in split_query:

        # Skip if part matches contingent skip patterns and 
        # entire query contains an institute pattern
        if geotools.any_match(_contingent_skip_patterns, part) and \
                geotools.any_match(_institute_patterns, query):
            continue
         
        # Skip if part matches department patterns
        if geotools.any_match(_department_patterns, part):
            continue
         
        # Skip if part is a state
        if any([state.lower() == part.lower() for state in states]):
            continue
        clean_query.append(part)
    
    # Search until query empty
    while clean_query:
        join_query = ', '.join(clean_query)
        if any([state.lower() == join_query.lower() for state in states]):
            break
        if any([join_query.lower() == np for np in non_places]):
            break
        if verbose:
            print 'Searching Wikipedia for %s...' % (join_query)
        placeinfo = wiki_to_place(join_query)
        if placeinfo:
            wikiinfo['final_query'] = join_query
            wikiinfo['final_n_parts'] = len(clean_query)
            if 'head' in placeinfo and \
                    placeinfo['head'] and \
                    any([placeinfo['head'].lower() == np for np in non_places]):
                return wikiinfo
            wikiinfo.update(placeinfo)
            return wikiinfo
        # Drop last part
        clean_query.pop()
    
    # Redirect to NIH
    if not recurse and geotools.any_match(nih_ptn, query):
        return tag('National Institutes of Health', 
            recurse=True, verbose=verbose)
    
    # Try next item from queue
    if queue.qsize():
        return tag(queue.get(), queue, verbose=verbose)

    # Fail
    return wikiinfo
