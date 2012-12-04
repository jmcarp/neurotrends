# -*- coding: latin-1 -*-

# Import libraries
import re
import time
import urllib

# Set up Google Maps
from googlemaps import GoogleMaps
from googlemaps import GoogleMapsError
gmaps = GoogleMaps()

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

inststr = ['university', 'college']
institutes = ['university', 'college', 'hospital']
instptn = [re.compile(ptn, re.I) for ptn in inststr]

depts = [
  'journalism',
  'communication',
  'psychology',
  'neuroscience',
]

wikibase = 'http://en.wikipedia.org/wiki'
wikinotfound = 'wikipedia does not have an article with this exact name'
wikinocaps = ['of', 'for',]
wikiskipchar = [u'\xa0']
wikiskipptn = '[' + ''.join(wikiskipchar) + ']*'

# Adapted from http://stackoverflow.com/questions/10852955/python-batch-convert-gps-positions-to-lat-lon-decimals
direct_mult = {'N':-1, 'S':1, 'E': -1, 'W':1}
def get_coords(old):
    new = old.replace(u'\xb0',' ')\
      .replace(u'\u2032',' ')\
      .replace(u'\u2033',' ')
    new = new.split()
    new_dir = new.pop()
    new = [float(num) for num in new]
    new.extend([0, 0, 0])
    return (new[0] + new[1] / 60.0 + new[2] / 3600.0) * direct_mult[new_dir]

def anymatch(patterns, text, flags=re.I):
  return any([re.search(pattern, text, flags) for pattern in patterns])

def wikiparse(query, verbose=False):
  
  split_query = geoprep(query)
  clean_query = []
  for part in split_query:
    if anymatch(['center'], part) and anymatch(institutes, query):
      continue
    if anymatch(depts, part):
      continue
    clean_query.append(part)

  while clean_query:
    _ = clean_query.pop()
    join_query = ', '.join(clean_query)
    if verbose:
      print 'Searching Wikipedia for %s...' % (join_query)
    wikiinfo = wikilookup(join_query)
    if wikiinfo:
      return join_query, wikiinfo

  return

def wikilookup(query):
  
  # Capitalize query terms
  query_parts = query.lower().split(' ')
  for partidx in range(len(query_parts)):
    part = query_parts[partidx]
    if part not in wikinocaps:
      query_parts[partidx] = part.capitalize()
  print 'hi', query_parts
  query_cap = ' '.join(query_parts)

  # Load Wikipedia
  wikiurl = '%s/%s' % (wikibase, urllib.quote(query_cap))
  print wikiurl
  try:
    br.open(wikiurl)
  except:
    return

  # Read browser
  html, soup = br2docs(br)

  # Quit if no results
  if re.search(wikinotfound, html, re.I):
    return
  
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
  loc = ', '.join(loclist)
  
  # Get coordinates
  latnum, lonnum = (0, 0)
  geospan = soup.find(
    'span',
    {'class' : re.compile('geo-dec')}
  )
  if geospan:
    geotext = geospan.string
    geocoord = geotext.split(' ')
    if len(geocoord) == 2:
      lat, lon = geocoord
      latnum = get_coords(lat)
      lonnum = get_coords(lon)
  
  return loc, latnum, lonnum

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
  splitquery = [sq for sq in splitquery if not re.search('department', sq, re.I)]

  # Return
  return splitquery

def geotag(splitquery, delay=False):
  
  # Initialize results
  lres = None
  lon = None; lat = None

  orig = ', '.join(splitquery)
  norig = len(splitquery)

  while True:
    
    # Build query
    tmpquery = ', '.join(splitquery)
    tmpquery = tmpquery.encode('utf-8', 'ignore')
    
    try:
      
      # Delay
      if delay:
        time.sleep(waittime)

      # Send Google Maps query
      lloc = gmaps.local_search(tmpquery)

      # Parse query results
      lres = lloc['responseData']['results'][0]
      lat = lres['lat']
      lon = lres['lng']

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

  # Return
  final = tmpquery
  nfinal = len(splitquery)
  return lon, lat, orig, norig, final, nfinal
