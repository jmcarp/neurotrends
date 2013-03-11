# Imports
import re

# External imports
from BeautifulSoup import BeautifulSoup as BS

highwire_patterns = [
  re.compile(pattern, re.I) for pattern in [
    'highwire\.stanford\.edu',
  ]
]

def is_highwire(html):
  
  return any([pattern.search(html) for pattern in highwire_patterns])

def extract_method(html):
  
  soup = BS(html)

  methods_section = soup.find({'class' : re.compile('methods-materials', re.I)})
  if not methods_section:
    return

  return ' '.join(methods_section.find(text=True))
