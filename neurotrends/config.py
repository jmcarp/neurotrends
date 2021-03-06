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


def make_collection_proxy(collection_name):
    def _get_collection():
        return mongo[collection_name]
    return LocalProxy(_get_collection)


article_collection = make_collection_proxy('article')

cache_collection = make_collection_proxy('cache')
dist_collection = make_collection_proxy('distance')

tag_counts_collection = make_collection_proxy('tag_counts')
year_counts_collection = make_collection_proxy('year_counts')
place_counts_collection = make_collection_proxy('place_counts')
version_counts_collection = make_collection_proxy('version_counts')
tag_year_counts_collection = make_collection_proxy('tag_year_counts')
version_year_counts_collection = make_collection_proxy('version_year_counts')
tag_place_counts_collection = make_collection_proxy('tag_place_counts')
tag_author_counts_collection = make_collection_proxy('tag_author_counts')
stats_collection = make_collection_proxy('stats')


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

