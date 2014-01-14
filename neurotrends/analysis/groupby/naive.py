"""
Group articles by permutations of tags, versions, years, and custom fields
in memory in Python.
"""

import collections
from neurotrends.model.utils import verified_mongo

BaseKey = collections.namedtuple('Key', ['label', 'date', 'version', 'value'])
class Key(BaseKey):
    def __new__(cls, label, date=None, version=None, value=None):
        return super(Key, cls).__new__(cls, label, date, version, value)

########
# Tags #
########

def summarize(articles):
    """Perform a naive group-by. Faster than map-reduce in MongoDB for data
    sets that fit in memory.

    :param articles: Iterable of articles (PyMongo cursor or list)
    :return: Dictionary mapping tuples of grouping data (label, label and
        version, etc.) to lists of article IDs

    """
    summary = collections.defaultdict(list)

    for article in articles:

        _id = article['_id']

        for tag in article['tags']:

            label = tag['label']
            version = tag.get('version')
            date = article['date'].year if article['date'] else None

            summary[Key(label)].append(_id)
            summary[Key(label, date)].append(_id)
            if version:
                summary[Key(label, version=version)].append(_id)
                summary[Key(label, date, version)].append(_id)

    try:
        articles.rewind()
    except AttributeError:
        pass

    return summary

def summarize_custom(articles, label, func):
    """Perform a naive group-by using a custom summary function.

    :param articles: Iterable of articles (PyMongo cursor or list)
    :param label: Label for summary key
    :param func: Custom function. Must accept a tag and return a value; values
        of type None will be ignored
    :return: Dictionary mapping tuples of grouping data to lists of article
        IDs

    """
    summary = collections.defaultdict(list)

    for article in articles:

        _id = article['_id']

        for tag in article['tags']:

            out = func(tag)
            date = article['date'].year if article['date'] else None

            if out is not None:
                summary[Key(label, value=out)].append(_id)
                summary[Key(label, date=date, value=out)].append(_id)

    try:
        articles.rewind()
    except AttributeError:
        pass

    return summary

def summarize_field_strength(tag):

    if tag['label'] == 'field_strength':
        return round(tag['value'] * 2.0) / 2

def summarize_smooth_kernel(tag):

    if tag['label'] == 'smooth_kernel':
        return round(tag['value'], 1)

def summarize_highpass_cutoff(tag):

    if tag['label'] == 'highpass_cutoff':
        return round(tag['value'], 1)

#########
# Ranks #
#########

from neurotrends.analysis.order import compute_positions, compute_ranks

def summarize_ranks(collection, labels, min_prop=None):
    """

    :param Collection collection:
    :param list labels:
    :param float min_prop:
    :return tuple:

    """
    summary = {}

    if min_prop:
        total_count = collection.find(verified_mongo).count()
        min_count = min_prop * float(total_count)
        labels = [
            label
            for label in labels
            if collection.find(
                {'tags.label': label}
            ).count() > min_count
        ]

    query = {
        'tags.label': {'$in': labels}
    }
    query.update(verified_mongo)
    cursor = collection.find(
        query,
        {'tags': True}
    )

    selectors = {
        label: {'label': label}
        for label in labels
    }

    for article in cursor:
        positions, _ = compute_positions(article['tags'], selectors)
        if not positions:
            continue
        summary[article['_id']] = compute_ranks(positions)

    return summary, labels
