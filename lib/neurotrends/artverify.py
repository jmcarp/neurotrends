def artverify(art, html='', pdf=''):
  
  # Cast article to Article
  art = toart(art)
  
  # Get article info
  info = artinfo({'xml' : art.xml})

  # Quit if no abstract
  if info['abstxt'] is None:
    return None, None
  
  # Tokenize abstract
  abstxt = info['abstxt']
  abswords = re.split('\s+', abstxt)
  abswords = [word.lower() for word in abswords]

  # Ignore punctuation
  for char in ['.', ',', ';', ':']:
    abswords = [word.strip(char) for word in abswords]

  # Load HTML
  if not html:
    html = loadhtml(art, overwrite=True)#, raw=True)
    html = html.lower()

  # Load PDF
  if not pdf:
    pdf = loadpdf(art)
    pdf = UnicodeDammit(pdf).unicode
    pdf = pdf.lower()
  
  # Check HTML
  if html:
    htmlwords = [word for word in abswords if html.find(word) > -1]
    htmlprop = float(len(htmlwords)) / len(abswords)
  else:
    htmlprop = None

  # Check PDF
  if pdf:
    pdfwords = [word for word in abswords if pdf.find(word) > -1]
    pdfprop = float(len(pdfwords)) / len(abswords)
  else:
    pdfprop = None
  
  # Return
  return htmlprop, pdfprop

def checkarts(arts):
  
  htmllist = []
  pdflist = []
  for artidx in range(arts.count()):
    print 'Working on article %d...' % (artidx + 1)
    htmlprop, pdfprop = artverify(arts[artidx])
    htmllist.append(htmlprop)
    pdflist.append(pdfprop)

  return htmllist, pdflist
