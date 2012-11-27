# Import modules
import time

# Import project modules
from trenddb import *

def toart(art):
  '''Convert article object or PMID to article object'''

  if type(art) in [str, unicode]:
    return session.query(Article).filter_by(pmid=art).one()
  return art

def urlclean(url):

  url = url.replace('&lt;', '<')
  url = url.replace('&gt;', '>')
  url = url.replace(' ', '%20')

  return url

def retry(f, ntry, delay, *args, **kwargs):

  for tryidx in range(ntry - 1):
    try:
      return f(*args, **kwargs)
    except Exception, e:
      print 'Exception: %s; retrying in %ds...' % (str(e), delay)
      time.sleep(delay)
  return f(*args, **kwargs)
