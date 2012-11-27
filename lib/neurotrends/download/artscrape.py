
# Import libraries
import time
import os, re, sys

# Set timeout for Browser objects
import socket
socket.setdefaulttimeout(60)

from BeautifulSoup import BeautifulSoup as bs

# Import internal libraries
from mechtools import *
from htmlrules import *
from pdfrules import *
from journalinfo import *
from util import *

# 
pmbase = 'http://www.ncbi.nlm.nih.gov/pubmed'
doibase = 'http://dx.doi.org'

def brdump(br, outname):
  
  if outname:
    fh = open(outname, 'w')
    fh.write(br.response().read())
    fh.close()

def getpmlink(pmid, br):
  
  pmurl = '%s/%s' % (pmbase, pmid)
  br.open(pmurl)

  html, soup = br2docs(br)

  pmlink = soup.find('a', title=re.compile('^full text', re.I))
  try:
    return pmlink['href']
  except:
    raise Exception('no puburl from pubmed')

def libproxy(br):
  
  url = br.geturl()

  liburl = url
  liberror = None

  # Redirect through UM proxy
  if re.search('medscimonit', url, re.I):
    liburl = url
  else:
    try:
      if re.search('^(?:http|https|ftp)//:', url):
        prefix = 'http://'
      else:
        prefix = ''
      liburl = 'http://proxy.lib.umich.edu/login?url=%s%s' % (prefix, url)
      br.open(liburl)
    except:
      liburl = url
      liberror = 'error on library proxy'

  return liburl, liberror
  
access_fail_ptn = [
  'why don\'t i have access',
  'we do not have a current subscription for your institution in our system',
  'sign in via athens',
  'add this item to your shopping cart',
  'your action has resulted in an error',
  'this item requires a subscription',        
  'if you have a sciencedirect username',     # ScienceDirect
  'access to this content is restricted',     # SpringerLink
  'pdf-preview\.axd',                         # SpringerLink
  'name="citedBySection"',                    # JoCN
  'full content is available to subscribers', # JAMA Network
  'you do not have access to this article',   # Taylor and Francis
  'how to purchase access',                   # Informa
  'purchase this article',                    # TheClinics.com
  'options for accessing this content',       # Wiley
  'access to this resource is secured',       # IOS Press
  'javascript:addToCart\(\d+\)',              # BenthamDirect
  'eurekaselect\.com\/cart',                  # EurekaSelect
  'pdf / purchase',                           # Pulsus
  'purchase multiple prints',                 # Pulsus
  'proceed to payment',                       # Neurology India
  'you have requested the following',         # Liebert Publishers
  'the requested article is not ' + \
    'currently available',                    # Various
  'the doi handle you entered is invalid'     # Bad DOI
  'logowanie',                                # Polish for <login>
  'i wish to purchase the article',           # Minerva Medica
  'paywalllightbox',                          # De Gruyter
]

access_success_ptn = [
  'identitieswelcome',                        # 
]

def wileyrule(html, soup):
  
  # Check for Wiley publication tag
  wileypub = False
  pub = soup.find('meta', {'name' : re.compile('citation_publisher')})
  if pub and pub.has_key('content'):
    if re.search('wiley', pub['content'], re.I):
      wileypub = True
  
  # Check for full text link
  fulllink = False
  fulltext = soup.find('meta', 
    {'name' : re.compile('citation_fulltext_html_url')}
  )
  if fulltext and fulltext.has_key('content'):
    fulllink = True

  # Return True if Wiley publication without full text
  if wileypub and not fulllink:
    return True
  
  # Return False otherwise
  return False

accessrule = {
  'html' : [
    wileyrule,
  ],
  'pdf' : [],
}

