# Import built-in modules
import os
import sys
import shelve
import smtplib
from email.mime.text import MIMEText

# Import project modules
from download.pubsearch import *
from download.artscrape import *
from acrobatch.acrobatch import *
from trendpath import *
from tagxtract import *
from tagplot import *
from logger import *

## Set up database
#session = getdb()

# Password files
userfile = '/Users/jmcarp/private/ump'
mailfile = '/Users/jmcarp/private/gmp'

def getartpath(art, attr, base):
  
  if not hasattr(art, attr):
    return

  path = '%s/%s' % (base, getattr(art, attr))
  if os.path.exists(path):
    return path

pathmap = {
  'htmlfile' : htmldir,
  'chtmlfile' : chtmldir,
  'pdfrawfile' : pdfdir,
  'pdftxtfile' : pdftxtdir,
}

def pmidset(op):
  """
  Do set operations on PMIDs.
  Args:
    op (str):
      extra: return PMIDs in database but not in query
      missing: return PMIDs in query but not in database
  """

  # Get query PMIDs
  pmrecs = artsearch(query)
  pmids = [str(rec['pmid']) for rec in pmrecs]

  # Get article PMIDs
  arts = session.query(Article.pmid)
  artids = [pmid[0] for pmid in arts]

  if op == 'extra':
    return list(set(artids) - set(pmids))
  if op == 'missing':
    return list(set(pmids) - set(artids))

def prune(commit_interval=50):
  """
  Delete Article entries and associated files for articles
  not in the current PubMed query.
  Args:
    commit_interval (int): how often to commit changes
  """
  
  badids = pmidset('extra')
  print 'Pruning %d extra articles...' % (len(badids))
  
  # Delete bad articles
  for idx in range(len(badids)):
    badid = badids[idx]
    art = toart(badid)
    for filetype in pathmap:
      filepath = getartpath(art, filetype, pathmap[filetype])
      if filepath:
        os.remove(filepath)
      session.delete(art)
    # Save changes
    if idx and idx % commit_interval == 0:
      session.commit()

  # Save changes
  session.commit()

def update(pmids=[], ndelay=None, overwrite=True):
  """
  Add articles to database. Get article info, location, 
  files, and meta-data.
  Args:
    pmids (list, optional): PubMed IDs of articles to add.
      If empty, add all missing articles
    ndelay (int/None): If len(pmids) > ndelay, add delay
      between articles
    overwrite (bool): Overwrite article info
  """
  
  # Set up browser
  br = getbr()
  umlogin(br, userfile=userfile)

  # Get new articles
  if not pmids:
    pmids = pmidset('missing')#newarts(query)

  # Get Google Maps delay
  narts = len(pmids)
  delay = ndelay is not None and narts > ndelay

  # Loop over articles
  for artidx in range(narts):
    
    pmid = pmids[artidx]
    artdict = {'pmid' : pmid}
    print 'Working on article %d of %d, PMID %s...' % \
      (artidx + 1, narts, pmid)
    
    # Create article object
    artobj = buildart(artdict)

    # Get place information
    addplace(artobj, delay=delay)

    # Get HTML and PDF
    artdump(artobj.pmid, br, overwrite=overwrite)

    # Extract PDF text
    artxtract(artobj, overwrite=overwrite)

    # Parse article
    parse = artparse(artobj, overwrite=overwrite)

# TODO: is this function still needed?
def filecheck():
  
  arts = session.query(Article).order_by(Article.pmid).all()
  
  for artidx in range(len(arts)):

    art = arts[artidx]
    
    #print 'Working on article %d of %d...' % (artidx + 1, len(arts))

    # 
    htmlfile = '%s/html/%s.html' % (dumpdir, art.pmid)
    pdfrawfile = '%s/pdf/%s.pdf' % (dumpdir, art.pmid)
    
    if os.path.exists(htmlfile):
      art.htmlfile = os.path.split(htmlfile)[-1]
      html = ''.join(open(htmlfile, 'r').readlines())
      if verpdf(resp=html):
        print 'bad html on file %s' % (htmlfile)
        art.htmlfile = None

    if os.path.exists(pdfrawfile):
      art.pdfrawfile = os.path.split(pdfrawfile)[-1]

  session.commit()

def batchdump(overwrite=False):
  
  # Set up browser
  br = getbr()
  umlogin(br, userfile=userfile)
  
  artquery = session.query(Article).order_by(Article.pmid)

  ct = 1
  nart = artquery.count()

  for art in artquery:
    
    # Update UM credentials
    if ct % 50 == 0:
      umlogin(br, userfile=userfile)

    print 'Working on article %d of %d...' % (ct, nart)

    artdump(art.pmid, br, overwrite=overwrite)

    ct += 1

