
# Modified from http://stackoverflow.com/questions/5022066/how-to-serialize-sqlalchemy-result-to-json
import json
from sqlalchemy.ext.declarative import DeclarativeMeta

def ismeta(obj):
  return isinstance(obj.__class__, DeclarativeMeta)

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

def new_alchemy_encoder(revisit_self=False, fields_to_expand=[], ignore_fields=[], ignore_objs=[]):
    _visited_objs = []
    class AlchemyEncoder(json.JSONEncoder):
        def default(self, obj):
            if ismeta(obj):
                # don't re-visit self
                if revisit_self:
                    if obj in _visited_objs:
                        return None
                    _visited_objs.append(obj)
                
                if hasattr(obj, '_desc'):
                  return getattr(obj, '_desc')

                # go through each field in this SQLalchemy class
                fields = {}
                #for field in [x for x in dir(obj) if not x.startswith('_') and not x.endswith('id') and x != 'metadata']:
                for field in dir(obj):
                    if field.startswith('_'):
                      continue
                    if field.endswith('id'):
                      continue
                    if field == 'metadata':
                      continue
                    if field in ignore_fields:#['articles']:
                      continue
                    if not getinfo(obj, field, 'vis', 'prop', False) and field not in fields_to_expand:
                      continue
                    fname = getinfo(obj, field, 'full', 'prop', field)
                    val = obj.__getattribute__(field)

                    # is this field another SQLalchemy object, or a list of SQLalchemy objects?
                    if ismeta(val) or isinstance(val, list):# and len(val) > 0 and ismeta(val[0]):
                        # unless we're expanding this field, stop here
                        if field not in fields_to_expand or obj.__class__ in ignore_objs:#[Field, Attrib]:
                            # not expanding this field: set it to None and continue
                            continue
                        print 'here', field
                        fname = getinfo(obj, field, 'full', 'rel', field)
                        print 'there', fname
                    
                    print field, fname
                    fields[fname] = val

                # a json-encodable dict
                return fields

            return json.JSONEncoder.default(self, obj)
    return AlchemyEncoder
