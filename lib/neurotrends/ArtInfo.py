
class ArtInfo(object):
  
  def __init__(self, artSQA=None, pmid=None):
    if artSQA is not None:
      self.artSQA = artSQA
    elif pmid is not None:
      self.artSQA = session.query(Article)\
        .filter(Article.pmid == pmid)\
        .one()
    self._doc_cache = {}

  def load_doc(self, doc_type):
    
    # Check cache
    if doc_type in self._doc_cache and self._doc_cache[doc_type]:
      return self._doc_cache[doc_type]
    
    # Read document
    if doc_type == 'html':
      doc_txt = self._load_html()
    elif doc_type == 'pdf':
      doc_txt = self._load_pdf()
    elif doc_type == 'pmc':
      doc_txt = self._load_pmc()
    else:
      raise Exception('Document type %s not implemented' % (doc_type))

    # Update cache
    self._doc_cache[doc_type] = doc_txt

    return doc_txt

  def _load_pdf(self):
    
    pdftxt = ''
    pdftxtfile = file_path(self.artSQA.pmid, 'pdftxt', file_dirs)

    if self.artSQA.pdftxtfile and os.path.exists(pdftxtfile):
        
      s = shelve.open(pdftxtfile)
      pdftxt = s['pdfinfo']['txt']

      # Update cache
      self._doc_cache['pdf'] = pdftxt
    
    return pdftxt

  def _load_html(self, method='lxml'):

    txt = ''
    htmlfile = file_path(art.pmid, 'html', file_dirs)

    if self.artSQA.htmlfile and os.path.exists(htmlfile):

      # Convert to plain text
      html = ''.join(open(htmlfile, 'r').readlines())
      
      # Pad TDs
      html = re.sub(
        '<td(.*?)>(.*?)</td>', 
        '<td\\1> \\2 </td>', 
        html, 
        flags=re.I
      )
      
      try:
        txt = ArtInfo._parse_html(html, method=method)
      except:
        return ''

      txt = to_unicode(txt)
      txt = parser.unescape(txt)

    return txt
  
  @staticmethod
  def _parse_html(html, method='soup'):
    
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

  def _load_pmc(self, method='soup'):
      
    pmcfile = file_path(self.artSQA.pmid, 'pmc', file_dirs)
    
    html = ''

    if self.artSQA.pmcfile and os.path.exists(pmcfile):

      html = ''.join(open(pmcfile, 'r').readlines())
      try:
        html = parsehtml(html, method=method)
      except:
        return ''

      html = to_unicode(html)
      html = parser.unescape(html)

    return html
