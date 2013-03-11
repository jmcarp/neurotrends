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

file_dirs = {
  'html' : { 'file_ext' : 'html' },
  'chtml' : { 'file_ext' : 'shelf' },
  'pdfraw' : { 'file_ext' : 'pdf' },
  'pdftxt' : { 'file_ext' : 'txt' },
  'pmc' : { 'file_ext' : 'html' },
}
for file_type in file_dirs:
  dir_path = '%s/%s' % (dumpdir, file_type)
  file_dirs[file_type]['base_path'] = dir_path
  if not os.path.exists(dir_path):
    os.mkdir(dir_path)
