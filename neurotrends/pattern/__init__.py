
from base import *

import os

moddir = os.path.split(__file__)[0]
ptnfiles = [mod.split('.')[0] for mod in os.listdir(moddir) if 
  mod.endswith('.py') and mod not in ['__init__.py', 'base.py']]

import imp

# Add module directory to path
import sys
sys.path.insert(0, moddir)

# Collect tags
tags = {}
for mod in ptnfiles:

  # Load tag module
  f, filename, description = imp.find_module(mod, __path__)
  modtmp = imp.load_module(mod, f, filename, description)

  # Compile tags
  for tag in modtmp.tags:
    modtmp.tags[tag] = comptag(modtmp.tags[tag])

  # Get category
  if 'cat' in dir(modtmp):
    cat = modtmp.cat
  else:
    cat = 'n/a'

  # Append tags
  tags[mod] = {
    'cat' : cat,
    'src' : modtmp.tags,
  }
