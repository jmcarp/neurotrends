

def copy_table(table, fromsess, tosess):
  
  ins = table.insert()
  sel = select([table])
  res = fromsess.execute(sel)

  while True:
    rows = res.fetchmany(25)
    if len(rows) == 0:
      break
    tosess.execute(ins, rows)

  tosess.commit()

#migrate_tables = [
#  'places', 'authors', 'fields', 'attribs', 'articles',
#  'attribs_fields', 'articles_attribs', 'articles_authors',
#]
migrate_tables = [table.name for table in Base.metadata.sorted_tables]
def migrate(fromsess, tosess):
  
  print 'Clearing tables...'

  for table_name in reversed(migrate_tables):

    print 'Clearing table %s...' % (table_name)
    tosess.execute('DELETE from %s' % (table_name))
    tosess.commit()
  
  print 'Copying tables...'

  for table_name in migrate_tables:

    print 'Copying table %s...' % (table_name)
    table = Base.metadata.tables[table_name]
    copy_table(table, fromsess, tosess)
