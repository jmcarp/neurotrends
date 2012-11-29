# Import built-in modules
import os, re
import copy
import time
import shelve

# Import external modules
from BeautifulSoup import BeautifulSoup as BS
from BeautifulSoup import UnicodeDammit
from sqlalchemy.orm.exc import MultipleResultsFound
import lxml.html

# Set up HTML parser
import HTMLParser
parser = HTMLParser.HTMLParser()

# Import project modules
from trendpath import *
from trenddb import *
from util import *

## Set up database
#session = getdb()

# Import sub-project modules
from download.pubsearch import *
from pattern import tags

# Import fmri-report
import sys
sys.path.append('/Users/jmcarp/Dropbox/projects/fmri-report/scripts')
import reportproc as rp

repchars = [
  ('- ', '-'),
  (u'\u2013', '-'),
  ('[\'\"\xa2\xa9\xae\x03]', ''),
  ('[\s\xa0]+', ' '),
]

repxcept = {
  'dept' : [
    ('[\'\"\xa2\xa9\xa3\x03]', ''),
    repchars[-1]
  ],
  'field' : [
    ('[\'\"\xa2\xa9\xa3\x03]', ''),
    repchars[-1]
  ],
}

#############
# Functions #
#############

def batchclearattrib(usereport=False):
  
  if not usereport:

    # Clear tables
    session.query(Attrib).delete()
    session.query(Field).delete()
    session.query(Snippet).delete()
   
    # Hack to clear association tables
    session.execute('DELETE from articles_attribs')
    session.execute('DELETE from attribs_fields')
  
  else:

    arts = getreparts()
    for art in arts:
      clearattrib(toart(art), commit=False)

  session.commit()

def clearattrib(art, commit=True):
  
  art.attribs = []

  if commit:
    session.commit()

def cleantxt(txt, ptns):
  
  ctxt = txt

  for ptn in ptns:
    ctxt = re.sub(ptn[0], ptn[1], ctxt)

  return ctxt

def getreparts():

  report = rp.ezread()
  arts = [art['pmid'] for art in report 
    if session.query(Article).filter(Article.pmid == art['pmid']).count()]
  return arts

def batchartparse(usereport=False, groups=[]):
  
  if usereport:
    arts = getreparts()
  else:
    arts = session.query(Article).all()

  for artidx in range(len(arts)):
    
    print 'Working on article %d of %d...' % (artidx + 1, len(arts))
    commit = artidx % 100 == 0
    artparse(arts[artidx], commit, groups=groups)

  # Save changes
  session.commit()

def artverify(art, html='', pdf=''):

  # Cast article to Article
  art = toart(art)

  # Get article info
  info = artinfo({'xml' : art.xml})

  # Quit if no abstract
  if info['abstxt'] is None:
    return None, None

  # Tokenize abstract
  abstxt = info['abstxt']
  abswords = re.split('\s+', abstxt)
  abswords = [word.lower() for word in abswords]

  # Ignore punctuation
  for char in ['.', ',', ';', ':']:
    abswords = [word.strip(char) for word in abswords]

  # Load HTML
  if not html:
    html = loadhtml(art, overwrite=True)#, raw=True)
  
  # Load PDF
  if not pdf:
    pdf = loadpdf(art)
    pdf = UnicodeDammit(pdf).unicode

  html = html.lower()
  pdf = pdf.lower()

  # Check HTML
  if html:
    htmlwords = [word for word in abswords if html.find(word) > -1]
    htmlprop = float(len(htmlwords)) / len(abswords)
  else:
    htmlprop = None

  # Check PDF
  if pdf:
    pdfwords = [word for word in abswords if pdf.find(word) > -1]
    pdfprop = float(len(pdfwords)) / len(abswords)
  else:
    pdfprop = None

  # Return
  return htmlprop, pdfprop

def loadhtml(art, overwrite=False, method='lxml', raw=False, verbose=False):
  
  artobj = toart(art)
  htmltxt = ''

  htmlfile = '%s/%s.html' % (htmldir, artobj.pmid)
  chtmlfile = '%s/%s.shelf' % (chtmldir, artobj.pmid)

  if overwrite and os.path.exists(chtmlfile):
    os.remove(chtmlfile)

  if artobj.htmlfile:

    if os.path.exists(chtmlfile) \
        and not overwrite \
        and not raw:

      # Load clean HTML
      chtml = shelve.open(chtmlfile)
      htmltxt = chtml['txt']

      # Done
      if verbose:
        print 'Finished loading HTML...'

    elif os.path.exists(htmlfile):
      
      # Convert to plain text
      html = ''.join(open(htmlfile, 'r').readlines())
      
      # 
      if raw:
        return html
      
      # 
      try:
        htmltxt = parsehtml(html, method=method)
      except:
        return ''

      htmltxt = UnicodeDammit(htmltxt).unicode
      htmltxt = parser.unescape(htmltxt)

      # Save clean HTML
      chtml = shelve.open(chtmlfile)
      chtml['txt'] = htmltxt
      chtml.close()

      # Done
      if verbose:
        print 'Finished reading HTML...'

  return htmltxt

