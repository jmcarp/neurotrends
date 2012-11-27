# Import modules
import os, re, sys
import time, random
import urllib

from BeautifulSoup import BeautifulSoup as bs
from BeautifulSoup import UnicodeDammit
import HTMLParser
parser = HTMLParser.HTMLParser()
from toascii import toascii

# Set up BioPython
from Bio import Entrez
Entrez.email = 'jm.carp@gmail.com'

# Import project modules
from geotag import *
from util import *

query = \
  '(' + \
    '"fmri"' + \
    ' OR "functional mri"' + \
    ' OR "functional magnetic resonance imaging"' + \
  ')' + \
  ' AND humans[MH]' + \
  ' AND "magnetic resonance imaging"[MH]' + \
  ' AND (' + \
    '"psychological phenomena and processes"[MH]' + \
    ' OR "behavior and behavior mechanisms"[MH]' + \
  ')' + \
  ' AND english[LA]'

def artsearch(query, verbose=True):

  if verbose:
    print('Searching terms %s...\n', (query))

  srchnd = retry(Entrez.esearch, 5, 5, db='pubmed', retmax=999999, term=query)
  srcrec = retry(Entrez.read, 5, 5, srchnd)
  arts = [{'pmid' : int(pmid)} for pmid in srcrec['IdList']]
  
  if verbose:
    print('Search returned %d articles' % (len(arts)))

  return arts

def artfetch(pmid):
  
  try:
    txthnd = retry(Entrez.efetch, 5, 5, \
      db='pubmed', retmode='xml', id=pmid)
    txtrec = txthnd.read()
    return txtrec
  except:
    return

def pmdoi(art):
  'Get DOI from PubMed.'
  
  if not art['soup']:
    return

  doitag = art['soup'].find('articleid', {'idtype': 'doi'})
  if doitag:
    doitxt = str(doitag.text)
    return doitxt

  return

def xrdoi(art):
  'Get DOI from CrossRef.'
  
  if 'info' not in art:
    return
  
  # Get article title
  try:
    atitle = art['info']['atitle']
    atitle = urllib.quote(atitle)
  except:
    return

  # Get author surname
  try:
    aulast = art['info']['auths'][0].split(',')[0]
    aulast = toascii(aulast)
    aulast = urllib.quote(aulast)
  except:
    return
  if not aulast:
    return

  # Build query URL
  xrurl = 'http://www.crossref.org/openurl/?' + \
    'pid=jm.carp@gmail.com&noredirect=true' + \
    '&atitle=' + atitle + \
    '&aulast=' + aulast

  # Load XML
  h = urllib.urlopen(xrurl)
  xml = h.read()
  soup = bs(xml)

  # Extract DOI
  doitag = soup.find('doi')
  if doitag and doitag.string:
    return doitag.string

  # Fail
  return

def artinfo(art):
  
  if not art['xml']:
    return None
 
  artsoup = bs(art['xml'])
  info = {}
  
  # Get abstract
  abstxt = artsoup.find(re.compile('abstracttext', re.I))
  if abstxt:
    info['abstxt'] = abstxt.string
  else:
    info['abstxt'] = None

  # Get journal title
  try:
    jtitle = artsoup.find('journal').find('title')
    info['jtitle'] = unicode(jtitle.string)
  except:
    info['jtitle'] = None

  # Get article title
  atitle = artsoup.find(re.compile('article\-*title'))
  info['atitle'] = ''.join(atitle.findAll(text=True))
 
  # Get keywords
  kwds = artsoup.findAll('kwd')
  info['kwds'] = [unicode(kwd.string) for kwd in kwds]

  # Get grants
  grants = artsoup.findAll('grant')
  info['grants'] = [unicode(grant.find('grantid').string) for grant in grants \
    if grant.find('grantid') and grant.find('grantid').string]
  info['sponsors'] = [grant.find('agency').string for grant in grants \
    if grant.find('agency') and grant.find('agency').string]
  for sponidx in range(len(info['sponsors'])):
    info['sponsors'][sponidx] = re.sub('\s*NIH\s*', '', info['sponsors'][sponidx])
    info['sponsors'][sponidx] = re.sub('\s*HHS\s*', '', info['sponsors'][sponidx])

  # Get publication date
  pdate = artsoup.find(re.compile('pubdate', re.I))
  if pdate:
    info['pmonth'] = [unicode(m.string) for m in pdate.findAll(re.compile('month', re.I)) if m.string]
    info['pyear'] = [unicode(y.string) for y in pdate.findAll(re.compile('year', re.I)) if y.string]
  else:
    info['pmonth'] = None
    info['pyear'] = None

  pubdate = artsoup.find(re.compile('pubmedpubdate', re.I), {'pubstatus' : 'pubmed'})
  if pubdate:
    info['pubday'] = pubdate.find('day').text
    info['pubmonth'] = pubdate.find('month').text
    info['pubyear'] = pubdate.find('year').text
  else:
    info['pubday'] = None
    info['pubmonth'] = None
    info['pubyear'] = None
  
  # Get page limits
  info['fpage'] = None; info['lpage'] = None
  page = artsoup.find('medlinepgn')
  if page:
    pages = page.string.split('-')
    ndf = len(pages[0])
    info['fpage'] = pages[0]
    if len(pages) > 1:
      ndl = len(pages[1])
      info['lpage'] = pages[0][:ndf-ndl] + pages[1]

  # Get authors
  authlist = []
  auths = artsoup.findAll('author')
  for auth in auths:
    authstr = ''
    last = auth.find('lastname')
    frst = auth.find('forename')
    if last and last.string:
      authstr = last.string
      if frst and frst.string:
        authstr += ', ' + frst.string
    if last and last.string and frst and frst.string:
      authlist.append([last.string, frst.string])
    #authlist.append(authstr)
  info['auths'] = authlist
  
  # Get affiliation
  affil = artsoup.find('affiliation')
  if affil and affil.string:
    info['affil'] = affil.string
  else:
    info['affil'] = None
 
  return info

def artupdate(dbobj, artdict, overwrite=False):
  
  for field in artdict:
    if overwrite or \
        (not hasattr(dbobj, field) or \
        not getattr(dbobj, field)):
      setattr(dbobj, field, artdict[field])

def artcollect(src, maxct=250):
  
  # Search for articles
  arts = artsearch(src)

  # Exclude articles beyond cutoff
  arts = arts[:maxct]
  
  # Initialize article list
  artobjs = []
  
  # Loop over articles
  for artidx in range(len(arts)):

    # Print progress
    print 'Working on article #%d of %d...' % (artidx + 1, len(arts))

    # Create article object
    art = buildart(arts[artidx])

    # Add to list
    if art:
      artobjs.append(art)
  
  # Return
  return artobjs

def needsparam(dictobj, dbobj, params):
  '''
  Check whether article is missing parameters.
  '''

  if type(params) != list:
    params = [params]
  
  if not dbobj:
    return True
  
  need = False
  for param in params:
    if hasattr(dbobj, param):
      val = getattr(dbobj, param)
      if val:
        dictobj[param] = val
      else:
        need = True
    else:
      need = True

  return need
