# -*- coding: utf-8 -*-

import re

from pymongo import MongoClient
from werkzeug.local import LocalProxy


DATES = range(2000, 2014)
DATABASE_NAME = 'neurotrends'


client = MongoClient()


# Use a `LocalProxy` for database access for simpler testing

def _get_database():
    return client[DATABASE_NAME]

mongo = LocalProxy(_get_database)


tag_counts_collection = mongo['tag_counts']
year_counts_collection = mongo['year_counts']
tag_year_counts_collection = mongo['tag_year_counts']
tag_author_counts_collection = mongo['tag_author_counts']
stats_collection = mongo['stats']


query = '''
    (
        "fmri"
        OR "functional mri"
        OR "functional magnetic resonance imaging"
    )
    AND humans[MH]
    AND (
        "psychological phenomena and processes"[MH]
        OR "behavior and behavior mechanisms"[MH]
        OR "brain mapping"[MH]
    )
    AND english[LA]
    AND "journal article"[PT]
    NOT "review"[PT]
    NOT "meta-analysis"[PT]
'''

