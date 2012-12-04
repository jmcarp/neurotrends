# Import modules
import time

# Import project modules
from trenddb import *

def toart(art):
  """
  Convert PubMed ID or Article to Article
  Arguments:
    art (str/Article): PubMed ID or Article object
  """
  
  # Convert PubMed ID to Article
  if type(art) in [str, unicode]:
    return session.query(Article).filter_by(pmid=art).one()
  
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
