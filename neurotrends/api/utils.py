# -*- coding: utf-8 -*-

from __future__ import division

import re
import weakref
import itertools
import collections

from flask.ext.api import exceptions
from flask import request
from modularodm import Q
from webargs import Arg
import pymongo

from neurotrends import config
from neurotrends import tagger
from neurotrends import pattern
from neurotrends.pattern.misc import clean


class lazyproperty(object):
    """Cached property method decorator.

    :param method: Method to cache
    """
    def __init__(self, method):
        self.data = weakref.WeakKeyDictionary()
        self.method = method

    def __get__(self, instance, owner):
        try:
            return self.data[instance]
        except KeyError:
            value = self.method(instance)
            self.data[instance] = value
            return value


text_bool_map = {
    'true': True,
    'false': False,
}

def make_bool_arg(**kwargs):
    return Arg(
        use=lambda x: text_bool_map.get(x.lower()),
        validate=lambda x: x is not None,
        **kwargs
    )


def get_record_by_id(record_id, record_model, record_serializer):
    """Load a record by primary key and serialize.

    :param record_id: Record primary key
    :param record_model: Model class
    :param record_serializer: Serializer class
    """
    record = record_model.load(record_id)
    if record is None:
        raise exceptions.NotFound()
    serialized = record_serializer(record)
    return serialized.data


class QueryFieldTranslator(object):
    """Translate a query field to a ModularODM `Query`.

    :param field: Model field name
    :param operator: Query operator
    """
    def __init__(self, field, operator='eq'):
        self.field = field
        self.operator = operator

    def __call__(self, value):
        return Q(self.field, self.operator, value)


class QueryTranslator(object):
    """Translate a query mapping to a ModularODM `Query`.

    :param model: Schema class
    :param kwargs: Mapping of field names to translator callables
    """
    def __init__(self, model, **kwargs):
        self.model = model
        self.translators = {}
        for field, translator in kwargs.iteritems():
            self.add(field, translator)

    def add(self, field, translator):
        """

        :param field: Label of field in input mapping
        :param translator: Callable that takes a value and returns a `Query` object

        """
        self.translators[field] = translator

    def translate(self, kwargs):
        """Translate input data into a ModularODM `Query`.

        """
        reducer = lambda x, y: x & y
        filterer = lambda x: x is not None
        translated = (
            translator(kwargs[field])
            for field, translator in self.translators.iteritems()
            if kwargs.get(field) is not None
        )
        # Handle `TypeError` when `translators` is empty
        try:
            query = reduce(reducer, filter(filterer, translated))
        except TypeError:
            query = None
        return self.model.find(query)


class SortFieldTranslator(object):

    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        sign = '-' if value.startswith('-') else ''
        return '{0}{1}'.format(sign, self.field)


class SortTranslator(object):

    def __init__(self, **kwargs):
        self.translators = {}
        for field, translator in kwargs.iteritems():
            self.add(field, translator)

    def add(self, field, translator):
        self.translators[field] = translator

    def get_translator(self, key):
        field = key.lstrip('-')
        return self.translators[field]

    def translate(self, value):
        ret = []
        fields = [
            prepare_label(field)
            for field in value.split(',')
        ]
        for field in fields:
            try:
                translator = self.get_translator(field)
            except KeyError:
                continue
            translated = translator(field)
            ret.append(translated)
        return ret


def prepare_label(label):
    """

    :param str:

    """
    return (
        label
            .strip()
            .replace('.', '')
            .replace('$', '')
    )


def filter_dict(data, predicate):
    return {
        key: value
        for key, value in data.iteritems()
        if predicate(key, value)
    }


def sort_dict(data, key, as_dict=True, **kwargs):
    ordered = [
        pair
        for pair in sorted(
            data.items(),
            key=key,
            **kwargs
        )
    ]
    if as_dict:
        return collections.OrderedDict(ordered)
    return ordered


def get_year_counts():
    return {
        record['_id']: record['value']
        for record in config.year_counts_collection.find()
    }


def normalize_counts(tag_counts, year_counts=None):
    """Normalize tag counts by total article counts per year.

    :param dict count_records: Tag count records
    :param dict year_counts: Year count data; pull from database if not provided
    """
    year_counts = year_counts or get_year_counts()
    return {
        year: tag_counts[year] / year_counts[year]
        for year in tag_counts
        if year in year_counts
    }


