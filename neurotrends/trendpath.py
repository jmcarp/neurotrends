"""
Set up paths for NeuroTrends.
"""

from __future__ import absolute_import

import os

import neurotrends
from .util import mkdir_p

# Get home directory
home_file = os.path.dirname(neurotrends.__file__)
home_dir = os.path.abspath(os.path.split(home_file)[0])

# Get sub-directories
data_dir = '%s/data' % (home_dir)
log_dir = '%s/log' % (home_dir)
fig_dir = '%s/fig' % (home_dir)

# Base path to downloaded files
#TODO: parameterize this
dumpdir = '/Users/jmcarp/Documents/artdump'

# Initialize file_dirs with extensions
file_dirs = {
    'html' : { 'file_ext' : 'html' },
    'chtml' : { 'file_ext' : 'shelf' },
    'pdf' : { 'file_ext' : 'pdf' },
    'pdftxt' : { 'file_ext' : 'shelf' },
    'pmc' : { 'file_ext' : 'html' },
}

for dir in [data_dir, log_dir, fig_dir]:
    mkdir_p(dir)

## Add directories to file_dirs
#for file_type in file_dirs:
#    dir_path = '%s/%s' % (dumpdir, file_type)
#    file_dirs[file_type]['base_path'] = dir_path
#    if not os.path.exists(dir_path):
#        os.mkdir(dir_path)
