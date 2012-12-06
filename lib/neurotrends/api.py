# Adapted from http://stackoverflow.com/questions/5022066/how-to-serialize-sqlalchemy-result-to-json
import collections
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm.properties import RelationshipProperty

from BeautifulSoup import UnicodeDammit
from trenddb import *

def thing2unicode(thing):
  
  if type(thing) in [str, unicode]:
    return UnicodeDammit(thing).unicode
  return UnicodeDammit(str(thing)).unicode

def data2html(data, indent=0, level=0, ichar='  '):
  
  ichar = unicode(ichar)
  if level == 0:
    ulstr = '<ul class="root">'
  else:
    ulstr = '<ul>'

  if isinstance(data, list):
    if len(data) == 1:
      return data2html(data[0], indent=indent, level=level+1)
    html = []
    html.append(ichar * indent + ulstr)
    for idx in range(len(data)):
      item = data[idx]
      html.append(ichar * (indent + 1) + '<li class="stub">')
      html.extend(data2html(item, indent=indent+2, level=level+1))
      html.append(ichar * (indent + 1) + '</li>')
    html.append(ichar * indent + '</ul>')
    return html

  if isinstance(data, dict):
    html = []

    if len(data) == 1:
      key = data.keys()[0]
      html.append('%s' % (key))
      html.extend(data2html(data[key], indent=indent+1, level=level+1))
      return html

    html.append(ichar * indent + ulstr)
    for key in data:
      val = data[key]
      usediv = isinstance(val, dict) or isinstance(val, list)
      if usediv:
        html.append(ichar * (indent + 1) + '<li>')
      else:
        html.append(ichar * (indent + 1) + '<li class="stub">')
      if usediv:
        html.append(ichar * (indent + 1) + '<div class="head">')
      html.append(ichar * (indent + 2) + '%s' % (key))
      if usediv:
        html.append(ichar * (indent + 1) + '</div>')
        html.append(ichar * (indent + 1) + '<div class="tail">')
      html.extend(data2html(val, indent=indent+2, level=level+1))
      if usediv:
        html.append(ichar * (indent + 1) + '</div>')
      html.append(ichar * (indent + 1) + '</li>')
    html.append(ichar * indent + '</ul>')
    return html

  return [ichar * indent + thing2unicode(data)]

def ismeta(obj):
  return isinstance(obj.__class__, DeclarativeMeta)

def getproperties(obj):
  return obj.__table__.columns.keys()

def getrelations(obj):
  return [
    prop.key for prop in obj.__mapper__.iterate_properties 
    if isinstance(prop, RelationshipProperty)
  ]

def getinfo(obj, field, infofield, type='prop', default=None):

  # Get default option
  if default is None:
    default = field

  # Get table column
  if type == 'prop':
    columns = obj.__class__.__table__.columns
    if field not in columns:
      return default
    column = columns[field]
    # Get info value
    if hasattr(column, 'info') and infofield in column.info:
      return column.info[infofield]
  elif type == 'rel':
    if not hasattr(obj.__class__, '__info__'):
      return default
    info = obj.__class__.__info__
    if infofield in info and field in info[infofield]:
      return info[infofield][field]

  # If not found return default
  return default

fields_to_expand = ['place', 'authors', 'attribs']
ignore_objs = []#[Attrib, Field]
def sqla2dict(obj):
    
  if isinstance(obj, list):

    return [sqla2dict(item) for item in obj]

  if isinstance(obj, dict):

    return collections.OrderedDict(
      [(key, sqla2dict(obj[key])) for key in obj]
    )

  if ismeta(obj):
    
    fields = collections.OrderedDict()
    
    keys = getproperties(obj) + getrelations(obj)

    if '_desc' in keys:
      fname = getinfo(obj, '_desc', 'full', 'prop')
      return obj._desc

    for field in keys:

      if not getinfo(obj, field, 'vis', 'prop', False) \
          and field not in fields_to_expand:
        continue

      fname = getinfo(obj, field, 'full', 'prop', field)
      val = obj.__getattribute__(field)

      if ismeta(val) or isinstance(val, list):
        #if field not in fields_to_expand or obj.__class__ in ignore_objs:
        if obj.__class__ in ignore_objs:
          continue
        fname = getinfo(obj, field, 'full', 'rel', field)
        val = sqla2dict(val)

      fields[fname] = val

    return fields

  return obj
