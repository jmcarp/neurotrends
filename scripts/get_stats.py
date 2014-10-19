#!/usr/bin/env python
# encoding: utf-8

import pymongo

from neurotrends.config import mongo
from neurotrends.config import stats_collection


articles = mongo['article']


def get_stats():
    num_articles = articles.count()

    article_dates = articles.find({'date': {'$ne': None}}, {'date': True})
    first_date = article_dates.sort('date', pymongo.ASCENDING)[0]['date'].year
    last_date = article_dates.sort('date', pymongo.DESCENDING)[0]['date'].year

    article_tags = articles.find(
        {'tags.0': {'$exists': True}},
        {'tags': True},
    )
    num_tags = sum((
        len(article['tags'])
        for article in article_tags
    ))

    return {
        'numArticles': num_articles,
        'firstYear': first_date,
        'lastYear': last_date,
        'numTags': num_tags,
    }


def cache_stats():
    stats = get_stats()
    stats['_id'] = 'stats'
    stats_collection.update(
        {'_id': 'stats'},
        stats,
        upsert=True,
    )