def sort_counts(tag_counts):
    return sort_dict(
        tag_counts,
        lambda pair: pair[0],
        as_dict=False,
    )


def process_version_counts(count_records, year_counts=None):
    """Reshape list of tag version count records to a dictionary mapping years
    to tag version counts, optionally normalizing by total article counts per
    year.

    :param list count_records: Tag version count records
    :param dict year_counts: Optional year count data
    """
    tag_counts = {
        int(each['_id']['year']): int(each['value'])
        for each in count_records
        if each['_id']['year']
    }
    if year_counts:
        tag_counts = normalize_counts(tag_counts, year_counts)
    return sort_counts(tag_counts)


def get_tags_by_label(label, with_versions):
    """Find tags by partial label, optionally restricting to tags with version
    information. Used for tag autocomplete.

    :param str label: Tag label substring
    :param bool with_versions: Restrict to tags with version information
    :return: List of dictionaries including the label and overall count of each
        matching tag
    """
    pattern = re.escape(label)
    if with_versions:
        labels = config.version_counts_collection.find(
            {'_id.label': {'$regex': pattern}}
        ).distinct(
            '_id.label'
        )
        query = {'_id': {'$in': labels}}
    else:
        query = {'_id': {'$regex': pattern}}
    counts = config.tag_counts_collection.find(
        query
    ).sort(
        '_id', pymongo.ASCENDING
    )
    return [
        collections.OrderedDict([
            ('label', count['_id']),
            ('count', int(count['value'])),
        ])
        for count in counts
    ]


def get_tag_counts(label, normalize):
    """Fetch tag counts by year, optionally normalized by total article counts
    per year.

    :param str label: Tag label
    :param bool normalize: Normalize by total article counts
    """
    tag_counts = {
        int(record['_id']['year']): int(record['value'])
        for record in config.tag_year_counts_collection.find(
            {'_id.label': label}
        )
        if record['_id']['year']
    }
    if normalize:
        tag_counts = normalize_counts(tag_counts)
    return sort_counts(tag_counts)


def get_tag_version_counts(label, normalize):
    """Fetch tag counts by version by year, optionally normalized by total
    article counts per year.

    :param str label: Tag label
    :param bool normalize: Normalize by total article counts
    """
    year_counts = get_year_counts() if normalize else None
    sorted_counts = sorted(
        config.version_year_counts_collection.find({'_id.label': label}),
        key=lambda count: count['_id']['version'],
    )
    grouped_counts = itertools.groupby(
        sorted_counts,
        key=lambda count: count['_id']['version'],
    )
    return collections.OrderedDict([
        (version, process_version_counts(counts, year_counts))
        for version, counts in grouped_counts
    ])


def get_tag_author_counts(author_id):
    counts = [
        (record['_id']['label'], record['value'])
        for record in config.tag_author_counts_collection.find(
            {'_id.authorId': author_id}
        )
    ]
    return collections.OrderedDict(
        sorted(
            counts,
            key=lambda item: item[0],
        )
    )


def get_places(limit):
    return config.place_counts_collection.find(
        {}
    ).sort(
        'value', pymongo.DESCENDING
    ).limit(
        limit
    )


def divide(num, denom):
    if denom is None:
        return num
    return num / denom


def get_tag_place_counts(place, normalize):
    records = config.tag_place_counts_collection.find({'_id.place': place})
    if not records.count():
        raise exceptions.NotFound()
    if normalize:
        total = config.place_counts_collection.find_one({'_id': place})
        if not total:
            raise exceptions.NotFound()
        denom = total['value']
    else:
        denom = None
    counts = [
        (
            record['_id']['label'],
            divide(int(record['value']), denom)
        )
        for record in records
    ]
    return collections.OrderedDict(
        sorted(
            counts,
            key=lambda item: item[0]
        )
    )


def extract_tags(text):
    text_clean = clean(text)
    return sum(
        [
            [dict(tag) for tag in tagger.tag(tag_group, text_clean)]
            for tag_group in pattern.tag_groups.itervalues()
        ],
        []
    )

