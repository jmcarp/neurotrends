import synth_load
import main
from download import pubsearch
from download import pmid_doi
from trenddb import *

def synth_update(indiv=False):
    '''Get latest batch of DOIs from NeuroSynth, convert DOIs
    to PMIDs, and add missing articles to NeuroTrends.

    '''
    
    # Get DOIs from NeuroSynth
    synth_dois = synth_load.extract_neurosynth_dois()
    
    # Get IDs from NeuroTrends
    trend_ids = session.query(Article.doi, Article.pmid).all()
    trend_dois = [id[0] for id in trend_ids if id[0] is not None]
    trend_pmids = [id[1] for id in trend_ids]

    # Get set difference
    dois_to_add = list(set(synth_dois) - set(trend_dois))

    print 'Adding %s articles...' % (len(dois_to_add))
    
    # Initialize PMIDs to add
    if not indiv:
        pmids_to_add = []

    # Loop over DOIs
    for doi in dois_to_add:
        
        # Initialize PMID to missing
        pmid = ''

        # Attempt to get PMID from CrossRef API
        xref_info = pmid_doi.pmid_doi({'doi' : doi})
        if 'pmid' in xref_info:
            pmid = xref_info['pmid']
            print 'Found PMID using CrossRef'
        else:
            # Attempt to get PMID from PubMed API
            pubmed_info = pubsearch.artsearch(doi, retmax=2)
            if len(pubmed_info) == 1:
                pmid = pubmed_info[0]['pmid']
                print 'Found PMID using PubMed'

        # Quit if PMID missing
        if not pmid:
            continue

        # Quit if PMID in NeuroTrends
        if pmid in trend_pmids:
            continue
        
        # Update database OR add to list
        if indiv:
            main.update([str(pmid)])
        else:
            pmids_to_add.append(str(pmid))

    # Add PMIDs to NeuroTrends
    if not indiv:
        main.update(pmids_to_add)
