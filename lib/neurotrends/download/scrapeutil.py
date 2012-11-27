# Import built-in modules
import re

# Import project modules
from util import *
from mechtools import *
from verpdf import *

def shortredir(br, tgt):
  
  # Get URL
  url = br.geturl()

  # Redirect if short url
  if re.search('\.short$', url, re.I):
    longurl = re.sub('\.short$', '.%s' % (tgt), url)
    br.open(longurl)
    return True
  
  # Return false
  return False

def absredir(br, tgt):
  
  # Get URL
  url = br.geturl()
  
  # Redirect if /doi/abs/
  if re.search('\/doi\/abs\/\d+', url, re.I):
    fullurl = re.sub('\/abs\/', '/%s/' % (tgt), url)
    br.open(fullurl)
    return True
  
  # Return false
  return False

def checkmeta(doctype, br, soup=None):

  # Quit if not soup
  if not soup:
    html, soup = br2docs(br)
    if not soup:
      return False
  
  # Get settings
  if doctype == 'html':
    metarules = [
      {'name' : 'citation_fulltext_html_url'},
      {'name' : 'DC.relation', 'content' : re.compile('html')},
    ]
    verfun = lambda br: not verpdf(br)
  elif doctype == 'pdf':
    metarules = [
      {'name' : 'citation_pdf_url'},
      {'name' : 'DC.relation', 'content' : re.compile('\.pdf$')},
    ]
    verfun = verpdf

  # Find meta tag
  for rule in metarules:
    meta = soup.find('meta', rule)
    if meta:
      break
  
  # Follow meta content
  if meta:

    print 'Redirecting to content from meta tag: %s...' % \
      (urlclean(meta['content']))

    # Load meta URL using Browser.follow_link
    # Works for JAMA Network articles
    try:
      br.follow_link(mechanize.Link(
        base_url=br.geturl(), url=meta['content'], 
        text='', tag='', attrs=()
      ))
      # Return True if verified
      if verfun(br):
        return True
    except:
      pass
    
    # Load meta URL using Browser.open()
    # Works for most articles
    try:
      br.open(urlclean(meta['content']))
      # Return True if verified
      if verfun(br):
        return True
    except:
      pass
  
  # Couldn't find document
  return False
