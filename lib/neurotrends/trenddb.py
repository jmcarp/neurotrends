# Import libraries
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.collections import attribute_mapped_collection

# Paths
rootdir = '/Users/jmcarp/Dropbox/projects/fmri-software'
datadir = '%s/data' % (rootdir)

# Files
dbfile = '%s/fmri-trends.db' % (datadir)

Base = declarative_base()

def getdb(sqltype='postgres', dbfile=dbfile):
  
  # Create engine
  if sqltype == 'sqlite':
    db = create_engine('sqlite:///%s' % (dbfile))
  elif sqltype == 'postgres':
    heroku_url = os.enrivon.get('HEROKU_POSTGRESQL_BROWN_URL')
    if heroku_url:
      db = create_engine(heroku_url)
    else:
      db = create_engine('postgresql+psycopg2://jmcarp@localhost/postgres')

  # Create tables
  Base.metadata.create_all(db)

  # Start session
  Session = sessionmaker(bind=db)
  session = Session()

  # Return
  return db, session

######################
# Association tables #
######################

# Attribute-Field association
attribs_fields = Table('attribs_fields', Base.metadata,
  Column('attrib_id', Integer, ForeignKey('attribs.id')),
  Column('field_id', Integer, ForeignKey('fields.id'))
)

# Article-Attribute association
articles_attribs = Table('articles_attribs', Base.metadata,
  Column('article_id', Integer, ForeignKey('articles.id')),
  Column('attrib_id', Integer, ForeignKey('attribs.id'))
)

# Article-Author association
articles_authors = Table('articles_authors', Base.metadata,
  Column('article_id', Integer, ForeignKey('articles.id')),
  Column('author_id', Integer, ForeignKey('authors.id'))
)

##########
# Tables #
##########

class Snippet(Base):
  
  __tablename__ = 'snippets'

  id = Column(Integer, primary_key=True)
  article_id = Column(Integer, ForeignKey('articles.id'))
  
  # 
  name = Column(String)

  # 
  text = Column(String)

  def __repr__(self):
    shorttext = self.text[:min(len(self.text), 50)]
    shorttext = shorttext.encode('raw-unicode-escape')
    return '<%s:%s>' % (repr(self.name), repr(shorttext))

class Field(Base):
  
  __tablename__ = 'fields'

  # Primary key
  id = Column(Integer, primary_key=True)

  # Field name
  name = Column(String)

  # Field value
  value = Column(String)

  def __repr__(self):
    return '<%s:%s>' % (self.name, self.value)

class Attrib(Base):
  
  __tablename__ = 'attribs'

  # Primary key
  id = Column(Integer, primary_key=True)
  
  # Attribute name
  name = Column(String,
    info={'vis' : True, 'full' : 'Name'})
  
  # Attribute category
  category = Column(String)

  # Fields
  fields = relationship('Field', 
    secondary=attribs_fields, 
    backref='attribs',
    cascade='all, delete',
    collection_class=attribute_mapped_collection('name'), 
  )

  def __repr__(self):
    return '<%s: %s>' % (self.name, ', '.join([repr(self.fields[f]) for f in self.fields]))

  _desc = Column(String, 
    info={'vis' : True, 'full' : 'Description'})
  def __setattr__(self, key, val):
    super(Attrib, self).__setattr__(key, val)
    if self.name is None:
      return
    desc = []
    namekey = self.name + 'name'
    if namekey in self.fields:
      desc.append(self.fields[namekey].value)
    details = [
      self.fields[key].value for key in self.fields 
      if key != namekey and self.fields[key].value
    ]
    if details:
      desc.append(', '.join(details))
    super(Attrib, self).__setattr__('_desc', ' '.join(desc))
  
class Author(Base):
  
  __tablename__ = 'authors'

  # Primary key
  id = Column(Integer, primary_key=True)

  # Author name
  lastname = Column(String)
  frstname = Column(String)

  def __repr__(self):
    return '<%s, %s>' % (self.lastname, self.frstname)

  _desc = Column(String,
    info={'vis' : True, 'full' : 'Name'})
  def __setattr__(self, key, val):
    super(Author, self).__setattr__(key, val)
    names = []
    if self.lastname:
      names.append(self.lastname)
    if self.frstname:
      names.append(self.frstname)
    desc = ', '.join(names)
    super(Author, self).__setattr__('_desc', desc)

class Place(Base):
  
  __tablename__ = 'places'

  # Primary key
  id = Column(Integer, primary_key=True)

  # Original query
  orig = Column(String)
  norig = Column(Integer)

  # Final query
  final = Column(String,
    info={'vis' : True, 'full' : 'Location'})
  nfinal = Column(Integer)

  # Coordinates
  lon = Column(Float, 
    info={'vis' : True, 'full' : 'Latitude'})
  lat = Column(Float, 
    info={'vis' : True, 'full' : 'Longitude'})

  articles = relationship(
    'Article',
    order_by='Article.id',
    backref='place',
    cascade='all, delete, delete-orphan'
  )

  def __repr__(self):
    efinal = self.final.encode('raw-unicode-escape')
    return '<%s: %f, %f>' % (efinal, self.lon, self.lat)

  #_desc = Column(String)
  #def __setattr__(self, key, val):
  #  super(Place, self).__setattr__(key, val)
  #  if key not in  ['lat', 'lon']:
  #    return
  #  if self.final:
  #    if type(self.lat) == float and type(self.lon) == float:
  #      desc = '%s: %0.2f, %0.2f' % (self.final, self.lat, self.lon)
  #    else:
  #      desc = self.final
  #  else:
  #    desc = self.orig
  #  super(Place, self).__setattr__('_desc', desc)

class Article(Base):

  __tablename__ = 'articles'
  __info__ = {
    'full' : {
      'attribs' : 'Attributes',
      'authors' : 'Authors',
      'place' : 'Place',
    }
  }
  
  # Primary key
  id = Column(Integer, primary_key=True)
  
  # Article identifiers
  pmid = Column(String, unique=True, 
    info={'vis' : True, 'full' : 'PubMed ID'})
  doi = Column(String, 
    info={'vis' : True, 'full' : 'Document Object Identifier'})
  atitle = Column(String, 
    info={'vis' : True, 'full' : 'Article Title'})
  jtitle = Column(String, 
    info={'vis' : True, 'full' : 'Journal Title'})

  # PubMed XML
  xml = Column(Text)
  
  # Date
  pubyear = Column(String,
    info={'vis' : True, 'full' : 'Publication Year'})
  pubmonth = Column(String)
  pubday = Column(String)

  # Location
  affil = Column(String)
  place_id = Column(Integer, ForeignKey('places.id'))

  # Files
  puburl = Column(String)
  htmlfile = Column(String)
  pdfrawfile = Column(String)
  pdftxtfile = Column(String)

  # Extration methods
  htmlmeth = Column(String)
  pdfmeth = Column(String)

  # File validation
  htmlval = Column(Float)
  pdfval = Column(Float)

  # PDF information
  pdfocr = Column(Boolean)
  pdfdecrypt = Column(Boolean)
  pdfdmethod = Column(String)
  
  # Status
  scrapestatus = Column(String)
  
  # Snippets
  snippets = relationship(
    'Snippet', 
    order_by='Snippet.id', 
    backref='article', 
    cascade='all, delete, delete-orphan'
  )
  
  # Attribs
  attribs = relationship('Attrib', 
    secondary=articles_attribs, 
    backref='articles',
    cascade='all, delete'
  )

  # Authors
  authors = relationship('Author', 
    secondary=articles_authors, 
    backref='articles',
    cascade='all, delete',
  )

db, session = getdb()
