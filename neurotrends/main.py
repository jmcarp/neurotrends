# Imports
import os
import re
import sys
import shelve
import smtplib
from email.mime.text import MIMEText

from BeautifulSoup import UnicodeDammit

# Project imports
import neurotrends as nt
from neurotrends.acrobatch import acrobatch
from neurotrends.download import pubsearch
from neurotrends.download import pmid_doi
from neurotrends import trenddb
from neurotrends import trendpath
from neurotrends import tagxtract
#from neurotrends import tagplot
from neurotrends import xtract
from neurotrends import util
from neurotrends import logger
from neurotrends.geo import geotag, geotools

# Sciscrape imports
from sciscrape.scrapetools import scrape

# Password files
user_file = '/Users/jmcarp/private/ump'
mail_file = '/Users/jmcarp/private/gmp'

doc_types = ['html', 'pdf', 'pmc']
scrape_doc_types = ['html', 'pdf']

def add_doi_to_all():
    
    arts = nt.session.query(trenddb.Article).filter(trenddb.Article.doi == None)

    for art in arts:

        info = download.pmid_doi({'pmid' : art.pmid})
        if 'doi' in info:
            art.doi = info['doi']
        else:
            print 'No DOI found for PMID %s...' % (art.pmid)

    nt.session.commit()

def getartpath(art, attr, base):
    
    if not hasattr(art, attr):
        return

    path = '%s/%s' % (base, getattr(art, attr))
    if os.path.exists(path):
        return path

def pmidset(op):
    '''
    Do set operations on PMIDs.
    Args:
        op (str):
            extra: return PMIDs in database but not in query
            missing: return PMIDs in query but not in database
    '''

    # Get query PMIDs
    pmrecs = pubsearch.artsearch()
    pmids = [str(rec['pmid']) for rec in pmrecs]

    # Get article PMIDs
    arts = nt.session.query(trenddb.Article.pmid)
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
        art = util.toart(badid)
        for filetype in pathmap:
            filepath = getartpath(art, filetype, pathmap[filetype])
            if filepath:
                os.remove(filepath)
            nt.session.delete(art)
        # Save changes
        if idx and idx % commit_interval == 0:
            nt.session.commit()

    # Save changes
    nt.session.commit()

def update(pmids=[], ndelay=None, doc_types=doc_types, do_parse=True, overwrite=True):
    """Add articles to database. Get article info, location, 
    files, and meta-data.

    Args:
        pmids (list, optional): PubMed IDs of articles to add.
            If empty, add all missing articles
        ndelay (int/None): If len(pmids) > ndelay, add delay
            between articles
        overwrite (bool): Overwrite article info

    """
    
    # Set up scraper
    scraper = scrape.UMScrape(user_file=user_file)

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
        artdump(artobj.pmid, scraper, doc_types=doc_types, overwrite=overwrite)

        # Extract PDF text
        if 'pdf' in doc_types:
            xtract.artxtract(artobj, overwrite=overwrite)

        # Parse article
        if do_parse:
            parse = tagxtract.artparse(artobj, overwrite=overwrite)

def batchdump(overwrite=False):
    
    # Set up browser
    br = getbr()
    umlogin(br, userfile=userfile)
    
    artquery = nt.session.query(trenddb.Article).order_by(trenddb.Article.pmid)

    ct = 1
    nart = artquery.count()

    for art in artquery:
        
        # Update UM credentials
        if ct % 50 == 0:
            umlogin(br, userfile=userfile)

        print 'Working on article %d of %d...' % (ct, nart)

        artdump(art.pmid, br, overwrite=overwrite)

        ct += 1

def short_name(full_path):
    return os.path.split(full_path)[-1]

