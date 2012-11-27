# Import libraries
import os
import re
import glob
import time
import psutil
import signal
import subprocess
from appscript import *
from docx.docx import *

# Acrobat Preferences
# Convert From PDF -> Word Document
# Page layout: Flowing Text
# Include comments: False
# Include images: False
# Run OCR if needed: True

# Set up Acrobat
acro = app('Adobe Acrobat Pro')

# Set temporary directory
tmpdir = '/tmp'

# Set minimum PDF character length
mintxtlength = 2500

def acropid():
  'Return PID of Acrobat process.'
  
  # Get all processes
  procs = psutil.get_process_list()

  # Look for Acrobat process
  for proc in procs:
    try:
      pname = proc.name
      pid = proc.pid
      if re.search('acrobat', pname, re.I):
        return pid
    except:
      pass

  # No process found
  return -1

def fileparts(filename):
  'Split file name into parts.'
  
  path, full = os.path.split(filename)
  name, ext = os.path.splitext(full)

  return path, name, ext

def acroproc():
  'Return Acrobat system process.'

  return app('System Events').processes['Acrobat']

def acrowin():
  'Return list of Acrobat windows.'

  return acroproc().windows()

def acrostart():
  'Start Acrobat.'
  
  # Activate Acrobat
  try:
    acro.activate()
    return
  except:
    pass

  # Launch and activate Acrobat
  try:
    acro = app('Adobe Acrobat Pro')
    acro.activate()
    return
  except:
    pass
  
  # Kill, launch, and activate Acrobat
  print 'Attempting to kill Acrobat...'
  pid = acropid()
  if pid > 0:
    os.kill(pid, signal.SIGKILL)
    time.sleep(5)
    acro = app('Adobe Acrobat Pro')
    acro.activate()

def acrosel(method='short'):
  'Select all'
  
  # Emulate CTRL-A
  if method == 'short':
    acroproc().\
      keystroke(u'a', using=[k.command_down])

  # Emulate Edit -> Select All
  elif method == 'menu':
    acroproc().\
      menu_bars[1].menus['Edit'].\
      menu_items['Select All'].click()

def acroclose():
  'Close all active Acrobat windows'
  
  print 'Closing Acrobat windows...'

  # Repeat until finished
  for ntry in range(30):
    
    try:
      windows = acrowin()
    except:
      break

    try:
      
      # Close dialog box
      acroproc().keystroke('\r')

      # Close Acrobat window
      acroproc().\
        menu_bars[1].menus['File'].\
        menu_items['Close'].click()
  
      # Check for Save dialog
      windows = acrowin()
      if len(windows) > 1 and any([re.search('windows\[1\]', repr(window), re.I) for window in windows]):
        app('System Events').processes['Acrobat']\
          .windows[1]\
          .buttons[u'Don\'t Save'].click()
    
      # Quit if finished
      windows = acrowin()
      if len(windows) == 0:
        break
      if len(windows) == 1 and re.search('windows\[1\]', repr(windows[0]), re.I):
        break

    except:
      
      pass
    
    # Wait
    time.sleep(1)

  # Restart Acrobat
  # (useful if Acrobat crashed)
  acrostart()

def pdfread(pdfname, totiff=False):
  
  pdfinfo = {
    'txt' : '',
    'ocr' : False,
    'decrypt' : False,
    'dmethod' : None
  }
  
  if not totiff:

    # Start Acrobat
    acrostart()

    # Extract PDF text
    # Attempt #1
    pdftxt = pdfxtract(pdfname, method='docx')
    if pdftxt and len(pdftxt) >= mintxtlength:
      pdfinfo['txt'] = pdftxt
      # Close Acrobat
      acroclose()
      return pdfinfo

  # Decrypt PDF: Acrobat
  acrostart()
  dpdfname = pdfdecrypt(pdfname)
  pdfinfo['ocr'] = True
  pdfinfo['decrypt'] = True
  pdfinfo['dmethod'] = 'acro'

  # Decrypt PDF: GhostScript
  if not dpdfname:
    dpdfname = pdfdecrypt(pdfname, 'ghost')
    pdfinfo['dmethod'] = 'ghost'
    if not dpdfname:
      return
  
  # Extract PDF text
  # Attempt #2
  pdftxt = pdfxtract(dpdfname, method='docx')
  if pdftxt and len(pdftxt) >= mintxtlength:
    pdfinfo['txt'] = pdftxt
    # Close Acrobat
    acroclose()
    return pdfinfo
  
  # Close Acrobat
  acroclose()

  return

def saveasdocx():
  
  acroproc().\
    menu_bars[1].menus['File'].\
    menu_items['Save As'].menus[1].\
    menu_items['Microsoft Word'].menus[1].\
    menu_items['Word Document'].\
    click()

