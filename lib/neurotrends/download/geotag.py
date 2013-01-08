# -*- coding: latin-1 -*-

# Import libraries
import re
import time
import urllib

import Queue

from BeautifulSoup import UnicodeDammit

import HTMLParser
parser = HTMLParser.HTMLParser()

from mechtools import *

# Set up Google Maps
from googlemaps import GoogleMaps
from googlemaps import GoogleMapsError
gmaps = GoogleMaps()

# From http://stackoverflow.com/questions/517923/what-is-the-best-way-to-remove-accents-in-a-python-unicode-string
import unicodedata
def strip_accents(s):
   return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))

# Time between queries
waittime = 35

# Email regex
mailre = re.compile(
  '(' +
    '[\w\-\.\+]+' +   # Check for +s also
    '[\s\-]*' +
    '(@|at)+' +
    '[\s\-]*' +
    '[\w\-]+' +
    '[\s\-]*' +
    '(' +
      '[\s\-]*' +
      '(\.|dot)+' +
      '[\s\-]*' +
      '[\w\-]+' +
    ')+' +
  ')', re.I)

inststr = ['university', 'université', 'college']
institutes = [
  'university', 'college', 'hospital', 
  'inserm', 'laboratory', 'laboratoire',
]
instptn = [re.compile(ptn, re.I) for ptn in inststr]

depts = [
  'journalism',
  'communication',
  'inserm',
  'information science',
  'computation',
  'speech',
]

wikibase = 'http://en.wikipedia.org/wiki'
wikinotfound = 'wikipedia does not have an article with this exact name'
wikidisamb = '<b>.*?</b> may (?:also )?refer to'
wikinocaps = ['of', 'for', 'at',]
wikiskipchar = [u'\xa0']
wikiskipptn = '[' + ''.join(wikiskipchar) + ']*'

def anymatch(patterns, text, flags=re.I):
  for pattern in patterns:
    if type(pattern) == str:
      if re.search(pattern, text, flags):
        return True
    elif type(pattern) == type(re.compile('')):
      if pattern.search(text):
        return True
  return False

def statelist():
  
  br = getbr()
  br.open('http://en.wikipedia.org/wiki/List_of_sovereign_states')
  html, soup = br2docs(br)

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
  
  return states

def nihlist():
  
  br = getbr()
  br.open('http://en.wikipedia.org/wiki/National_Institutes_of_Health')
  html, soup = br2docs(br)

  instspan = soup.find(
    'span',
    {'id' : 'Institutes'}
  )
  
  insttable = instspan.findNext('table')

  instrows = insttable.findAll('tr')

  instlist = []
  for row in instrows[1:]:
    instcols = row.findAll('td')
    instlist.append({
      'full' : instcols[0].text,
      'abbr' : instcols[1].text,
    })

  return instlist

states = statelist()

nih_inst = nihlist()
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

def wikiparse(query, queue=Queue.Queue(), recurse=False, verbose=True):
  
  wikiinfo = {}
  
  # Add variants to queue
  for variant in wiki_variants:
    if re.search(variant[0], query):
      queue.put(re.sub(variant[0], variant[1], query))

  split_query = geoprep(query)
  wikiinfo['orig'] = ', '.join(split_query)
  wikiinfo['norig'] = len(split_query)
  
  clean_query = []
  for part in split_query:
    if anymatch(contingent_skip_patterns, part) and \
        anymatch(institutes, query):
      continue
    if anymatch(depts, part):
      continue
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
    placeinfo = wiki2place(join_query)
    if placeinfo:
      wikiinfo['final'] = join_query
      wikiinfo['nfinal'] = len(clean_query)
      if 'head' in placeinfo and \
          placeinfo['head'] and \
          any([placeinfo['head'].lower() == np for np in non_places]):
        return wikiinfo
      wikiinfo.update(placeinfo)
      return wikiinfo
    # Drop last part
    _ = clean_query.pop()
  
  # Redirect to NIH
  if not recurse and anymatch(nih_ptn, query):
    return wikiparse('National Institutes of Health', 
      recurse=True, verbose=verbose)
  
  # Try next item from queue
  if queue.qsize():
    return wikiparse(queue.get(), queue, verbose=verbose)

  # Fail
  return wikiinfo

