#
import re
import tempfile

import pyPdf

#
from mechtools import *

def verpdf(br=None, resp=None):
  'Verify PDF'

  print 'Verifying PDF: %s...' % (br.geturl())

  # Load response if not given
  if not resp:
    resp = br.response().read()

  # Return if link broken
  if re.search('page not found', resp, re.I):
    return False

  # Write response to temporary file
  fh = tempfile.TemporaryFile()
  fh.write(resp)

  # Check PDF using pyPdf
  try:
    pdftmp = pyPdf.PdfFileReader(fh)
    return True
  except:
    pass
 
  # Check PDF using header
  if re.search('^%pdf', resp, re.I):
    return True

  # Fail
  return False
