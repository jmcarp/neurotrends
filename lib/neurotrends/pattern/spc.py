cat = 'analysis'

# Import base
from base import *

# Initialize tags
tags = {}

tags['mni'] = [
  mninumptn + delimptn + spcptn,
  spcptn + delimptn + 
    'of%sthe' % (delimptn) + 
    delimptn + mniptn,
]

tags['tal'] = [
    'talairach' + delimptn + spcptn,
]

