# Import modules
import os
import re
import sys
import glob
import json
import urllib
import collections

# Import Flask
from flask import Flask
from flask import request
from flask import url_for
from flask import redirect
from flask import render_template
from flask.ext.sqlalchemy import SQLAlchemy

# Import database
from trenddb import *

from api import *

# Set up app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s' % (dbfile)

# Set up database connection
flaskdb = SQLAlchemy(app)

pubptn = 'ncbi\.nlm\.nih\.gov/pubmed/(\d+)'

@app.errorhandler(404)
def error404(e):

  return render_template('404.html'), 404

@app.route('/')
def home():
  
  return render_template('home.html')

@app.route('/about')
def about():
  
  return render_template('about.html')

@app.route('/list_galleries')
def list_galleries():
  
  galleries = [
    {
      'name' : 'Temporal Visualizations',
      'link' : 'temporal',
    },
    {
      'name' : 'Spatial Visualizations',
      'link' : 'spatial',
    },
  ]
  return render_template('list_galleries.html', galleries=galleries)

@app.route('/show_gallery/<gallery_name>')
def show_gallery(gallery_name):
  
  imgfull = glob.glob('%s/img/%s/*.png' % (app.static_folder, gallery_name))
  imgs = [os.path.split(img)[-1] for img in imgfull]
  imgdim = 500

  return render_template('show_gallery.html', **locals())

@app.route('/search')
def searchquery():

  if not request.args or not any(request.args.values()):
    return render_template('search.html')
  
  args = request.args.to_dict()
  if not all(args.values()):
    args = dict([(key, args[key]) for key in args if args[key]])
    return redirect(url_for('searchquery', **args))
  
  narts, offset, results = search(request)
  
  lastview = offset + len(results)
  if offset > 0:
    args['offset'] = max(0, offset - 10)
    prevhref = urllib.urlencode(args)
  if lastview < narts:
    args['offset'] = offset + 10
    nexthref = urllib.urlencode(args)
  
  html = data2html(results)
  html = '\n'.join(html)
  
  return render_template(
    'results.html', **locals()
  )

@app.route('/api')
def apiquery():

  ## Get results
  #narts, offset, results = search(request)
  #
  ## Return JSON
  #return json.dumps(results)
  return render_template('api_preview.html')

def search(request):

  # Copy arguments to dict
  if hasattr(request, 'args'):
    args = request.args.to_dict()
  else:
    args = request
  args = dict([(key, args[key]) for key in args if args[key]])

  # Initialize Article query
  arts = session.query(Article).order_by(Article.pubyear)
  
  if 'puburl' in args:
    puburl = args['puburl']
    pubreg = re.search(pubptn, puburl, re.I)
    if not pubreg:
      return 'invalid pubmed url'
    args['pmid'] = pubreg.groups()[0]
  
  # Filter by Article conditions
  conds = {}
  for key in ['pmid', 'doi', 'pubyear']:
    if key in args:
      conds[key] = args[key]
  if conds:
    arts = arts.filter_by(**conds)
  
  # Filter by article title
  if 'article_title' in args:
    likestr = '%' + args['article_title'] + '%'
    arts = arts.filter(Article.atitle.ilike(likestr))

  # Filter by journal title
  if 'journal_title' in args:
    likestr = '%' + args['journal_title'] + '%'
    arts = arts.filter(Article.jtitle.ilike(likestr))

  # Filter by authors
  if 'auths' in args:
    for auth in args['auths'].split(','):
      likestr = '%' + auth.strip() + '%'
      arts = arts.filter(Article.authors.any(Author.lastname.ilike(likestr)))

  # Filter by attribs
  if 'attribs' in args:
    for attrib in args['attribs'].split(','):
      likestr = '%' + attrib.strip() + '%'
      arts = arts.filter(Article.attribs.any(Attrib._desc.ilike(likestr)))

  # Get article count
  narts = arts.count()

  # Offset query
  offset = 0
  if 'offset' in args:
    offset = args['offset']
    if offset.isdigit():
      offset = int(offset)
      arts = arts.offset(offset)

  # Limit query
  arts = arts.limit(10)

  # Retrieve results
  arts = arts.all()

  # 
  artdict = collections.OrderedDict()
  for artidx in range(len(arts)):
    art = arts[artidx]
    key = 'Article %s: %s' % (artidx + offset + 1, art.atitle)
    artdict[key] = art

  # Convert to dict
  artjson = sqla2dict(artdict)
  
  # Return
  return narts, offset, artjson

if __name__ == '__main__':
  runargs = {}
  if len(sys.argv) > 1 and sys.argv[1] == 'visible':
    runargs['host'] = '0.0.0.0'
    runarts['port'] = int(os.environ.get('PORT', 5000))
  app.run(**runargs)