def loadpdf(art, verbose=False):

  artobj = toart(art)
  pdftxt = ''

  if artobj.pdftxtfile:

    pdffile = '%s/%s' % (pdftxtdir, artobj.pdftxtfile)

    if os.path.exists(pdffile):
      
      s = shelve.open(pdffile)
      pdftxt = s['pdfinfo']['txt']
      ## Convert to plain text
      #pdftxt = pdfjoin(pdffile)
      #pdftxt = UnicodeDammit(pdftxt).unicode
      
      # Done
      if verbose:
        print 'Finished reading PDF...'

  return pdftxt

def artparse(art, commit=True, overwrite=False, verify=True, 
    groups=[], verbose=False):
  
  # Find article
  artobj = toart(art)
  
  # Initialize docs
  docs = []

  # Read HTML file
  htmltxt = loadhtml(artobj, overwrite=overwrite, verbose=verbose)

  # Read PDF text file
  pdftxt = loadpdf(artobj, verbose=verbose)
  
  # Verify documents
  if verify:
    htmlprop, pdfprop = artverify(artobj, htmltxt, pdftxt)
    artobj.htmlval = htmlprop
    artobj.pdfval = pdfprop
    verhtml = htmlprop is None or htmlprop >= 0.85
    verpdf = pdfprop is None or pdfprop >= 0.85
  else:
    verhtml = True
    verpdf = True
  
  # Add HTML document
  if htmltxt and verhtml:
    docs.append(htmltxt)

  # Add PDF document
  if pdftxt and verpdf:
    docs.append(pdftxt)
  
  # Quit if no docs
  if not docs:
    return

  # Process docs
  if groups:
    procsrc = dict([(group, tags[group]) for group in groups])
  else:
    procsrc = tags

  taggroups = procdocs(docs, procsrc)

  for groupname in taggroups:
    
    taggroup = taggroups[groupname]

    if not taggroup:
      continue

    for tag in taggroup['tags']:

      attobj = []

      # Build Attrib query
      attq = session.query(Attrib)
      conq = []
      foundfield = True
      fields = {}
      for field in tag:
        fieldname = groupname + field
        fieldvalue = tag[field]
        try:
          fieldobj = session.query(Field).\
            filter(
              and_(
                Field.name == fieldname, 
                Field.value == fieldvalue
              )
            ).one()
        except MultipleResultsFound, e:
          print e
          raise
        except:
          fieldobj = Field(name=fieldname, value=fieldvalue)
          session.add(fieldobj)
          foundfield = False
        fields[fieldname] = fieldobj
        if foundfield:
          conq.append(Attrib.fields.contains(fieldobj))
      if conq and foundfield:
        attq = session.query(Attrib).filter(conq[0])
        for con in conq[1:]:
          attq = attq.intersect(session.query(Attrib).filter(con))
        attobj = attq.first()

      # Create Attrib if needed
      if not attobj:
        attobj = Attrib(
          name=groupname,
          category=taggroup['cat'],
          fields=fields
        )
      
      # Add Attrib to Article
      if attobj not in artobj.attribs:
        artobj.attribs.append(attobj)
      
      # Add snippets
      for sniptxt in taggroup['snippets']:
        if not sniptxt:
          continue
        exsnip = [snipobj for snipobj in artobj.snippets
          if snipobj.name == groupname 
          and snipobj.text == sniptxt
        ]
        if not any(exsnip):
          artobj.snippets.append(Snippet(name=groupname, text=sniptxt))
  
  # Save changes
  if commit:
    session.commit()

  # Return tags
  return taggroups

def pdfjoin(pdffile):
  
  # Read PDF
  pdflines = open(pdffile, 'r').readlines()

  # Join PDF lines
  pdftxt = ''
  for line in pdflines:
    if line.endswith('-'):
      pdftxt += line[:-1]
    else:
      pdftxt += line + ' '
  
  # Return
  return pdftxt
  
