# Imports
import re
import csv
import tarfile
from cStringIO import StringIO
import requests

neurosynth_data_url = 'http://neurosynth.org/data/current_data.tar.gz'

# Adapted from http://stackoverflow.com/questions/8858414/using-python-how-do-you-untar-purely-in-memory
def load_neurosynth_data():
    '''Load data from a NeuroSynth tar file.
    
    Returns:
        Dictionary of file names -> file objects

    '''
    
    # Load NeuroSynth tar file
    req = requests.get(neurosynth_data_url)
    
    # Open tar file
    tar = tarfile.open(
        mode='r:gz', 
        fileobj=StringIO(req.content)
    )
    
    # Initialize files
    files = {}
    
    # Extract files
    for name in tar.getnames():
        files[name] = tar.extractfile(name)

    # Return files
    return files

def extract_neurosynth_dois(delimiter='\t'):
    '''Extract DOIs from a NeuroSynth database.txt file object.

    Args:
        database : file object containing a NeuroSynth database.txt file
    Returns:
        list of DOIs

    Note: Could use the csv module instead of splitting raw text,
    but this would require reading data in universal-newline mode,
    which is not supported by tarfile at the moment.

    '''
    
    # Load database
    database = load_neurosynth_data()

    # Read raw text
    raw = database['database.txt'].read()

    # Split into lines
    lines = re.split('[\n\r]', raw)

    # Split lines by delimiter
    lines = [line.strip().split(delimiter) for line in lines]

    # Get index of ID column
    idcol = lines[0].index('ID')

    # Get DOIs
    dois = [line[idcol] for line in lines[1:]]
    dois = list(set(dois))

    # Return DOIs
    return dois
