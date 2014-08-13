# -*- coding: utf-8 -*-

from __future__ import division

import math
import collections

import furl
from flask import request
from marshmallow import Serializer, fields

from . import utils


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

    @utils.lazyproperty
    def count(self):
        return self.query.offset(0).limit(0).count()

    @utils.lazyproperty
    def total_pages(self):
        return int(math.ceil(self.count / self.page_size))


class PaginatedQuerySerializer(Serializer):

    def __init__(self, page, *args, **kwargs):
        super(PaginatedQuerySerializer, self).__init__(
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

    @property
    def data(self):
        super_data = super(PaginatedQuerySerializer, self).data
        return collections.OrderedDict([
            ('prev', self.prev),
            ('next', self.next),
            ('pages', self.page.paginator.total_pages),
            ('count', self.page.paginator.count),
            ('results', super_data),
        ])


# Base serializers

class TagSerializer(Serializer):
    class Meta:
        fields = ('label', 'category', 'context')


class AuthorSerializer(Serializer):
    class Meta:
        fields = ('_id', 'last', 'first', 'middle', 'suffix', '_full')
    wrote = fields.Nested('ArticleSerializer', many=True)


class ArticleSerializer(Serializer):
    class Meta:
        fields = ('_id', 'record', 'date', 'pmid', 'doi', 'authors', 'tags')
    authors = fields.Nested(AuthorSerializer, many=True, exclude=['wrote'])
    tags = fields.Nested('TagSerializer', many=True)


# Paginated serializers

class AuthorQuerySerializer(AuthorSerializer, PaginatedQuerySerializer):
    pass


class ArticleQuerySerializer(ArticleSerializer, PaginatedQuerySerializer):
    pass

