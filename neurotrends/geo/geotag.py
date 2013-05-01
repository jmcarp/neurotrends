'''

'''

#TODO: Search Wikipedia w/ fuzzy comparison

# Imports


# Project imports
from neurotrends.geo import geotools
from neurotrends.geo import gmaptag
from neurotrends.geo import wikitag

def geotag(query, taggers=[wikitag, gmaptag]):
    '''

    '''
    
    # Prepare query
    prep_query = geotools.geo_prep(query)
    
    # Try taggers in order
    for tagger in taggers:
        geo_info = tagger.tag(query)
        if geo_info and 'lat' in geo_info and 'lon' in geo_info:
            return geo_info