def artdump(art, br, overwrite=False):
  """
  Download HTML and PDF documents for an article.
  """
  
  # Get article object
  art = toart(art)

  # 
  htmlfile = '%s/html/%s.html' % (dumpdir, art.pmid)
  chtmlfile = '%s/chtml/%s.shelf' % (dumpdir, art.pmid)
  pdfrawfile = '%s/pdf/%s.pdf' % (dumpdir, art.pmid)
  
  # Return if article complete
  if \
      os.path.exists(htmlfile) \
      and os.path.exists(pdfrawfile) \
      and not overwrite:
    art.htmlfile = os.path.split(htmlfile)[-1]
    art.pdfrawfile = os.path.split(pdfrawfile)[-1]
    print 'Download already complete'
    session.commit()
    return

  # Return if PDF complete and HTML terminally unavailable
  if \
      os.path.exists(pdfrawfile) \
      and art.scrapestatus \
      and re.search('no html full text', art.scrapestatus) \
      and not overwrite:
    art.htmlfile = None
    art.pdfrawfile = os.path.split(pdfrawfile)[-1]
    print 'Download already complete; HTML not available'
    session.commit()
    return
    
  # Clear fields
  art.puburl = None
  art.htmlfile = None
  art.pdfrawfile = None
  art.pdfocr = None
  art.pdfdecrypt = None
  art.pdfdmethod = None
  art.htmlmeth = None
  art.pdfmeth = None
  art.htmlval = None
  art.pdfval = None

  try:
    status, puburl, outhtml, outrawpdf, htmlmeth, pdfmeth = pmid2file(
      art.pmid, br, outhtml=htmlfile, outpdf=pdfrawfile, doi=art.doi
    )
    art.scrapestatus = status
    art.puburl = puburl
    if outhtml:
      art.htmlfile = os.path.split(outhtml)[-1]
    if outrawpdf:
      art.pdfrawfile = os.path.split(outrawpdf)[-1]
    art.htmlmeth = htmlmeth.__name__
    art.pdfmeth = pdfmeth.__name__
  except Exception as exc:
    print exc
    art.scrapestatus = exc.message
    
  # Save changes
  session.commit()

def buildart(art):

  print('Retrieving pmid %s...' % (art['pmid']))
  
  # Check for article in database
  artobj = session.query(Article).\
    filter(Article.pmid==art['pmid']).first()
  
  # Return if complete
  if artobj and artobj.authors:
    print 'Article already complete.'
    return artobj
  
  # Get PubMed text
  if needsparam(art, artobj, 'xml'):
    fetchtxt = artfetch(art['pmid'])
    if fetchtxt:
      art['xml'] = UnicodeDammit(fetchtxt).unicode
    else:
      return

  # Parse PubMed XML
  art['soup'] = bs(art['xml'])
  art['info'] = artinfo(art)

  # Get article DOI
  if needsparam(art, artobj, 'doi'):
    # Try DOI from PubMed first
    doi = pmdoi(art)
    # If none, try CrossRef
    if not doi:
      doi = xrdoi(art)
    if doi:
      art['doi'] = parser.unescape(doi)

  # Get affiliation coordinates
  if needsparam(art, artobj, ['affil', 'lat', 'lng', 'gtquery', 'gtlen']):
    art['affil'] = art['info']['affil']
  
  # Add titles
  art['atitle'] = art['info']['atitle']
  art['jtitle'] = art['info']['jtitle']

  # Get publication date
  if needsparam(art, artobj, ['pubyear', 'pubmonth', 'pubday']):
    art['pubyear'] = art['info']['pubyear']
    art['pubmonth'] = art['info']['pubmonth']
    art['pubday'] = art['info']['pubday']

  # Delete unused fields
  del art['soup']; del art['info']

  # Update database
  if artobj:
    print 'Updating database...'
    artupdate(artobj, art, overwrite=True)
  else:
    print 'Adding entry to database...'
    artobj = Article(**art)
    session.add(artobj)

  # Add authors
  addauths(artobj)

  # Save changes
  session.commit()

  # Return
  return artobj

def batchaddauths():
  """
  Add authors to all articles
  """

  # Get articles
  arts = session.query(Article).order_by(Article.pmid)

  # Add authors
  for art in arts:
    addauths(art)

  # Save changes
  session.commit()

def addauths(art, commit=False):
  """
  Add authors to an article
  """

  info = ''

  if type(art) == dict:
    if 'info' in art and art['info']:
      info = art['info']
    elif 'xml' in art and art['xml']:
      info = artinfo(art)
    artobj = session.query(Article).filter(Article.pmid==art['pmid']).first()
  else:
    artobj = toart(art)
    info = artinfo({'xml' : artobj.xml})

  if not info or not artobj:
    return

  for auth in info['auths']:

    last = auth[0]
    frst = auth[1]

    if last and frst:

      # Clean up first name
      frst = re.sub('\-', ' ', frst)
      frst = re.sub('[^A-Z\s]', '', frst)

      # Get author object
      authobj = session.query(Author).\
        filter(and_(Author.lastname==last, Author.frstname==frst)).first()

      # Create if it doesn't exist
      if not authobj:
        authobj = Author(lastname=last, frstname=frst)
        session.add(authobj)

      # Append to article
      if authobj not in art.authors:
        art.authors.append(authobj)

  # Save changes
  if commit:
    session.commit()

