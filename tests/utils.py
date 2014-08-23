# -*- coding: utf-8 -*-

import pymongo

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