def artdump(art, scraper, doc_types, overwrite=False):
    '''

    '''
    
    # Get article object
    art = util.toart(art)
    
    # Get output files
    out_files = {}
    for doc_type in doc_types:
        out_files[doc_type] = util.file_path(art.pmid, doc_type, trendpath.file_dirs)
    
    # Return if all documents complete and not overwrite
    if all([os.path.exists(out_files[doc_type]) for doc_type in doc_types]) \
            and not overwrite:

        print 'Download already complete'

        # Ensure documents saved in database
        for doc_type in doc_types:
            setattr(art, '%sfile' % (doc_type), short_name(out_files[doc_type]))
         
        # Save changes
        nt.session.commit()
        
        # Quit
        return

    # Clear database fields
    art.puburl = None
    art.publisher = None

    # Clear file fields
    for doc_type in doc_types:
        setattr(art, '%sfile' % (doc_type), None)
    
    # Clear PDF fields
    art.pdfocr = None
    art.pdfdecrypt = None
    art.pdfdmethod = None

    # Clear validation fields
    art.htmlval = None
    art.pdfval = None
    
    # Download articles
    info = scraper.scrape(pmid=art.pmid, doi=art.doi)

    # Save documents
    save_dirs = dict([(k, trendpath.file_dirs[k]['base_path']) for k in trendpath.file_dirs])
    info.save(save_dirs=save_dirs, id_type='pmid')

    # Log details to database
    art.scrapestatus = info.pretty_status
    art.puburl = info.pub_link
    art.publisher = info.publisher
    
    # Log files to database
    for doc_type in info.docs:
        if out_files[doc_type]:
            setattr(art, '%sfile' % (doc_type), short_name(out_files[doc_type]))

    # Save changes
    nt.session.commit()

def buildart(art):

    print('Retrieving pmid %s...' % (art['pmid']))
    
    # Check for article in database
    artobj = nt.session.query(trenddb.Article).\
        filter(trenddb.Article.pmid==art['pmid']).first()
    
    # Return if complete
    if artobj and artobj.authors:
        print 'Article already complete.'
        return artobj
    
    # Get PubMed text
    if pubsearch.needsparam(art, artobj, 'xml'):
        fetchtxt = pubsearch.artfetch(art['pmid'])
        if fetchtxt:
            art['xml'] = pubsearch.UnicodeDammit(fetchtxt).unicode
        else:
            return

    # Parse PubMed XML
    art['soup'] = pubsearch.bs(art['xml'])
    art['info'] = pubsearch.artinfo(art)

    # Get article DOI
    if pubsearch.needsparam(art, artobj, 'doi'):
        # Try DOI from PubMed first
        doi = pubsearch.pmdoi(art)
        # If none, try CrossRef
        if not doi:
            doi = pubsearch.xrdoi(art)
        if doi:
            art['doi'] = pubsearch.parser.unescape(doi)

    # Get affiliation coordinates
    if pubsearch.needsparam(art, artobj, ['affil', 'lat', 'lng', 'gtquery', 'gtlen']):
        art['affil'] = art['info']['affil']
    
    # Add titles
    art['atitle'] = art['info']['atitle']
    art['jtitle'] = art['info']['jtitle']

    # Get publication date
    if pubsearch.needsparam(art, artobj, ['pubyear', 'pubmonth', 'pubday']):
        art['pubyear'] = art['info']['pubyear']
        art['pubmonth'] = art['info']['pubmonth']
        art['pubday'] = art['info']['pubday']

    # Delete unused fields
    del art['soup']; del art['info']

    # Update database
    if artobj:
        print 'Updating database...'
        pubsearch.artupdate(artobj, art, overwrite=True)
    else:
        print 'Adding entry to database...'
        artobj = trenddb.Article(**art)
        nt.session.add(artobj)

    # Add authors
    addauths(artobj)

    # Save changes
    nt.session.commit()

    # Return
    return artobj

