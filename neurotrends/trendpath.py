#!/usr/bin/env python
# encoding: utf-8

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

for dir in [data_dir, log_dir, fig_dir]:
    mkdir_p(dir)