def parsehtml(html, method='soup'):
  
  if method == 'soup':

    # Parse HTML
    soup = BS(html)

    # Remove <script> elements
    [el.extract() for el in soup.findAll('script')]

    # Assemble text
    txt = ''.join(soup.findAll(text=True))

  elif method == 'lxml':
    
    # Parse HTML
    parse = lxml.html.fromstring(html)

    # Extract text
    txt = parse.text_content()

  # Return text
  return txt

def unique(list):
  
  ulist = []
  for item in list:
    if item not in ulist:
      ulist.append(item)

  return ulist

def procdocs(docs, tags):
  
  tagsum = {}

  for src in tags:

    taglist = []
    snippets = []
    
    # Process documents
    for doc in docs:
      doctags, docsnips = txt2tag(doc, tags[src]['src'], verbose=False)
      taglist.extend(doctags)
      snippets.extend(docsnips)

    # Remove duplicate tags
    taglist = unique(taglist)

    # Remove unversioned tags if versioned tags present
    # Reverse index list to allow deletions
    for tagidx in reversed(range(len(taglist))):
      tag = taglist[tagidx]
      if 'ver' not in tag or not tag['ver']:
        if any([vtag for vtag in taglist if vtag['name'] == tag['name'] and 'ver' in vtag and vtag['ver']]):
          del(taglist[tagidx])

    # 
    tagsum[src] = {
      'cat' : tags[src]['cat'],
      'tags' : taglist,
      'snippets' : snippets,
    }

  return tagsum

def txt2tag(txt, src, verbose=True):
  
  # Initialize
  taglist = []
  snippets = []
  
  # Apply default clean pattern
  deftxt = cleantxt(txt, repchars)

  for tag in src:
    
    # Check for non-default clean pattern
    if tag in repxcept:
      srctxt = cleantxt(txt, repxcept[tag])
    else:
      srctxt = deftxt
    
    foundtag = False
    foundknownver = False
    foundarbitver = False

    # Get tag pattern
    if type(src[tag]) == dict:
      tagptn = src[tag]['bool']
    elif type(src[tag]) in [list, type(lambda x: x)]:
      tagptn = src[tag]
    else:
      raise Exception('Error: pattern must be a dict, list, or function')

    # Search for tag
    vals = []
    for ptn in tagptn:
      ruleres = ptn.apply(srctxt)
      #ruleres = ptn(srctxt)
      #ruleres = applyrule(ptn, srctxt)
      for val, snip in ruleres:
        if val:
          foundtag = True
          vals.append(val)
          snippets.append(snip)
          if verbose:
            print 'Found tag %s with context %s' % (tag, snip)
    
    # Stop if tag not found
    if not foundtag:
      continue
    
    # 
    if type(val) != bool:
      for val in vals:
        if type(val) == dict:
          val.update({'name' : tag})
          taglist.append(val)
        else:
          taglist.append({'name' : tag, 'value' : val})
      continue

    # Stop if no version info
    if type(src[tag]) != dict:
      taglist.append({'name' : tag})
      continue
    
    # Extract version (known)
    for ver in src[tag]:
      if ver in ['bool', 'arbit']:
        continue
      verptn = src[tag][ver]
      for ptn in verptn:
        #if any([res[0] for res in ptn(srctxt)]):
        if any([res[0] for res in ptn.apply(srctxt)]):
          taglist.append({'name' : tag, 'ver' : ver})
          foundknownver = True
      #if any([flexsearch(ptn, srctxt) for ptn in verptn]):
      #  taglist.append({'name' : tag, 'ver' : ver})
      #  foundknownver = True

    # Extract version (arbitrary)
    if not foundknownver:
      if 'arbit' in src[tag]:
        # Initialize arbitrary function with identity
        arbfun = lambda x: x
        if type(src[tag]['arbit']) == dict:
          arblist = src[tag]['arbit']['src']
          if 'fun' in src[tag]['arbit']:
            arbfun = src[tag]['arbit']['fun']
        else:
          arblist = src[tag]['arbit']
        for arbptn in arblist:
          arbres = arbptn.apply(srctxt)
          #arbres = arbptn(srctxt)
          #arbres = flexsearch(arbptn, srctxt, fun=re.findall)
          if arbres:
            arbver = [res for res in arbres if res][0]
            if type(arbver) == tuple:
              arbver = [res for res in arbver if res][0]
            if arbver:
              taglist.append({'name' : tag, 'ver' : arbfun(arbver)})
              foundarbitver = True

    if not (foundknownver or foundarbitver):
      taglist.append({'name' : tag, 'ver' : ''})

  return taglist, snippets
