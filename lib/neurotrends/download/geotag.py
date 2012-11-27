# Import libraries
import re
import time

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
instptn = [re.compile(ptn, re.I) for ptn in inststr]

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