def batchaddplace():
  """
  Add place information to all articles
  """

  # Get articles
  arts = session.query(Article).order_by(Article.pmid)
  narts = arts.count()

  # Loop over articles
  for artidx in range(narts):

    print 'Working on article #%d of %d...' % (artidx + 1, narts)

    art = arts[artidx]

    # Save progress on multiples of 50
    commit = artidx % 50 == 0

    # Get place information
    addplace(art, commit=commit)

  # Save changes
  session.commit()

def addplace(art, overwrite=False, delay=True, commit=True):
  """
  Add place information to an article
  Arguments:
    art (str/Article): PubMed ID or Article object
    overwrite (bool): Overwrite existing files?
    delay (bool): Wait between requests?
    commit (bool): Save changes to database?
  """

  # Get article object
  artobj = toart(art)

  # Return if place exists
  if artobj.place:
    sys.stdout.write('Article place already completed. ')
    if not overwrite:
      print 'Quitting...'
      return
    print 'Overwriting...'

  # Return if not article affiliation
  if not art.affil:
    print 'Article affiliation missing. Quitting...'
    return

  # Prepare geotag query
  prepsplit = geoprep(art.affil)
  prepquery = ', '.join(prepsplit)

  # Check for existing place object
  qplace = session.query(Place).filter(Place.orig==prepquery)

  if qplace.count() > 0:
    placeobj = qplace.first()
  else:
    placeobj = Place()

  if qplace.count() == 0 or overwrite:

    # Get coordinates
    lon, lat, orig, norig, final, nfinal = geotag(prepsplit, delay=delay)

    if lon and lat:

      orig = UnicodeDammit(orig).unicode
      final = UnicodeDammit(final).unicode

      placeobj.lon = lon
      placeobj.lat = lat
      placeobj.orig = orig
      placeobj.norig = norig
      placeobj.final = final
      placeobj.nfinal = nfinal

  # Attach to article object
  if placeobj.lon and placeobj.lat:
    artobj.place = placeobj

  # Save changes
  if commit:
    session.commit()

xskip = [
  '19135072',   # Crashes on extraction
  '18442810',   # Crashes on extraction
]

def batchxtract():
  """
  Extract PDF text from all articles
  """
  
  # Set up browser
  br = getbr()
  umlogin(br, userfile=userfile)

  arts = session.query(Article).order_by(Article.pubyear.desc())

  ct = 1
  nart = arts.count()

  for art in arts:
    
    if art.pmid in xskip:
      print 'Skipping article %d...' % (ct)
    else:
      print 'Working on article %d of %d...' % (ct, nart)
      artxtract(art, br=br)
    ct += 1

def artxtract(art, br=None, commit=True, totiff=False, overwrite=False):
  """
  Extract PDF text from an article
  """
  
  # Stop if no PDF in record
  if not art.pdfrawfile:
    art.pdftxtfile = None
    if commit:
      session.commit()
    return

  # Retry download if PDF missing
  if not os.path.exists('%s/%s' % (pdfdir, art.pdfrawfile)):
    print 'Retrying download...'
    artdump(art.pmid, br)
    art = toart(art)
    if not art.pdfrawfile:
      return

  print 'Working on article %s...' % (art.pmid)

  pdftxtfile = '%s/pdftxt/%s.shelf' % (dumpdir, art.pmid)
  if os.path.exists(pdftxtfile):
    shelf = shelve.open(pdftxtfile)
    if isinstance(shelf, shelve.Shelf) \
        and 'pdfinfo' in shelf \
        and shelf['pdfinfo']['txt'] \
        and not overwrite:
      print 'File already exists'
      return
    else:
      os.remove(pdftxtfile)

  # Read PDF
  pdfinfo = pdfread('%s/%s' % (pdfdir, art.pdfrawfile), totiff=totiff)
  if not pdfinfo:
    return

  # Write text to file
  shelf = shelve.open(pdftxtfile)
  shelf['pdfinfo'] = pdfinfo

  # Update article
  art.pdftxtfile = os.path.split(pdftxtfile)[-1]
  art.pdfocr = pdfinfo['ocr']
  art.pdfdecrypt = pdfinfo['decrypt']
  art.pdfdmethod = pdfinfo['dmethod']
  
  # Save changes
  if commit:
    session.commit()

if __name__ == '__main__':

  if len(sys.argv) > 1 and sys.argv[1] == 'update':

    # Set up logging
    log = Logger(filepath=logdir)
    sys.stdout = log

    # Run update
    try:
      update()
    except Exception, err:
      print 'Error:', str(err)

    # Close log
    log.close()
    sys.stdout = log.terminal

    # Set up email server
    mailinfo = open(mailfile, 'r').readlines()
    user = mailinfo[0].strip()
    addr = '%s@gmail.com' % (user)
    pw = mailinfo[1].strip()
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    
    # Build message
    msg = MIMEText(open(log.filename, 'r').read())
    msg['To'] = addr
    msg['From'] = addr
    msg['Subject'] = 'fmri-trends update'
    server.login(user, pw)
    
    # Send email
    try:
      server.sendmail(addr, addr, msg.as_string())
    finally:
      server.quit()
