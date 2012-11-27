#!/usr/bin/env python
# -*- coding: latin-1 -*-

import re

reptable = {
  'ä' : 'a',
  'ö' : 'o',
  'ü' : 'u',
}

def toascii(instr):
  
  for fromchar in reptable:
    tochar = reptable[fromchar]
    instr = re.sub(fromchar, tochar, instr)
    instr = re.sub(fromchar.decode('utf-8'), tochar, instr)

  return instr
