# Import modules
import re
import time
import urlparse

# Import external moules
from BeautifulSoup import BeautifulSoup as bs

# Import project modules
from util import *
from mechtools import *
from scrapeutil import *

htmlposptn = [
  'html', 
  'full[\s\-]*text', 
  'read[\s\-]*online', 
  'free article',
]
htmlnegptn = [
  'media kit',                  # 
  'free article:[\w\s]+',       # Avoid promos on Taylor and Francis
  'abstract/free full text',    # Avoid citations on Journal of Neuroscience
]
htmlnegrules = [
  # Avoid citations on MIT Press
  lambda a: a.has_key('class') and 
    bool(re.search('(?<!\w)ref(?!\w)', a['class'], re.I)),
  # Avoid citations on MIT Press
  lambda a: a.has_key('href') and 
    bool(re.search('validator\.w3\.org', a['href'], re.I)),
  # Avoid "Related Documents" on Springer
  lambda a: bool(
    a.findParent('div', 
      {'class' : re.compile('scroll-pane')}
    )
  ),
]

def sciredir(br):
  
  # Initialize redir to False
  redir = False

  # Get current URL
  url = br.geturl()

  html, soup = br2docs(br)

  # Redirect if ScienceDirect LinkingHub
  if re.search('linkinghub', url) or re.search('redirecttoscienceurl', html, re.I):
    
    # Initialize article ID
    artid = None

    # Try hidden input
    hidden = soup.find(
      'input',
      {'id' : re.compile('sciencedirecturl', re.I)}
    )
    if hidden and hidden.has_key('value'):
      longurl = hidden['value']
      # Redirect to link if PDF
      if re.search('\.pdf$', url, re.I):
        br.open(longurl)
        return True
      # Otherwise extract article ID
      urlpars = urlparse.parse_qs(longurl)
      if '_piikey' in urlpars:
        artid = urlpars['_piikey'][0]
    
    # Check URL for article ID
    if not artid:

      # Get ScienceDirect article ID
      artid = url.split('/')[-1]
      artid = re.sub('[\-\(\)]', '', artid)

    # Get ScienceDirect URL
    sdurl = 'http://www.sciencedirect.com.proxy.lib.umich.edu/science/article/pii/%s' % (artid)
  
    # Redirect to ScienceDirect URL
    # May require several attempts
    print 'Redirecting to Science Direct URL: %s...' % (sdurl)
    for redirct in range(5):
      try:
        br.open(sdurl)
      except:
        redir = False
        break
      if br.geturl() == sdurl:
        redir = True
        break
  
  # Return to starting URL if fail
  if not redir:
    br.open(url)

  # Return
  return redir

def buildurl(baseurl, newurl):
  
  newurlclean = re.sub('[\s]', '', newurl)
  baseurlsplit = re.split('(?<!\/)\/(?!\/)', baseurl)
  
  urlptn = ['^http', '^www', '\.com', '\.org', '\.net', '\.edu']
  if any([re.search(ptn, newurlclean, re.I) for ptn in urlptn]):
    return newurlclean

  if newurlclean.startswith('/'):
    urlparts = [baseurlsplit[0], newurlclean.strip('/')]
  elif newurlclean.find('?') > -1:
    urlparts = []
    for part in baseurlsplit:
      if part.startswith('?'):
        break
      urlparts.append(part)
    urlparts += [newurlclean]
  else:
    urlparts = baseurlsplit[:-1] + [newurlclean.strip('/')]

  return '/'.join(urlparts)

def tostd(br, soup=None):
  
  # 
  if not soup:
    html, soup = br2docs(br)

  # 
  stdview = soup.find(text=re.compile('switch to standard view', re.I))
  if stdview:
    stdlink = stdview.findParent('a')
    if stdlink and stdlink.has_key('href'):
      br.open(buildurl(br.geturl(), stdlink['href']))

