# Import modules
import os
import sys
import datetime

# Modified from http://stackoverflow.com/questions/4675728/redirect-stdout-to-a-file-in-python
class Logger(object):

  def __init__(self, filepath='', filename=''):
    
    # Get log path
    if not filename:
      now = datetime.datetime.now()
      filename = now.strftime('log-%y-%m-%d')
    if filepath:
      filename = '%s/%s' % (filepath, filename)
    self.filename = filename
    ct = 0
    while os.path.exists(self.filename):
      ct += 1
      self.filename = '%s-%02d' % (filename, ct)

    self.terminal = sys.stdout
    self.log = open(self.filename, 'a')

    # Write initial message
    self.write('*****\n')

  def write(self, message):
    self.terminal.write(message)
    self.log.write(message)

  def close(self):
    self.log.close()
