# -*- coding: utf-8 -*-

import pymongo
from modularodm.storage import MongoStorage

from neurotrends.config import client, mongo
from neurotrends.model import MODELS


def ensure_database(value):
    if isinstance(value, pymongo.database.Database):
        return value
    return client[value]


class TestDatabase(object):

    def __init__(self, database, models=None):
        self.database = ensure_database(database)
        self.models = models or MODELS
        self.backup = {}

    def __enter__(self):
        client.drop_database(self.database)
        self.backup = {
            model: model._storage[0]
            for model in self.models
        }
        for model in self.models:
            model._storage[0] = MongoStorage(self.database, model._name)

    def __exit__(self, exc_value, exc_type, exc_tb):
        client.drop_database(self.database)
        for model, storage in self.backup.iteritems():
            model._storage[0] = storage
        self.backup = {}

