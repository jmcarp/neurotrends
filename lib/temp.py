

# Converting from SQLite to Postgres messed up the encoding on the XML and affiliation fields
# ... and probably otheres
def update_xml_and_affil():
  
  arts = session.query(Article).order_by(Article.pmid)

  for artidx in range(arts.count()):

    print 'Working on article %d...' % (artidx + 1)

    art = arts[artidx]
    
    retry(update_one, 5, 5, art)

    if artidx and artidx % 50:
      session.commit()

  session.commit()

def update_one(art):

  xml = artfetch(art.pmid)
  info = artinfo({'xml' : xml})
  art.xml = xml
  art.affil = info['affil']
