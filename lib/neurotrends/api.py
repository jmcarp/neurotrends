
# Modified from http://stackoverflow.com/questions/5022066/how-to-serialize-sqlalchemy-result-to-json
import json
from sqlalchemy.ext.declarative import DeclarativeMeta

def ismeta(obj):
  return isinstance(obj.__class__, DeclarativeMeta)

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
                for field in [x for x in dir(obj) if not x.startswith('_') and not x.endswith('id') and x != 'metadata']:
                    #print 'hi', field, field in ignore_fields
                    if field in ignore_fields:#['articles']:
                      #fields[field] = None
                      continue
                    val = obj.__getattribute__(field)

                    # is this field another SQLalchemy object, or a list of SQLalchemy objects?
                    if ismeta(val) or isinstance(val, list) and len(val) > 0 and ismeta(val[0]):
                        # unless we're expanding this field, stop here
                        if field not in fields_to_expand or obj.__class__ in ignore_objs:#[Field, Attrib]:
                            # not expanding this field: set it to None and continue
                            #fields[field] = None
                            continue

                    fields[field] = val

                # a json-encodable dict
                return fields

            return json.JSONEncoder.default(self, obj)
    return AlchemyEncoder



