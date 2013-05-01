# -*- coding: latin-1 -*-

# Import libraries
import re
import time
import urllib

# Set up pygeocoder
from pygeocoder import Geocoder, GeocoderError

# Project imports
from neurotrends.geo import geotools

# Time between queries
wait_time = 35

def tag(query, delay=False, start_ntry=5, verbose=True):
    '''Query Google Maps. Takes a list of query parameters, then repeatedly
    pops the first item until either a result is found or the list is empty.

    Args:
        query (list) : List of query parameters
        delay (bool) : Delay between queries?
        start_ntry (int) : Number of tries to make in case Google Maps
                           raises an exception
        verbose (bool) : Print output
    Returns:
        Dictionary of query parameters and results

    '''
    
    # 
    query = geotools.geo_prep(query)

    # Initialize results
    geoinfo = {
        'lat' : None,
        'lon' : None,
        'orig_query' : ', '.join(query),
        'orig_n_parts' : len(query),
    }

    # Reset try counter
    ntry = start_ntry
    
    # Loop until result obtained or query list is empty
    while query:
        
        # Build query string
        #query_str = geotools.geo_prep(query, join=True)
        query_str = ', '.join(query)
        query_str = query_str.encode('utf-8', 'ignore')
        
        try:
            
            # Delay
            if delay:
                time.sleep(wait_time)
            
            # Print what we're doing
            if verbose:
                print 'Searching Google Maps for %s...' % (query_str)

            # Send Google Maps query
            geo = Geocoder.geocode(query_str)
            geoinfo['lat'], geoinfo['lon'] = geo.coordinates
            
            # Break if success
            break

        except GeocoderError as e:
            
            if e.message != 'ZERO_RESULTS' and ntry > 0:
                
                ntry -= 1
                continue

        except:
            
            # Continue with next query
            pass
        
        # Pop first item from query and run next search
        query = query[1:]

        # Reset try counter
        ntry = start_ntry

    # Get final query
    geoinfo['final_query'] = ', '.join(query)
    geoinfo['final_n_parts'] = len(query)
    
    # Return
    return geoinfo
