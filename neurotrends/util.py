# Imports
import time
from BeautifulSoup import UnicodeDammit

# Project imports
import neurotrends as nt
from neurotrends import trenddb
#from trenddb import *
from trendpath import *

def short_name(full_path):
    return os.path.split(full_path)[-1]

def file_path(pmid, file_type, file_info):
    return '%s/%s.%s' % (
        file_info[file_type]['base_path'],
        pmid,
        file_info[file_type]['file_ext']
    )

def to_unicode(s):
    return UnicodeDammit(s).unicode

def toart(art):
    '''
    Convert PubMed ID or Article to Article
    Arguments:
        art (str/Article): PubMed ID or Article object
    '''
    
    # Convert PubMed ID to Article
    if type(art) in [str, unicode]:
        return nt.session.query(trenddb.Article).\
            filter_by(pmid=art).\
            one()
    
    # Return Article
    return art

def urlclean(url):

    url = url.replace('&lt;', '<')
    url = url.replace('&gt;', '>')
    url = url.replace(' ', '%20')

    return url

def retry(f, ntry, delay, *args, **kwargs):
    """
    Retry a function
    Arguments:
        f (function): Function to retry
        ntry (int): Max number of tries
        delay (number): Delay between tries
        args (list): Function arguments
        kwargs (dict): Function keyword arguments
    """

    for tryidx in range(ntry - 1):
        try:
            return f(*args, **kwargs)
        except Exception, e:
            print 'Exception: %s; retrying in %ds...' % (str(e), delay)
            time.sleep(delay)
    return f(*args, **kwargs)