def htmlfollow(br):
  
  url = br.geturl()
  
  # Done if long url
  if re.search('\.long$', url, re.I):
    return
  
  # Redirect if short url
  if shortredir(br, 'long'):
    return
  
  # Redirect if /doi/abs/
  if absredir(br, 'full'):
    return
  
  # 
  if sciredir(br):
    tostd(br)
    return
  
  html, soup = br2docs(br)
  
  # Get HTML from meta tag
  if checkmeta('html', br, soup):
    sciredir(br)
    tostd(br)
    return True
  
  # Get full text from image tag
  imgsrcptn = [
    'xml\.gif',
    'bt_vedi_html\.gif',
  ]
  img = soup.find('img', 
    {'src' : lambda src: type(src) in [str, unicode] and 
      any([re.search(ptn, src, re.I) for ptn in imgsrcptn])}
  )
  
  if img:
    imglnk = img.findParent('a')
    if imglnk:
      htmllink = buildurl(url, imglnk['href'])
      try:
        br.open(htmllink)
        return
      except:
        br.open(url)
  
  # Find full text link
  soupfollow(br, htmlposptn, htmlnegptn, negrules=htmlnegrules)
  tostd(br)

def soupfollow(br, posptn, negptn, negrules=None, soup=None):
  
  if not soup:
    html, soup = br2docs(br)
    if not soup:
      return False
  
  # Get starting URL
  url = br.geturl()

  # Find links
  links = soup.findAll('a')
  links = [link for link in links if 
    link.has_key('href') and link['href']]

  # Loop over links
  for pos in posptn:

    # Find links matching positive pattern
    poslinks = [link for link in links if 
      re.search(pos, link.text, re.I)]
      
    # Loop over positive links
    for link in poslinks:

      # Find links not matching negative patterns
      if not any([re.search(neg, link.text, re.I) 
          for neg in negptn]):
        
        # Apply negative rules
        if negrules:
          if any([rule(link) for rule in negrules]):
            continue

        # Build full URL
        fullurl = buildurl(url, link['href'])
        print 'hi', fullurl
        try:
          # Open full URL
          br.open(fullurl)
          # Succeed
          return True
        except:
          pass
  
  # Fail
  return False

def htmlpass(br):
  
  sciredir(br)
  #pass

def htmlnature(br):
  
  html, soup = br2docs(br)
  #html = br.response().read()
  if re.search('this article appears in:', html, re.I | re.S):
    #soup = bs(html)
    reflink = soup.find('a', {'class' : re.compile('articletext', re.I)})
    if reflink:
      refurl = 'http://www.nature.com' + reflink['href']
      br.open(refurl)

def htmlapa(br):

  url = br.geturl()
  urlend = url.split('journals/')[-1]
  urlend = urlend.strip('/')
  apaid = 'AN %s' % (urlend.replace('/', '-'))

  br.open('http://www.lib.umich.edu/database/link/27957')

  br.select_form(nr=0)
  br['ctl00$ctl00$FindField$FindField$ctl00$guidedFields$fieldRepeater$ctl01$SearchTerm'] = apaid
  br.submit(type='submit')

  br.follow_link(url_regex=re.compile('viewarticle', re.I))

def htmlwk(br):
  
  url = br.geturl()
  urlqry = url.split('?')[-1]
  urlpar = dict(urlparse.parse_qsl(urlqry))

  ovidbase = 'http://ovidsp.ovid.com/ovidweb.cgi?' + \
    'T=JS&MODE=ovid&NEWS=n&PAGE=fulltext&D=ovft&SEARCH='

  if 'an' in urlpar:
    urlovid = '%s%s.an.' % \
      (ovidbase, urlpar['an'])
  else:
    urlovid = '%s%s.is+and+%s.vo+and+%s.ip+and+%s.pg.' % \
      (ovidbase, urlpar['issn'], urlpar['volume'],
      urlpar['issue'], urlpar['spage'])

  br.open(urlovid)

def htmlrsc(br):

  html, soup = br2docs(br)
  #s = bs(br.response().read())
  m = soup.find('meta', content=re.compile('articlehtml'))
  br.open(m['content'])

def htmlfrontiers(br):

  url = br.geturl()
  url = re.sub('abstract$', 'full', url)
  br.open(url)

