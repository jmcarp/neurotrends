#!/usr/bin/env python
# encoding: utf-8

from __future__ import division

import numpy as np
import pandas as pd
import scipy.spatial

from neurotrends import util
from neurotrends import config


DIST_FUNCS = [
    scipy.spatial.distance.cosine,
    scipy.spatial.distance.correlation,
]


def get_article_ids(label):
    """Get set of article IDs that include requested tag.
    """
    return set(
        record['_id']
        for record in config.article_collection.find(
            {'tags.label': label},
            {'_id': True},
        )
    )


def jaccard_index(set1, set2):
    """Calculate Jaccard index across two sets.
    """
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union


def get_unique_tags():
    return config.tag_counts_collection.distinct('_id')


def get_pairwise_jaccard():
    tags = get_unique_tags()
    article_ids = {
        tag: get_article_ids(tag)
        for tag in tags
    }
    ntags = len(tags)
    frame = pd.DataFrame(
        data=np.zeros((ntags, ntags), dtype=np.float64),
        columns=tags,
        index=tags,
    )
    for idx1, tag1 in enumerate(tags):
        for tag2 in tags[idx1:]:
            distance = jaccard_index(article_ids[tag1], article_ids[tag2])
            frame[tag1][tag2] = distance
            frame[tag2][tag1] = distance
    return frame


class DistSet(object):
    """Encapsulate results of pairwise distances between tags.

    :param str metric: Name of distance function
    :param list tags: Tag labels
    :param dict dists: Mapping between sorted tuples of tag labels and distance
        values
    """
    def __init__(self, metric, tags, dists):
        self.metric = metric
        self.tags = tags
        self.dists = dists

    def get_vector(self, tag):
        if tag not in self.tags:
            raise ValueError('Tag {0} not found in distance matrix'.format(tag))
        vector = {}
        for each in self.tags:
            if each == tag:
                continue
            pair = tuple(sorted([tag, each]))
            vector[each] = self.dists[pair]
        return vector

    def to_matrix(self):
        ntags = len(self.tags)
        frame = pd.DataFrame(
            data=np.zeros((ntags, ntags), dtype=np.float64),
            columns=self.tags,
            index=self.tags,
        )
        for pair, dist in self.dists.iteritems():
            frame[pair[0]][pair[1]] = dist
            frame[pair[1]][pair[0]] = dist
        return frame

    def to_json(self):
        return {
            '_id': self.metric,
            'tags': self.tags,
            'distances': [
                {
                    'keys': keys,
                    'value': value,
                }
                for keys, value in self.dists.iteritems()
            ],
        }

    @classmethod
    def from_json(cls, data):
        return cls(
            data['_id'],
            data['tags'],
            {
                tuple(dist['keys']): dist['value']
                for dist in data['distances']
            },
        )


class DistMaker(object):
    """Encapsulate calculation of pairwise distances between tags as a function
    of co-occurrence in articles.
    """
    @util.lazyproperty
    def tags(self):
        return get_unique_tags()

    @util.lazyproperty
    def article_tags(self):
        return [
            [each['label'] for each in record['tags']]
            for record in config.article_collection.find(
                {'tags': {'$ne': None}},
                {'tags.label': True},
            )
        ]

    @util.lazyproperty
    def article_tags_bool(self):
        return {
            tag: [int(tag in tags) for tags in self.article_tags]
            for tag in self.tags
        }

    def get_distances(self, dist_func):
        dists = {}
        for idx1, tag1 in enumerate(self.tags):
            for tag2 in self.tags[idx1 + 1:]:
                key = tuple(sorted([tag1, tag2]))
                dists[key] = dist_func(
                    self.article_tags_bool[tag1],
                    self.article_tags_bool[tag2],
                )
        return DistSet(dist_func.__name__, self.tags, dists)


def cache_distances(dist_funcs=None):
    """Compute pairwise distances between tags according to the metrics in
    `dist_funcs` and cache results in database.
    """
    differ = DistMaker()
    dist_funcs = dist_funcs or DIST_FUNCS
    for dist_func in DIST_FUNCS:
        dist_set = differ.get_distances(dist_func)
        data = dist_set.to_json()
        config.dist_collection.update(
            {'_id': data['_id']},
            data,
            upsert=True,
        )
