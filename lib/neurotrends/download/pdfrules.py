# Import modules
import re
import tempfile

# Import external modules
from BeautifulSoup import BeautifulSoup as bs
import pyPdf

# Import project modules
from util import *
from mechtools import *
from htmlrules import htmlnature, htmlwk, htmlapa
from htmlrules import buildurl, sciredir, soupfollow
from verpdf import *
from scrapeutil import *

# PDF link patterns
pdfptns = [
  'pdf\s*\(?\d+\)? k',
  'pdf\s*\(?\d+(\.\d+)?\s*[km]b?\)?',
  '(full text.*?pdf)|(pdf.*?full text)', 
  'download\s+pdf', '(?<!\.)pdf', 'pdf',
  'begin manual download',
]

pdfposptn = ['download']
pdfnegptn = [
  'citation',
  #'pubcat',     # Avoid publisher info for Liebert Publishers
  'download publication list',   # Avoid publisher info for Liebert Publishers
]

def getpdflink(soup, ptns):
  
  for ptn in ptns:

    linktexts = soup.findAll(text=re.compile(ptn, re.I))
    linkobjs = [lt.findParent('a') for lt in linktexts if
      lt.findParent('a') and not re.search(
        '(masthead)(editorial.*?board)|(media kit)', 
        lt, re.I
      )]
    rellinkobjs = [lo for lo in linkobjs if 
      lo.has_key('rel') and re.search('view\-full\-text', lo['rel'], re.I)]

    if rellinkobjs:
      return rellinkobjs[0]['href']
    if linkobjs:
      return linkobjs[0]['href']
  
  # Fail
  return ''

imgaltptn = ['full text', 'you can view this text']
imgsrcptn = ['(?<!mmc_)(?<!icon_)pdf\.gif', 'pass\.jpg']

def pdfdown(br):
  '''Download PDF.'''
  
  # ScienceDirect redirect
  sciredir(br)

  # Get URL
  url = br.geturl()

  # Redirect if /doi/abs/
  if absredir(br, 'pdf'):
    return

  # Return if PDF
  if verpdf(br):
    return True
     
  # Parse HTML
  html, soup = br2docs(br)
  
  # Get PDF from meta tag
  if checkmeta('pdf', br, soup):
    return True

  # ScienceDirect redirect
  sciredir(br)
  if verpdf(br):
    return True

  # Try appending intermediate to URL
  # Works for some ScienceDirect PDFs
  url = br.geturl()
  br.open(url + '?intermediate=true')
  if verpdf(br):
    return True
  br.open(url)
  
  # Get PDF from image tag
  # Check alt attribute
  img = soup.find('img', 
    {'src' : lambda alt:
      type(alt) in [str, unicode] and any([re.search(ptn, alt, re.I) for ptn in imgaltptn])
    }
  )
  # Check src attribute
  if not img:
    img = soup.find('img', 
      {'src' : lambda src:
        type(src) in [str, unicode] and any([re.search(ptn, src, re.I) for ptn in imgsrcptn])
      }
    )
  if img:
    imglnk = img.findParent('a')
    if imglnk:
      pdflink = buildurl(url, imglnk['href'])
      try:
        br.open(pdflink)
        if verpdf(br):
          return True
      except:
        pass

  # Get PDF link
  pdflink = getpdflink(soup, pdfptns)
  if pdflink:

    # Build PDF link
    pdflink = buildurl(url, pdflink)

    try:
      # Open PDF link
      br.open(pdflink)
      # Return if PDF
      if verpdf(br):
        return True
    except:
      pass
      ## Return to original URL
      #if br.geturl() != url:
      #  br.open(url)
  
  html, soup = br2docs(br)

  # Get PDF from meta tag
  if checkmeta('pdf', br, soup):
    return True

  # Get PDF from iframe tag
  iframe = soup.findAll(re.compile('^i?frame$'))#, src=re.compile('\.pdf'))
  if iframe:
    for frame in iframe:
      try:
        # Open iframe link
        br.open(frame['src'])
        # Return if PDF
        if verpdf(br):
          return True
      except:
        pass
        ## Return to original URL
        #if br.geturl() != url:
        #  br.open(url)
  
  # Get PDF from download link
  soupfollow(br, pdfposptn, pdfnegptn)

  # Fail
  return False

