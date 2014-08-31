# -*- coding: utf-8 -*-

import logging
import multiprocessing
from collections import namedtuple

from neurotrends.model import Article


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


RetagCommand = namedtuple('RetagCommand', ['article_id', 'overwrite'])
RescrapeCommand = namedtuple('RescrapeCommand', ['article_id', 'overwrite'])


def retag(command):
    logger.info('Re-tagging article {0}'.format(command.article_id))
    try:
        article = Article.load(command.article_id)
        article.tag(overwrite=command.overwrite)
    except Exception as error:
        logger.error('Error tagging article {0}'.format(command.article_id))
        logger.exception(error)


def rescrape(command):
    logger.info('Re-scraping article {0}'.format(command.article_id))
    try:
        article = Article.load(command.article_id)
        article.scrape(overwrite=command.overwrite)
    except Exception as error:
        logger.error('Error scraping article {0}'.format(command.article_id))
        logger.exception(error)


def batch_retag(processes, query=None, limit=None, overwrite=True):
    pool = multiprocessing.Pool(processes=processes)
    articles = Article.find(query)
    if limit:
        articles = articles.limit(limit)
    results = pool.map(
        retag,
        (RetagCommand(article._id, overwrite) for article in articles),
    )


def batch_rescrape(processes, query=None, limit=None, overwrite=False):
    pool = multiprocessing.Pool(processes=processes)
    articles = Article.find(query)
    if limit:
        articles = articles.limit(limit)
    results = pool.map(
        rescrape,
        (RescrapeCommand(article._id, overwrite) for article in articles),
    )

