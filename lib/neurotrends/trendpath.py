# Import modules
import os
import re

# Home directory
homedir = '/Users/jmcarp/Dropbox/projects/fmri-software'

scriptdir = '%s/scripts' % (homedir)
datadir = '%s/data' % (homedir)
logdir = '%s/log' % (homedir)
figdir = '%s/fig' % (homedir)

# Base path to downloaded files
dumpdir = '/Users/jmcarp/Documents/artdump'

# Path to HTML files
htmldir = '%s/html' % (dumpdir)

# Path to cleaned HTML files
chtmldir = '%s/chtml' % (dumpdir)

# Path to raw PDF files
pdfdir = '%s/pdf' % (dumpdir)

# Path to extracted PDF files
pdftxtdir = '%s/pdftxt' % (dumpdir)

# Check directories
dirptn = re.compile('\w+dir$')
loctmp = locals().keys()
for dirname in [loc for loc in loctmp if dirptn.search(loc)]:
  trenddir = locals()[dirname]
  if not os.path.exists(trenddir):
    os.mkdir(trenddir)