def verpdf(br=None, resp=None):
  'Verify PDF'
  
  print 'Verifying PDF: %s...' % (br.geturl())

  # Load response if not given
  if not resp:
    resp = br.response().read()

  # Return if link broken
  if re.search('page not found', resp, re.I):
    return False

  # Write response to temporary file
  fh = tempfile.TemporaryFile()
  fh.write(resp)

  # Check PDF using pyPdf
  try:
    pdftmp = pyPdf.PdfFileReader(fh)
    return True
  except:
    pass
  
  # Check PDF using header
  if re.search('^%pdf', resp, re.I):
    return True

  # Fail
  return False

def pdfnature(br):

  htmlnature(br)
  try:
    br.follow_link(text_regex=re.compile('download pdf', re.I))
    return
  except:
    pass
  br.follow_link(text_regex=re.compile('pdf', re.I))

def pdfmedsci(br):
  
  html = br.response().read()
  freeloc = re.search('window\.location=\'(.*?)\'', html)
  if freeloc:
    freeext = freeloc.groups()[0]
    baseurl = '/'.join(br.geturl().split('/')[:-1])
    freeaddr = baseurl + '/' + freeext
    br.open(freeaddr)

def pdfama(br):

  url = br.geturl()
  url = re.sub('content\/full', 'reprint', url)
  url = url + '.pdf'
  br.open(url)

def pdffrontiers(br):

  # Parse HTML
  html, soup = br2docs(br)
  
  # Get URL components
  fid = re.search('var fileid = \'(\d+)\';', html, re.I).groups()[0]
  aid = re.search('var articleid = \'(\d+)\';', html, re.I).groups()[0]
  fn = re.search('var filename = \'(.*?)\';', html, re.I).groups()[0]

  # Build PDF link
  pdflink = 'http://www.frontiersin.org/Journal/DownloadFile.ashx' + \
    '?pdf=1&FileId=%s&articleId=%s&Version=1&ContentTypeId=21&FileName=%s' \
    % (fid, aid, fn)

  # Open PDF link
  br.open(pdflink)

def pdfwk(br):

  htmlwk(br)

  url = br.geturl()

  html = br.response().read()
  soup = bs(html)
  url0 = url.split('ovidweb')[0]
  
  # 
  frame = soup.find('iframe')
  if frame:
    br.open(frame['src'])
    return

  # 
  lnk = soup.find('a', id=re.compile('pdf', re.I));
  if lnk:
    urlpdf = url0 + lnk['href']
    br.open(urlpdf)
    soup = bs(br.response().read())
    frame = soup.find('iframe')
    if frame:
      br.open(frame['src'])
    return

  # 
  lnk = soup.find('a', id=re.compile('ftemail', re.I))
  if lnk:
    urlpdf = url0 + lnk['href']
    br.open(urlpdf)
    soup = bs(br.response().read())
    frame = soup.find('iframe')
    if frame:
      br.open(frame['src'])
    return

def pdfapa(br):
  
  htmlapa(br)

  url = br.geturl()
  pdfinfo = url.split('detail?')[-1]

  pdfurl = 'http://web.ebscohost.com.proxy.lib.umich.edu/ehost/pdfviewer/pdfviewer?' + pdfinfo
  br.open(pdfurl)

  html = br.response().read()
  soup = bs(html)

  embed = soup.find('embed', {'id' : re.compile('pdfembed', re.I)})
  if embed:
    pdflink = embed['src']
    pdflink = re.sub('&amp;', '&', pdflink)
    br.open(pdflink)

def pdfbioscience(br):
  
  # Parse HTML
  html, soup = br2docs(br)
  
  # Find frames
  frames = soup.findAll('frame')
  
  # Open 0th frame
  try:
    f0link = buildurl(br.geturl(), frames[0]['src'])
    br.open(f0link)
  except:
    pass
  
  # Pass to default PDF finder
  pdfdown(br)

def pdfpsyonl(br):

  url = br.geturl()
  soup = bs(br.response().read())

  lnk = soup.find('a', onclick=re.compile('downloadfile', re.I))
  js = lnk['onclick']
  jspart = re.search('(\/.*?\.pdf)', js, re.I).groups()[0]

  url0 = url.split('.org')[0] + '.org'
  urlpdf = url0 + jspart

  br.open(urlpdf)
