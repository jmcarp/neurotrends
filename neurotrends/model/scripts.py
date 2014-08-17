# -*- coding: utf-8 -*-

import random
import logging
import collections

from modularodm import Q
from sciscrape.utils import pubtools

from neurotrends.model import Article
from neurotrends.config import mongo
from neurotrends.model.config import SCRAPE_CLASS, SCRAPE_KWARGS


logger = logging.getLogger(__name__)


def add_missing(query, max_count, randomize=False):
    """Search PubMed for articles and scrape documents.

    :param str query: PubMed query
    :param int max_count: Maximum number of articles to process
    :param bool randomize: Randomize list of articles to fetch
    :return: Added article objects

    """
    pmids = pubtools.search_pmids(query)
    stored_pmids = [
        article['pmid']
        for article in mongo['article'].find(
            {}, {'pmid': 1}
        )
    ]

    missing_pmids = set(pmids) - set(stored_pmids)
    logger.warn('Found {0} articles to add.'.format(len(missing_pmids)))

    pmids_to_add = list(missing_pmids)[:max_count]
    if randomize:
        random.shuffle(pmids_to_add)

    records = pubtools.download_pmids(pmids_to_add)

    scraper = SCRAPE_CLASS(**SCRAPE_KWARGS)

    added = []

    for pmid, record in zip(pmids_to_add, records):
        logger.debug('Adding article {}'.format(pmid))
        article = Article.from_record(record)
        article.scrape(scraper)
        added.append(article)

    return added


def remove_duplicates(by='pmid'):
    """Remove duplicate articles by field.

    :param str by: Article field to identify duplicates

    """
    counts = collections.defaultdict(int)
    values = [
        value[by]
        for value in Article._storage[0].store.find({}, {by: 1})
    ]
    for value in values:
        counts[value] += 1

    for value, count in counts.items():
        if count == 1:
            continue
        articles = list(Article.find(Q(by, 'eq', value)))
        for duplicate in articles[1:]:
            logger.debug(
                'Deleting duplicate record: {}'.format(
                    value
                )
            )
            Article.remove_one(duplicate)