def batchaddauths():
    """
    Add authors to all articles
    """

    # Get articles
    arts = nt.session.query(trenddb.Article).order_by(trenddb.Article.pmid)

    # Add authors
    for artidx in range(arts.count()):
        art = arts[artidx]
        print 'Working on article #%s, PMID %s...' % (artidx, art.pmid)
        addauths(art)
        if artidx and artidx % 50 == 0:
            nt.session.commit()

    # Save changes
    nt.session.commit()

def addauths(art, commit=False):
    """
    Add authors to an article
    """

    info = ''

    if type(art) == dict:
        if 'info' in art and art['info']:
            info = art['info']
        elif 'xml' in art and art['xml']:
            info = pubsearch.artinfo(art)
        artobj = nt.session.query(trenddb.Article).filter(trenddb.Article.pmid==art['pmid']).first()
    else:
        artobj = util.toart(art)
        info = pubsearch.artinfo({'xml' : artobj.xml})

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
            authobj = nt.session.query(trenddb.Author).\
                filter(trenddb.and_(
                    trenddb.Author.lastname==last, trenddb.Author.frstname==frst
                )).first()
            
            # Create if it doesn't exist
            if not authobj:
                authobj = trenddb.Author(lastname=last, frstname=frst)
                nt.session.add(authobj)

            # Append to article
            if authobj not in art.authors:
                art.authors.append(authobj)

    # Save changes
    if commit:
        nt.session.commit()

def batchaddplace():
    """
    Add place information to all articles
    """

    # Get articles
    arts = nt.session.query(trenddb.Article).order_by(trenddb.Article.pmid)
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
    nt.session.commit()

def addplace(art, overwrite=False, delay=True, commit=True):
    """
    Add place information to an article
    Arguments:
        art (str/trenddb.Article): PubMed ID or trenddb.Article object
        overwrite (bool): Overwrite existing files?
        delay (bool): Wait between requests?
        commit (bool): Save changes to database?
    """

    # Get article object
    art = util.toart(art)

    # Return if place exists
    if art.place:
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
    prepsplit = geotools.geo_prep(art.affil)
    prepquery = ', '.join(prepsplit)

    # Check for existing place object
    qplace = nt.session.query(trenddb.Place).\
        filter(trenddb.Place.orig==prepquery)

    placeobj = None

    if qplace.count() == 1 and not overwrite:

        placeobj = qplace.first()

    else:
        
        # Geotag affiliation string
        locinfo = geotag.geotag(art.affil)

        if 'lat' in locinfo and locinfo['lat'] or \
             'lon' in locinfo and locinfo['lon']:
            # Check for existing Place
            if 'head' in locinfo:
                qplace = nt.session.query(trenddb.Place).\
                    filter(trenddb.Place.wikiname == locinfo['head'])
        if qplace.count() == 1 and not overwrite:

            placeobj = qplace.first()

        else:
            
            # Quit if no coordinates
            if 'lat' not in locinfo or not locinfo['lat'] or \
                 'lon' not in locinfo or not locinfo['lon']:
                return

            placeobj = trenddb.Place()

            # Add Wikipedia info
            if 'head' in locinfo:
                placeobj.wikiname = locinfo['head']
            if 'loc' in locinfo:
                placeobj.wikiloc = locinfo['loc']

            if 'lat' in locinfo and locinfo['lat'] and \
                 'lon' in locinfo and locinfo['lon']:

                orig = UnicodeDammit(locinfo['orig_query']).unicode
                final = UnicodeDammit(locinfo['final_query']).unicode

                placeobj.lon = locinfo['lon']
                placeobj.lat = locinfo['lat']
                placeobj.orig = orig
                placeobj.norig = locinfo['orig_n_parts']
                placeobj.final = final
                placeobj.nfinal = locinfo['final_n_parts']

    # Attach to article object
    if placeobj.lon and placeobj.lat:
        art.place = placeobj

    # Save changes
    if commit:
        nt.session.commit()

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
        mail_info = open(mail_file, 'r').readlines()
        user = mail_info[0].strip()
        addr = '%s@gmail.com' % (user)
        pw = mail_info[1].strip()
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
