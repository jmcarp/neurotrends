# -*- coding: utf-8 -*-

import logging
import functools
import multiprocessing

from neurotrends.model import Article


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def retag(article_id, **kwargs):
    logger.info('Re-tagging article {0}'.format(article_id))
    try:
        article = Article.load(article_id)
        article.tag(**kwargs)
    except Exception as error:
        logger.error('Error tagging article {0}'.format(article_id))
        logger.exception(error)


def rescrape(article_id, **kwargs):
    logger.info('Re-scraping article {0}'.format(article_id))
    try:
        article = Article.load(article_id)
        article.scrape(**kwargs)
    except Exception as error:
        logger.error('Error scraping article {0}'.format(article_id))
        logger.exception(error)


def batch_retag(processes, query=None, limit=None, **kwargs):
    pool = multiprocessing.Pool(processes=processes)
    articles = Article.find(query)
    if limit:
        articles = articles.limit(limit)
    results = pool.map(
        functools.partial(retag, **kwargs),
        (article._id for article in articles),
    )


def batch_rescrape(processes, query=None, limit=None, **kwargs):
    pool = multiprocessing.Pool(processes=processes)
    articles = Article.find(query)
    if limit:
        articles = articles.limit(limit)
    results = pool.map(
        functools.partial(rescrape, **kwargs),
        (article._id for article in articles),
    )

