
from collections import OrderedDict

def list2string(list, delim):
  return delim.join([str(x).lower() for x in list])

def val_or_blank(val, blank=None):
  return val if val else blank

def has_param(field, like_str):

  param_attribs = session.query(Attrib)\
    .filter(Attrib.fields.contains(field))\
    .filter(Attrib.fields.any(Field.name.like('%%%s' % (like_str))))

  return param_attribs.count() > 0

def arts2csv(out_name, xtra_vars=['pmid', 'doi'], delim=','):
  '''
  Write all article attributes to text.
  '''
  
  # Open output file
  out_file = open(out_name, 'w')
  
  # Get articles
  arts = session.query(Article)\
    .filter(or_(
      Article.htmlval >= 0.9,
      Article.pdfval >= 0.9
      ))\
    .order_by(Article.pmid)\
    .all()
    
  print 'Writing %d articles to text...' % (len(arts))
  
  columns = get_columns(tags)

  # Get labels
  csv0 = art2csv(arts[0], columns)
  labels = xtra_vars + csv0.keys()
  values = [getattr(arts[0], var) for var in xtra_vars] + csv0.values()
  
  # Write labels + first row
  out_file.write(list2string(labels, delim) + '\n')
  out_file.write(list2string(values, delim) + '\n')

  # Write remaining articles
  for artidx in range(1, len(arts)):
    if artidx % 100 == 0:
      print 'Working on article #%d...' % (artidx + 1)
    csv_data = art2csv(arts[artidx], columns)
    values = [getattr(arts[artidx], var) for var in xtra_vars] + csv_data.values()
    out_file.write(list2string(values, delim) + '\n')

  # Close output file
  out_file.close()

def get_columns(tags):
  
  columns = []

  for grp in tags:

    for tag in tags[grp]['src']:
      
      try:

        # Get name field
        field = session.query(Field)\
          .filter(Field.name == grp + 'name')\
          .filter(Field.value == tag)\
          .one()

        columns.append({
          'grp' : grp,
          'tag' : tag,
          'field' : field,
          'has_ver' : has_param(field, 'ver'),
          'has_value' : has_param(field, 'value'),
        })

      except:
        
        pass

  return columns

def art2csv(art, columns, bool_names={False : 0, True : 1}):
  '''
  Get dictionary of attributes from article.
  '''
  
  csv_dict = OrderedDict()
    
  for column in columns:

    csv_key = '%s_%s' % (column['grp'], column['tag'])
    csv_dict[csv_key] = bool_names[False]

    if column['has_ver']:
      csv_ver_key = '%s_ver' % (csv_key)
      csv_dict[csv_ver_key] = bool_names[False]

    if column['has_value']:
      csv_value_key = '%s_value' % (csv_key)
      csv_dict[csv_value_key] = bool_names[False]
    
    for attrib in art.attribs:

      if column['field'] in attrib.fields.values():

        csv_dict[csv_key] = bool_names[True]

        if column['has_ver']:
          verkey = column['grp'] + 'ver'
          if verkey in attrib.fields:
            csv_dict[csv_ver_key] = val_or_blank(
              attrib.fields[verkey].value,
              bool_names[False]
            )

        if column['has_value']:
          valkey = column['grp'] + 'value'
          if valkey in attrib.fields:
            csv_dict[csv_value_key] = val_or_blank(
              attrib.fields[valkey].value,
              bool_names[False]
            )

        break

  return csv_dict
