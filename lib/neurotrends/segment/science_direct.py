# Imports
import re
import json

# External imports
from BeautifulSoup import BeautifulSoup as BS

# Extract tocJson variable from ScienceDirect <script> tag
toc_re = re.compile('tocjson\s+=\s+\'(.*?)\';\n', re.I)

# Patterns for methods section titles
methods_patterns = [
  re.compile(pattern, re.I) for pattern in [
    'methods',
    'materials',
  ]
]

def extract_methods(html):
  
  # Get Table of Contents JSON from HTML
  toc_match = toc_re.search(html)
  if toc_match:
    toc_json = toc_match.groups()[0]
    try:
      toc = json.loads(toc_json)
    except:
      return
  
  # Get ToC sections
  sections = [sect for sect in toc['TOC']]
  
  # Get indices of sections matching methods patterns
  methods_idx = [
    idx for idx in range(len(toc['TOC']))
    if any([pattern.search(sections[idx]['sT']) for pattern in methods_patterns])
  ]
  if methods_idx:
    methods_idx = methods_idx[0]
  else:
    return
  
  # Get HTML IDs of methods section and following section
  methods_id = sections[methods_idx]['sID']
  next_idx = methods_idx + 1
  next_id = sections[next_idx]['sID']
  
  # Parse HTML
  soup = BS(html)
  
  # Find methods section
  methods_html = soup.find(id=methods_id)
  if not methods_html:
    return
  
  # Initialize methods text
  methods_text = ''
  methods_generator = methods_html.nextSiblingGenerator()
  
  # Iterate over methods siblings until we hit next section
  for elm in methods_generator:
    if hasattr(elm, 'get') and elm.get('id') == next_id:
      break
    if hasattr(elm, 'findAll'):
      methods_text += ' ' + ' '.join(elm.findAll(text=True))
    else:
      methods_text += ' ' + elm.string
  
  # Return
  return methods_text
