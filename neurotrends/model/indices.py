# -*- coding: utf-8 -*-

import pymongo

from neurotrends.config import mongo


INDICES = {
    'article': [
        [('_lrecord.TI', pymongo.ASCENDING)],
        [('_lrecord.JT', pymongo.ASCENDING)],
        [('_lrecord.FAU', pymongo.ASCENDING)],
        [('tags.label', pymongo.ASCENDING)],
    ],
}


def ensure_indices():
    for collection_name, indices in INDICES.iteritems():
        collection = mongo[collection_name]
        for index in indices:
            collection.ensure_index(index)

