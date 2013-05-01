# -*- coding: latin-1 -*-

'''
Utility functions for geotagging using Google Maps
and Wikipedia.
'''

# Imports
import re

inststr = ['university', 'université', 'college']
instptn = [re.compile(ptn, re.I) for ptn in inststr]

# Email regex
email_ptn = re.compile(
    '(' +
        '[\w\-\.\+]+' +     # Check for +s also
        '[\s\-]*' +
        '(@|at)+' +
        '[\s\-]*' +
        '[\w\-]+' +
        '[\s\-]*' +
        '(' +
            '[\s\-]*' +
            '(\.|dot)+' +
            '[\s\-]*' +
            '[\w\-]+' +
        ')+' +
    ')', re.I)

inststr = ['university', 'université', 'college']
# From http://stackoverflow.com/questions/517923/what-is-the-best-way-to-remove-accents-in-a-python-unicode-string
import unicodedata
def strip_accents(s):
    '''

    '''

    return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))

def any_match(patterns, text, flags=re.I):
    '''

    '''

    for pattern in patterns:
        if type(pattern) == str:
            if re.search(pattern, text, flags):
                return True
        elif type(pattern) == type(re.compile('')):
            if pattern.search(text):
                return True

    return False

def geo_prep(query, join=False):
    '''

    '''

    # Strip email
    query = re.sub(email_ptn, '', query)

    # Strip initial / final characters
    query = query.strip('. ')

    # Split
    splitquery = re.split('\s*,\s*', query)

    # Drop parts before institution
    for splitidx in range(len(splitquery)):
        if any([re.search(inst, splitquery[splitidx]) for inst in instptn]):
            splitquery = splitquery[splitidx:]
            break

    # Drop departments
    clean_query = []
    for part in splitquery:
        if not re.search('department|division', part, re.I):
            clean_query.append(part)
        elif any_match(instptn, part):
            clean_query.append(part)
    
    # Optionally rejoin query
    if join:
        clean_query = ', '.join(clean_query)

    # Return
    return clean_query

