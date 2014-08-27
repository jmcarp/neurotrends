# -*- coding: utf-8 -*-

import pymongo
from factory.base import Factory

from neurotrends import config


TEST_DATABASE_NAME = 'neurotrends_test'


class TestDatabase(object):
    """Context manager for database testing. On enter, switch to a test database,
    then clear it. On exit, clear database again and switch back to original
    database. Note: database switching is handled by the `LocalProxy` in
    neurotrends/config.py

    """
    def __init__(self, database_name=TEST_DATABASE_NAME):
        self.database_name = database_name
        self.original_database_name = None

    def __enter__(self):
        config.DATABASE_NAME, self.original_database_name = \
            self.database_name, config.DATABASE_NAME
        config.client.drop_database(self.database_name)

    def __exit__(self, exc_value, exc_type, exc_tb):
        config.client.drop_database(self.database_name)
        config.DATABASE_NAME = self.original_database_name
        self.original_database_name = None


class DictFactory(Factory):

    ABSTRACT_FACTORY = True
    FACTORY_FOR = dict

    @classmethod
    def _build(cls, target_class, **kwargs):
        return target_class(**kwargs)

    @classmethod
    def _create(cls, target_class, **kwargs):
        return cls._build(target_class, **kwargs)



# Borrowed from osf.io
class ModularOdmFactory(Factory):

    ABSTRACT_FACTORY = True

    @classmethod
    def _build(cls, target_class, *args, **kwargs):
        return target_class(*args, **kwargs)

    @classmethod
    def _create(cls, target_class, *args, **kwargs):
        instance = cls._build(target_class, *args, **kwargs)
        instance.save()
        return instance

