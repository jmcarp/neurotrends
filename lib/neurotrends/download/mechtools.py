# Import modules
import os
import getpass
import mechanize

# 
from BeautifulSoup import BeautifulSoup as bs

def checkproxy(br):
  
  br.open('http://weblogin.umich.edu')
  if br.geturl() == 'https://weblogin.umich.edu/services/':
    return True
  return False

def umlogin(br, userfile=None):
  """
  Log in to UM proxy
  Arguments:
    br (mechanize.Browser): Browser object
    userfile (str): Path to name/password file
  """

  ## Open login page
  #br.open('http://weblogin.umich.edu')
  #
  ## Quit if already logged in
  #if br.geturl() == 'https://weblogin.umich.edu/services/':
  #  return

  loggedin = checkproxy(br)
  if loggedin:
    return
  
  # Select form
  br.select_form(nr=0)

  # Fill form fields
  if userfile and os.path.exists(userfile):
    userinfo = open(userfile, 'r').readlines()
    br['login'] = userinfo[0].strip()
    br['password'] = userinfo[1].strip()
  else:
    br['login'] = getpass.getpass('Username: ')
    br['password'] = getpass.getpass()

  # Submit login form
  br.submit()

class NoHistory(object):
  'Hack to disable history in mechanize module.'
  
  def add(self, *a, **k): pass
  def clear(self): pass

def getbr():
  'Create mechanize.Browser instance.'

  br = mechanize.Browser(history=NoHistory())
  br.addheaders = [('User-Agent',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT)')]
  br.set_handle_robots(False)

  return br

def br2docs(br):
  'Extract HTML and BeautifulSoup documents from mechanize.Browser.'

  html = br.response().read()
  try:
    soup = bs(html)
  except:
    soup = None

  return html, soup
