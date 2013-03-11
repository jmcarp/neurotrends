# Imports
import requests
import json
import re

xref_api_url = 'http://pmid2doi.labs.crossref.org/'

def pmid_doi(info):
  '''Use the CrossRef Labs API to convert between PMID and DOI.

  Arguments:
  info -- dictionary with optional pmid and doi keys; must include at least one

  Usage:
  > pmid_doi({'pmid' : '9990848'})
  {u'doi': u'10.1037/0033-2909.125.1.155', u'pmid': u'9990848'}
  > pmid_doi({'doi' : '10.1037/0033-2909.125.1.155'})
  {u'doi': u'10.1037/0033-2909.125.1.155', u'pmid': u'9990848'}

  '''
  
  # Quit if both PMID and DOI provided
  if 'pmid' in info and 'doi' in info:
    return info

  # Get known value
  if 'pmid' in info:
    known = info['pmid']
  elif 'doi' in info:
    known = info['doi']
  else:
    raise Exception('Must provide PMID or DOI value')

  # Look up value on CrossRef API
  lookup = requests.get(
    '%s/%s' % (xref_api_url, known),
    headers={'accept' : 'application/json'}
  )
  
  # Quit if DOI not found
  if re.search('unknown (doi|pmid)', lookup.text, re.I):
    return info
  
  # Parse JSON
  lookup_json = json.loads(lookup.text)
  
  # Return mapping
  return lookup_json['mapping']
