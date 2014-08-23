# -*- coding: utf-8 -*-

from modularodm import Q

from neurotrends.model import Article


def update_dates(overwrite=False):
    query = None if overwrite else Q('date', 'eq', None)
    articles = Article.find(query)
    for article in articles:
        article.update_date()
        article.save()