def saveasext():
  
  # Delete existing extended file
  extfile = '%s/extfile.pdf' % (tmpdir)
  if os.path.exists(extfile):
    os.remove(extfile)

  # Call save dialog
  acroproc().\
    menu_bars[1].menus['File'].\
    menu_items['Save As'].menus[1].\
    menu_items['Reader Extended PDF'].menus[1].\
    menu_items['Enable Additional Features...'].\
    click()
  
  # 
  while any([re.search('Enable Usage Rights', repr(win)) for win in acrowin()]):
    acroproc().keystroke('\r')
    time.sleep(0.5)

  # Input file name
  while True:
    time.sleep(1)
    acrosel()
    acroproc().keystroke(extfile)
    for tryct in range(5):
      acroproc().keystroke(u'\r')
      time.sleep(0.5)
      windows = acrowin()
      if not checkwindow('Save'):
        break
    if not checkwindow('Save'):
      break
  print 'Done with Save As dialog...'

def pdf2docx():

  print 'Saving as docx...'

  # Get file names
  docxname = '%s/xtract' % (tmpdir)
  docxfull = '%s.docx' % (docxname)

  # Delete existing .docx file
  if os.path.exists(docxfull):
    os.remove(docxfull)

  # Save as .docx
  todoc = False
  try:
    saveasdocx()
    todoc = True
  except:
    print 'Save as .docx failed...'

  # Save as extended pdf
  # Then save as .docx
  if not todoc:
    print 'Saving as Extended PDF...'
    try:
      saveasext()
      # Delete existing .docx file
      if os.path.exists(docxfull):
        os.remove(docxfull)
      saveasdocx()
      todoc = True
    except:
      print 'Save as Extended PDF -> .docx failed'

  # Quit if conversion failed
  if not todoc:
    return ''

  # Wait for Save As dialog
  waitwindow('Save As')
  
  # Input file name
  while True:
    time.sleep(1)
    acrosel()
    acroproc().keystroke(docxname)
    for tryct in range(5):
      acroproc().keystroke(u'\r')
      time.sleep(0.5)
      windows = acrowin()
      if not checkwindow('Save As'):
        break
    if not checkwindow('Save As'):
      break
  print 'Done with Save As dialog...'
  
  # Check for fail dialog
  print 'Checking for fail dialog...'
  windows = acrowin()
  if len(windows) > 1:
    while len(windows) > 1:
      acroproc().keystroke(u'\r')
      time.sleep(1)
      windows = acrowin()
    return ''
  print 'Done checking for fail dialog...'

  for ntry in range(600):
    print 'Checking docxfile', os.path.exists(docxfull)
    if os.path.exists(docxfull):
      return docxfull
    time.sleep(1)

  return ''

def pdfxtract(pdfname, method='docx'):
  
  if method == 'docx':
    
    # Save as .docx
    for ntry in range(5):

      # Bring Acrobat to front
      acro.activate()

      # Open PDF
      acroopen(pdfname)

      # Check for scanned text alert
      alert = closescanalert()
      if alert:
        print 'Warning: Encountered scanned text alert'
        return

      docxname = pdf2docx()
      if docxname:
        break

      # Close documents
      acroclose()

    if not docxname:
      return ''
    
    # Read file
    txt = ''
    lines = []
    for tryct in range(5):
      try:
        lines = getdocumenttext(opendocx(docxname))
        break
      except:
        print 'Retrying .docx read...'
        time.sleep(1)
    for line in lines:
      if not txt or txt.endswith('-'):
        txt = '%s%s' % (txt, line)
      else:
        txt = '%s %s' % (txt, line)
    txt = re.sub('\s+', ' ', txt)
    os.remove(docxname)
    
    return txt

  elif method == 'copy':

    # Select all
    time.sleep(1)
    acrosel()
    
    # Copy
    time.sleep(1)
    acroproc().\
      menu_bars[1].menus['Edit'].\
      menu_items['Copy'].click()
    
    # Extract text (may take several attempts)
    time.sleep(3)
    txt = ''
    ntxt = 0
    nemp = 0
    while True:
      txttmp = getclip()
      if txttmp:
        if len(txttmp) > len(txt):
          txt = txttmp
        ntxt += 1
      else:
        nemp += 1
        print 'Warning: No text. Repeating copy...'
      if ntxt >= 3:
        break
      if nemp >= 15:
        break
      print 'Repeating copy...'
      time.sleep(3)
    
    # Clear clipboard
    clearclip()

