
from collections import OrderedDict

def list2string(list, delim):
  return delim.join([str(x).lower() for x in list])

def str_or_q(str):
  return str if str else '?'

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

  # Get labels
  csv0 = art2csv(arts[0], tags)
  labels = xtra_vars + csv0.keys()
  values = [getattr(arts[0], var) for var in xtra_vars] + csv0.values()
  
  # Write labels + first row
  out_file.write(list2string(labels, delim) + '\n')
  out_file.write(list2string(values, delim) + '\n')

  # Write remaining articles
  for artidx in range(1, len(arts)):
    if artidx % 100 == 0:
      print 'Working on article #%d...' % (artidx + 1)
    csv_data = art2csv(arts[artidx], tags)
    values = [getattr(arts[artidx], var) for var in xtra_vars] + csv_data.values()
    out_file.write(list2string(values, delim) + '\n')

  # Close output file
  out_file.close()

def art2csv(art, tags):
  '''
  Get dictionary of attributes from article.
  '''
  
  csv_dict = OrderedDict()
  
  # Loop over tag groups
  for grp in tags:

    # Loop over tags
    for tag in tags[grp]['src']:

      # Initialize result to false
      found_field = 'false'

      try:

        # Get name field
        field = session.query(Field)\
          .filter(Field.name == grp + 'name')\
          .filter(Field.value == tag)\
          .one()

        # Check attributes for name field
        for attrib in art.attribs:
          if field in attrib.fields.values():
            found_field = 'true'
            # Look up secondary properties
            verkey = grp + 'ver'
            valkey = grp + 'value'
            if verkey in attrib.fields:
              found_field += ':' + str_or_q(attrib.fields[verkey].value)
            elif valkey in attrib.fields:
              found_field += ':' + str_or_q(attrib.fields[valkey].value)
            break
      
      except:
        # Skip if field not found
        pass

      # Add result to list
      csv_key = '%s_%s' % (grp, tag)
      csv_dict[csv_key] = found_field

  # Return results
  return csv_dict