def repdump(dtype, fun, br, verfun=None, ntry=5, wtime=5, nftime=600):
  
  url = br.geturl()
  ct = 0
  
  while ct < ntry:

    if ct > 0:
      print 'Attempt #%d...' % (ct + 1)
      time.sleep(wt)
      br.open(url)

    try:
      
      # Parse browser state
      html, soup = br2docs(br)
      
      # Check for journal main page
      if re.search('viewing items \d+[-\s]+\d+', html, re.I):
        raise Exception('wk: cannot locate')

      # Apply function
      fun(br)
      
      # Parse browser state
      html, soup = br2docs(br)

      # Check for Wolters-Kluwer missing text
      if re.search('cannot get full text',
          html, re.I):
        raise Exception('wk: no full text')
      if re.search('the fulltext record could not be located',
          html, re.I):
        raise Exception('wk: cannot locate')

      # Check for generic missing text
      access_granted = False
      for ptn in access_success_ptn:
        if re.search(ptn, html, re.I):
          access_granted = True
      if not access_granted:
        for ptn in access_fail_ptn:
          if re.search(ptn, html, re.I):
            print 'accessfail', ptn
            raise Exception('no access')

      # Check for access
      if dtype == 'html':
        if any([rule(html, soup) for rule in accessrule['html']]):
          raise Exception('no access')
      elif dtype == 'pdf':
        if any([rule(html, soup) for rule in accessrule['pdf']]):
          raise Exception('no access')

      # Check for ScienceDirect missing text
      if re.search('sciencedirect', br.geturl()):
        svpar = soup.findAll('p', {'class' : re.compile('svarticle', re.I)})
        if not svpar:
          raise Exception('no access')

      # Check for PDF frame
      if dtype == 'html':
        pdfframe = soup.find(re.compile('^i?frame$'), 
          {'src' : re.compile('\.pdf', re.I)})
        if pdfframe:
          raise Exception('pdf frame')

      # Verify content
      if verfun and not verfun(br):
        raise Exception('verfail')
      
      # Success
      return

    except Exception as exc:
      if exc.message == 'wk: no full text':
        wt = nftime
      else:
        wt = wtime

    ct += 1

  raise exc

def pmid2file(pmid, br, outhtml=None, outpdf=None, doi=None):
  
  print 'Working on PMID %s...' % (pmid)
  
  status = []
  url = None
  pubopen = False
  
  ## Get publisher link from PubMed
  #try:
  #  url = retry(getpmlink, 5, 5, pmid, br)
  #except:
  #  status.append('no puburl from pubmed')
  #
  ## Open publisher link from PubMed
  #if url:
  #  try:
  #    retry(br.open, 5, 5, url)
  #    pubopen = True
  #  except:
  #    status.append('invalid puburl from pubmed')

  # Get publisher link from DOI
  #if not pubopen and doi:
  if doi:
    doiurl = '%s/%s' % (doibase, doi)
    print 'Working on link %s...' % (doiurl)
    try:
      br.open(doiurl)
      url = br.geturl()
    except:
      status.append('invalid puburl from doi')
      #url = ''

  # Get publisher link from PubMed
  if not url:
    try:
      url = retry(getpmlink, 5, 5, pmid, br)
    except:
      status.append('no puburl from pubmed')
  
    # Open publisher link from PubMed
    if url:
      try:
        retry(br.open, 5, 5, url)
        #pubopen = True
      except:
        status.append('invalid puburl from pubmed')

  # No valid link
  if not url:
    status.append('fail')
    status.reverse()
    return '; '.join(status), '', '', ''
  
  # Delete existing output files
  if os.path.exists(outhtml):
    os.remove(outhtml)
  if os.path.exists(outpdf):
    os.remove(outpdf)
  
  # 
  liburl, liberror = libproxy(br)
  if liberror:
    status.append(liberror)

  # Get defaults
  htmlmeth = htmldefault
  pdfmeth = pdfdefault
  
  # Get publisher rules
  foundinfo = False
  for ji in journalinfo:
    if journalinfo[ji]['rule'](liburl):
      if 'htmlmeth' in journalinfo[ji]:
        htmlmeth = journalinfo[ji]['htmlmeth']
      if 'pdfmeth' in journalinfo[ji]:
        pdfmeth = journalinfo[ji]['pdfmeth']
      foundinfo = True
      break
  
  # Download HTML
  if outhtml and htmlmeth:
    try:
      repdump('html', htmlmeth, br, verfun=lambda br: not verpdf(br))
      brdump(br, outhtml)
    except:
      status.append('error on html: %s' % (repr(sys.exc_info()[1])))
      outhtml = None
  
  # Refresh
  br.open(liburl)
  
  # Download PDF
  print 'Working on PDF...'
  if outpdf and pdfmeth:
    try:
      repdump('pdf', pdfmeth, br, verfun=verpdf)
      brdump(br, outpdf)
    except:
      status.append('error on pdf: %s' % (repr(sys.exc_info()[1])))
      outpdf = None
  
  status.reverse()
  if not status:
    status = ['success']
  return '; '.join(status), url, outhtml, outpdf