def pdfdecrypt(pdfname, splitmethod='acro'):

  # Get output name
  path, name, ext = fileparts(pdfname)
  tifname = '%s/d%s.tiff' % (path, name)
  newpdfname = '%s/d%s.pdf' % (path, name)

  # Delete TIFFs
  delcmd = 'rm %s/*Page*.tif*' % (tmpdir)
  os.system(delcmd)

  # Split PDF
  if splitmethod == 'acro':
    acrosplit(pdfname)
  elif splitmethod == 'ghost':
    ghostsplit(pdfname)

  # Get TIFFs
  splitfiles = glob.glob('%s/*Page*.tif*' % (tmpdir))
  if len(splitfiles) < 1:
    return False

  # Join TIFFs
  joincmd = 'tiffcp %s/*Page*.tif* %s' % (tmpdir, tifname)
  os.system(joincmd)

  # Delete TIFFs
  delcmd = 'rm %s/*Page_*.tif*' % (tmpdir)
  os.system(delcmd)

  # Convert TIFF to PDF
  if os.path.exists(newpdfname):
    os.remove(newpdfname)
  
  # Open TIFF
  acro.activate()
  acroopen(tifname)
  
  # Save
  acroproc().\
    keystroke(u's', using=[k.command_down])

  while True:

    # Select all
    acrosel()
    
    # Enter file name
    acroproc().keystroke(newpdfname)
    time.sleep(1); acroproc().keystroke(u'\r')
    time.sleep(1); acroproc().keystroke(u'\r')
    
    # Check completion
    time.sleep(3)
    windows = acrowin()
    if not checkwindow('Save As'):
      break
  
  # Close PDF
  acroclose()

  return newpdfname

def pdf2txt(pdfname):

  # Bring Acrobat to front
  acro.activate()

  # Open PDF
  acroopen(pdfname)

  alert = closescanalert()
  if alert:
    print 'Warning: Encountered scanned text alert'
    return
  
  try:
    txt = pdfxtract(method='docx')
  except:
    txt = ''

  # Return PDF text
  if txt:
    return txt

  return ''

def closescanalert():
  'Check for Scanned Page Alert.'

  windows = acrowin()
  if checkwindow('scanned page alert', re.I):
    time.sleep(1)
    acroproc().\
      windows['Scanned Page Alert'].\
      buttons['Cancel'].click()
    return True

  return False
  
def acroopen(filename):
  'Open file using Acrobat.'
  
  # Activate Acrobat
  acro.activate()

  # Close active files
  acroclose()

  # Open file
  acro.open(filename)
  
  # Check for Scanned Page Alert
  closescanalert()

  # Check for pop-up
  windows = acrowin()
  if len(windows) > 1:
    acroproc().\
      keystroke(u'\r')

  # Check for full-screen
  windows = acrowin()
  if re.search('windows\[1\]', repr(windows[0])):
    acroproc().keystroke(u'l', using=[k.command_down])

  # Enable scrolling
  acroproc().\
    menu_bars[1].menus['View'].\
    menu_items['Page Display'].\
    menus[1].menu_items['Enable Scrolling'].click()

def checkwindow(winptn, flags=0):
  '''Check windows for pattern.'''
  
  for win in acrowin():
    if re.search(winptn, repr(win), flags=flags):
      return True

  return False

def waitwindow(winptn, sleepint=1):
  '''Wait for dialog box to close.'''

  while True:
    if checkwindow(winptn):
      break
    time.sleep(sleepint)

def acrosplit(pdfname):
  '''Split PDF into single-page TIFFs using Acrobat.'''
  
  # Delete existing .tiff
  tifname = '%s/pdfsplit' % (tmpdir)
  tiffull = '%s.tiff' % (tifname)
  if os.path.exists(tiffull):
    os.remove(tiffull)

  # Activate Acrobat
  acro.activate()

  # Open PDF
  acroopen(pdfname)

  # Convert to TIFF
  acroproc().\
    menu_bars[1].menus['File'].\
    menu_items['Save As'].menus[1].\
    menu_items['Image'].menus[1].\
    menu_items['TIFF'].\
    click()
  
  waitwindow('Save As')
  
  # Input file name
  while True:
    time.sleep(1)
    acroproc().keystroke(u'a', using=[k.command_down])
    acroproc().keystroke(tifname)
    time.sleep(0.25); acroproc().keystroke(u'\r')
    time.sleep(0.25); acroproc().keystroke(u'\r')
    windows = acrowin()
    if not checkwindow('Save As'):
      break

  # Check for fail dialog
  print 'Checking for fail dialog...'
  windows = acrowin()
  if len(windows) > 1:
    while len(windows) > 1:
      acroproc().keystroke(u'\r')
      time.sleep(1)
      windows = acrowin()
  print 'Done checking for fail dialog...'

  # Close PDF
  acroclose()

def ghostsplit(pdfname):
  'Split PDF into single-page TIFFs using GhostScript'
  
  # Build GhostScript command
  splitcmd = 'gs -dBATCH -dNOPAUSE -sDEVICE=tiffg4 -r600x600 ' + \
    '-sOutputFile=%s/pdfsplit-Page%%03d.tif %s' % (tmpdir, pdfname)
  
  # Run command
  os.system(splitcmd)
