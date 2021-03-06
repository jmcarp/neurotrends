#!/usr/bin/env python
# encoding: utf-8

from __future__ import division

import math
import collections

import furl
from flask import request, url_for
from marshmallow import Schema, fields, MarshalResult

from neurotrends import util


def goto_page(url, page_num, page_key='page_num'):
    """Build URL for specified page number, preserving existing query parameters.

    :param url: Original URL
    :param page_num: Page number to browse to
    :param page_key: Query string key for page number

    """
    parsed_url = furl.furl(url)
    parsed_url.args[page_key] = page_num
    return parsed_url.url


class Page(object):

    def __init__(self, paginator, page_num):
        self.paginator = paginator
        self.page_num = page_num

    @property
    def offset(self):
        return (self.page_num - 1) * self.paginator.page_size

    @property
    def prev_page_num(self):
        return self.paginator.page_num_or_none(self.page_num - 1)

    @property
    def next_page_num(self):
        return self.paginator.page_num_or_none(self.page_num + 1)

    @property
    def contents(self):
        return self.paginator.query.offset(
            self.offset
        ).limit(
            self.paginator.page_size
        )


class Paginator(object):

    def __init__(self, query, page_size):
        self.query = query
        self.page_size = page_size

    def get_page(self, page_num):
        return Page(self, page_num)

    def page_num_or_none(self, page_num):
        if 1 <= page_num <= self.total_pages:
            return page_num
        return None

    @util.lazyproperty
    def count(self):
        return self.query.offset(0).limit(0).count()

    @util.lazyproperty
    def total_pages(self):
        return int(math.ceil(self.count / self.page_size))


class PaginatedQuerySchema(Schema):

    def __init__(self, page=None, *args, **kwargs):
        super(PaginatedQuerySchema, self).__init__(
            page.contents if page else None, *args, **kwargs
        )
        self.page = page

    @property
    def prev(self):
        prev_page_num = self.page.prev_page_num
        if prev_page_num is None:
            return None
        return goto_page(request.url, prev_page_num)

    @property
    def next(self):
        next_page_num = self.page.next_page_num
        if next_page_num is None:
            return None
        return goto_page(request.url, next_page_num)

    def dump(self, page, *args, **kwargs):
        self.page = page
        super_data, errors = super(PaginatedQuerySchema, self).dump(
            page.contents if page else None
        )
        data = collections.OrderedDict([
            ('prev', self.prev),
            ('next', self.next),
            ('pages', self.page.paginator.total_pages),
            ('count', self.page.paginator.count),
            ('results', super_data),
        ])
        return MarshalResult(data, errors)

# Base serializers

class TagSchema(Schema):
    class Meta:
        fields = ('label', 'category', 'group', 'context', 'value', 'version')
    value = fields.Function(lambda obj: obj.get('value'))
    version = fields.Function(lambda obj: obj.get('version'))


def serialize_author_url(obj):
    return url_for('author', author_id=obj._id, _external=True)


class AuthorSchema(Schema):
    class Meta:
        fields = ('_id', 'url', 'full', 'last', 'first', 'middle', 'suffix')
    full = fields.String(attribute='_full')
    url = fields.Function(serialize_author_url)


def serialize_article_date(obj):
    return obj.date.isoformat() if obj.date else None


def serialize_article_url(obj):
    return url_for('article', article_id=obj._id, _external=True)


class ArticleSchema(Schema):
    class Meta:
        fields = ('_id', 'url', 'record', 'date', 'pmid', 'doi', 'authors', 'tags')
    authors = fields.Nested(AuthorSchema, many=True)
    tags = fields.Nested(TagSchema, many=True)
    date = fields.Function(serialize_article_date)
    url = fields.Function(serialize_article_url)


# Paginated serializers

class AuthorQuerySchema(AuthorSchema, PaginatedQuerySchema):
    pass


class ArticleQuerySchema(ArticleSchema, PaginatedQuerySchema):
    pass


# Singleton "default" schemas
tag_schema = TagSchema()
tags_schema = TagSchema(many=True)

author_schema = AuthorSchema()
authors_schema = AuthorSchema(many=True)

author_query_schema = AuthorQuerySchema(many=True)
article_query_schema = ArticleQuerySchema(many=True)
