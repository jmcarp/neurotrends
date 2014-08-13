# -*- coding: utf-8 -*-


class Config(object):

    DB_PORT = '27017'
    DB_NAME = 'neurotrends'


class DevConfig(Config):

    DEBUG = True


class ProdConfig(Config):

    DEBUG = False

