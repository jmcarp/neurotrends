# Import modules
import re

# Import Flask
from flask import Flask
from flask import request
from flask import render_template
from flask.ext.sqlalchemy import SQLAlchemy

# Import database
from trenddb import *

from api import *
artcls = new_alchemy_encoder(fields_to_expand=['authors', 'attribs', 'place'], ignore_fields=['articles', 'snippets', 'xml'], ignore_objs=[Field, Attrib])

# Set up app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s' % (dbfile)

# Set up database connection
flaskdb = SQLAlchemy(app)

pubptn = 'ncbi\.nlm\.nih\.gov/pubmed/(\d+)'

bookmarklet = """
  (function () {
    var pop = window.open(
      'http://127.0.0.1:5000/api?puburl=' + 
        encodeURIComponent(location.href), 
      'NeuroTrends Lookup', 
      'width=800, height=600'
    );
    void(window.setTimeout('pop.focus()', 250));
  }())
"""

@app.route('/')
def home():
  
  return render_template('home.html')

@app.route('/api')
def apiquery():

  # Copy arguments to dict
  args = request.args.to_dict()

  # Initialize Article query
  arts = session.query(Article)
  
  if 'puburl' in request.args:
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
  arts = arts.filter_by(**conds)

  # Filter by authors
  if 'auths' in args:
    for auth in args['auths'].split(','):
      likestr = '%' + auth.strip() + '%'
      arts = arts.filter(Article.authors.any(Author.lastname.like(likestr)))

  # Filter by attribs
  if 'attribs' in args:
    for attrib in args['attribs'].split(','):
      likestr = '%' + attrib.strip() + '%'
      arts = arts.filter(Article.attribs.any(Attrib._desc.like(likestr)))

  # Limit query
  arts = arts.limit(10)

  # Return JSON
  return json.dumps(arts.all(), cls=artcls)

if __name__ == '__main__':
  app.run()