def wiki2place(query):
  
  placeinfo = {}
  placeinfo['head'] = None
  placeinfo['lat'], placeinfo['lon'] = (None, None)

  # Capitalize query terms
  query_parts = query.lower().split(' ')
  for partidx in range(len(query_parts)):
    part = query_parts[partidx]
    if part not in wikinocaps:
      query_parts[partidx] = part.capitalize()
  
  query_cap = ' '.join(query_parts)
  query_cap = UnicodeDammit(query_cap).unicode
  query_cap = strip_accents(query_cap)

  # Load Wikipedia
  br = getbr()
  try:
    wikiurl = '%s/%s' % (wikibase, urllib.quote(query_cap))
    br.open(wikiurl)
  except:
    return {}
  
  # Read browser
  html, soup = br2docs(br)

  if not soup:
    return {}

  # Quit if no results
  if re.search(wikinotfound, html, re.I) or \
     re.search(wikidisamb, html, re.I):
    return {}
  
  # Quit if city
  city_ptns = [
    # Places
    'category:countries',
    'category:villages',
    'category:streets',
    'category:\w+_arrondissement',
    'category:states_of',
    'category:provinces',
    'category:cities_in',
    'category:capitals_in',
    'category:communes_of',
    'category:prefectures_of',
    'category:neighborhoods',
    'category:populated',
    # Departments
    'category:psychiatry',
    'category:social_sciences',
    'category:subjects_taught',
    'category:medical_specialties',
    'category:public_university_system',
    # Miscellaneous
    'category:school_types',
    'category:greek_loanwords',
    # Scientific terms
    'category:biology',
    'category:branches_of_biology',
    'category:chemistry',
    'category:biochemistry',
    'category:molecular',
    'category:cognition',
    'category:human',
  ]
  if anymatch(city_ptns, html):
    return {}

  # Get heading text
  headh1 = soup.find(
    'h1',
    {'id' : re.compile('firstheading', re.I)}
  )
  if headh1:
    placeinfo['head'] = headh1.text
  
  # Get location description
  loclist = []
  for locpart in ['locality', 'region', 'country-name']:
    locspan = soup.find(
      'span',
      {'class' : re.compile(locpart)}
    )
    if locspan:
      for loctxt in locspan.findAll(text=re.compile('\w+')):
        loctxt = parser.unescape(loctxt)
        loctxt = re.sub(wikiskipptn, '', loctxt, re.I)
        loctxt = loctxt.strip()
        if loctxt:
          loclist.append(loctxt)
  placeinfo['loc'] = ', '.join(loclist)
  
  # Get coordinates
  geospan = soup.find(
    'span',
    {'class' : re.compile('^geo$')}
  )
  
  if geospan:
    geostr = geospan.string
    geosplit = geostr.split(';')
    if len(geosplit) == 2:
      try:
        placeinfo['lat'] = float(geosplit[0].strip())
        placeinfo['lon'] = float(geosplit[1].strip())
      except:
        pass
  
  return placeinfo

def geoprep(query):

  # Strip email
  query = re.sub(mailre, '', query)

  # Strip initial / final characters
  query = query.strip('. ')

  # Split
  splitquery = re.split('\s*,\s*', query)

  # Drop parts before institution
  for splitidx in range(len(splitquery)):
    if any([re.search(inst, splitquery[splitidx]) for inst in instptn]):
      splitquery = splitquery[splitidx:]
      break

  # Drop departments
  clean_query = []
  for part in splitquery:
    if not re.search('department|division', part, re.I):
      clean_query.append(part)
    elif anymatch(instptn, part):
      clean_query.append(part)
  #splitquery = [sq for sq in splitquery if not re.search('department|division', sq, re.I)]

  # Return
  return clean_query
  #return splitquery

def geotag(splitquery, delay=False, verbose=True):
  
  # Initialize results
  geoinfo = {}
  lres = None
  geoinfo['lon'], geoinfo['lat'] = (None, None)

  geoinfo['orig'] = ', '.join(splitquery)
  geoinfo['norig'] = len(splitquery)

  while True:
    
    # Build query
    tmpquery = ', '.join(splitquery)
    tmpquery = tmpquery.encode('utf-8', 'ignore')
    
    try:
      
      # Delay
      if delay:
        time.sleep(waittime)

      # Send Google Maps query
      if verbose:
        print 'Searching Google Maps for %s...' % (tmpquery)
      lloc = gmaps.local_search(tmpquery)

      # Parse query results
      lres = lloc['responseData']['results'][0]
      geoinfo['lat'] = float(lres['lat'])
      geoinfo['lon'] = float(lres['lng'])

      # Break if success
      break

    except GoogleMapsError as gme:
      
      print 'GoogleMapsError: %s' % (repr(gme))
      if delay:
        time.sleep(waittime)
      
      # Try again
      continue
    
    except:
      
      # Continue with next query
      pass
    
    if len(splitquery) > 1:

      # Run next query
      splitquery = splitquery[1:]

    else:

      # No terms remaining
      break

  # Get final query
  geoinfo['final'] = tmpquery
  geoinfo['nfinal'] = len(splitquery)
  
  # Return
  return geoinfo
