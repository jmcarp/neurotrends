# -*- coding: utf-8 -*-

import weakref

from flask.ext.api import exceptions
from flask import request
from modularodm import Q


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
        translated = (
            translator(kwargs[field])
            for field, translator in self.translators.iteritems()
            if field in kwargs
        )
        # Handle `TypeError` when `translators` is empty
        try:
            query = reduce(reducer, translated)
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

