'''
Set up paths for NeuroTrends.
'''

# Imports
import os
import re

# Project imports
import neurotrends

# Get home directory
home_dir = os.path.dirname(neurotrends.__file__)

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

# Add directories to file_dirs
for file_type in file_dirs:
    dir_path = '%s/%s' % (dumpdir, file_type)
    file_dirs[file_type]['base_path'] = dir_path
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
