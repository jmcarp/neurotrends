# Imports
import os
import shelve

# Project imports
import neurotrends as nt
from neurotrends import util
from neurotrends import trenddb
from neurotrends import trendpath

# Sciscrape imports
from sciscrape.pdftools import pdfx

# Parameters
min_pdf_length = 2500

# Article PMIDs to skip PDF extraction using acrobatch
xskip = [
    '19519639',     # Crashes on extraction
    '19135072',     # Crashes on extraction
    '18442810',     # Crashes on extraction
    '17280644',     # Crashes on extraction
]

def batchxtract():
    """
    Extract PDF text from all articles
    """
    
    # Set up browser
    br = getbr()
    umlogin(br, userfile=userfile)

    arts = nt.session.query(trenddb.Article).\
        order_by(trenddb.Article.pubyear.desc())

    ct = 1
    nart = arts.count()

    for art in arts:
        
        print 'Working on article %d of %d...' % (ct, nart)
        artxtract(art, br=br)
        ct += 1

def artxtract(art, scraper=None, commit=True, totiff=False, overwrite=False):
    '''
    Extract PDF text from an article
    '''
    
    # Stop if no PDF in record
    if not art.pdffile:
        art.pdftxtfile = None
        if commit:
            nt.session.commit()
        return

    # Retry download if PDF missing
    pdffile = util.file_path(art.pmid, 'pdf', trendpath.file_dirs)
    if not os.path.exists(pdffile) and scraper is not None:
        print 'Retrying download...'
        artdump(art.pmid, scraper)
        art = util.toart(art)
        if not art.pdffile:
            return

    print 'Working on article %s...' % (art.pmid)

    pdftxtfile = util.file_path(art.pmid, 'pdftxt', trendpath.file_dirs)
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

    # Initialize PDF info
    pdfinfo = None

    # Read PDF using PDFX
    if pdfinfo is None or 'txt' not in pdfinfo or len(pdfinfo['txt']) < min_pdf_length:

        print 'Reading PDF using pdfx...'

        qpdf = pdfx.PDFExtractor().extract(open(pdffile))
        if qpdf is not None:
            pdfinfo = {
                'txt' : qpdf.text(),
                'ocr' : False,
                'decrypt' : False,
                'dmethod' : None,
                'method' : 'pdfx',
            }

    # Read PDF using Acrobat
    if pdfinfo is None or 'txt' not in pdfinfo or len(pdfinfo['txt']) < min_pdf_length:
        
        # Stop if PMID in skip list
        if art.pmid in xskip:
            print 'Skipping article %s...' % (art.pmid)
            return

        print 'Reading PDF using acrobatch...'

        pdfinfo = acrobatch.pdfread(pdffile, totiff=totiff)

    # Quit if PDF was not parsed
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
        nt.session.commit()

