# -*- coding: utf-8 -*-

import os
import re
import logging

from bson import ObjectId
from bs4 import UnicodeDammit
from unicodedata import normalize
from modularodm import Q


logger = logging.getLogger(__name__)


###########
# Queries #
###########

verified_mongo = {
    'verified': {'$ne': []}
}

verified_odm = Q(
    'verified', 'ne', []
)

#############
# Functions #
#############

def to_unicode(value):
    return UnicodeDammit(value).unicode_markup

make_oid = lambda: str(ObjectId())

def norm(txt):
    decode = txt.decode('utf-8')
    return normalize('NFKD', decode).encode('ascii', 'ignore')

def clean_institution(txt):
    txt = txt.strip()
    txt = re.sub(r'\(.*?\)', '', txt)
    txt = re.sub(r' - .*', '', txt)
    original = txt
    txt = re.sub(r'^the ', '', txt)
    txt = re.sub(r'[,&\-]', ' ', txt)
    txt = re.sub(r'\s(at|of|in)\s', ' ', txt)
    txt = re.sub(r'\s+', ' ', txt)
    txt = txt.lower()
    txt = txt.strip()
    txt = norm(txt)
    return (original, txt)

def load_institutions(fname):
    try:
        institutions = open(fname).readlines()
    except IOError as error:
        logger.error('Could not load institutions.')
        logger.exception(error)
        return []
    return [
        clean_institution(institution)
        for institution in institutions
    ]

here, _ = os.path.split(os.path.abspath(__file__))
institutions = load_institutions(os.path.join(here, 'data', 'institutions.csv'))

domains = [
    # Web domains
    ('yale.edu', 'Yale University'),
    ('harvard.edu', 'Harvard University'),
    ('stanford.edu', 'Stanford University'),
    ('columbia.edu', 'Columbia University'),
    ('princeton.edu', 'Princeton University'),
    ('mit.edu', 'Massachusetts Institute of Technology'),
    ('umaryland.edu', 'University of Maryland, College Park'),
    ('cam.ac.uk', 'University of Cambridge'),
    ('ox.ac.uk', 'University of Oxford'),
    ('ucl.ac.uk', 'University College London'),
    ('nottingham.ac.uk', 'The University of Nottingham'),
    ('kcl.ac.uk', "King's College London"),
    ('bangor.ac.uk', 'Bangor University'),
    ('mcgill.ca', 'McGill University'),
    ('man.ac.uk', 'The University of Manchester'),
    ('manchester.ac.uk', 'The University of Manchester'),
    ('wustl.edu', 'Washington University in St. Louis'),
    ('berkeley.edu', 'University of California, Berkeley'),
    ('ucla.edu', 'University of California, Los Angeles'),
    ('ucsd.edu', 'University of California, San Diego'),
    ('ucsf.edu', 'University of California, San Francisco'),
    ('davis.edu', 'University of California, Davis'),
    ('sunysb.edu', 'Stony Brook University'),
    ('umich.edu', 'University of Michigan'),
    ('msu.edu', 'Michigan State University'),
    ('wayne.edu', 'Wayne State University'),
    ('upenn.edu', 'University of Pennsylvania'),
    ('uic.edu', 'University of Illinois, Chicago'),
    ('uni-ulm.de', u'Universität Ulm'),
    ('uni-hamburg.de', u'Universität Hamburg'),
    ('freiburg.de', u'Universität Freiburg'),
    ('uni-duesseldorf.de', u'Universität Düsseldorf'),
    ('koeln.de', u'Universität zu Köln'),
    # University names and abbreviations
    ('Harvard', 'Harvard University'),
    ('UCLA', 'University of California, Los Angeles'),
    ('MIT,', 'Massachusetts Institute of Technology'),
    ('NYU', 'New York University'),
    # NIH rules
    ('NIH', 'National Institutes of Health'),
    ('National Institutes of Health', 'National Institutes of Health'),
    ('National Institute of Health', 'National Institutes of Health'),
    ('NIMH', 'National Institutes of Health'),
    ('National Institute of Mental Health', 'National Institutes of Health'),
    ('NINDS', 'National Institutes of Health'),
    ('National Institute of Neurological Disorders and Stroke', 'National Institutes of Health'),
    ('National Institute on Aging', 'National Institutes of Health'),
]

def get_institution(affiliation):
    """Look up the institution for a given article.

    :param str affiliation: PubMed-style affiliation string
    :return str: Institution name

    """
    for domain in domains:
        if domain[0] in affiliation:
            return domain[1]

    _, clean = clean_institution(affiliation)

    matches = [
        institution
        for institution in institutions
        if institution[1] in clean
    ]
    matches = sorted(matches, key=lambda x: len(x[1]))

    if matches:
        return matches[-1][0].strip()

