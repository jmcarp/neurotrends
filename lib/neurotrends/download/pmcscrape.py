from pubsearch import *

pmc_base_url = 'http://www.ncbi.nlm.nih.gov/pmc/articles/pmid'

def pmc_scrape(br, pmid):
  '''
  Point Browser to PMC full text.
  '''
  
  pmc_url = '%s/%s' % (pmc_base_url, pmid)

  br.open(pmc_url)
  html = br.response().read()
  
  if re.search('ipmc11', html, re.I):
    raise('Bad PMC link')
