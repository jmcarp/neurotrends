# Import modules
import time

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
