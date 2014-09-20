# -*- coding: utf-8 -*-

import os
import re
import functools
import collections

from flask import request, url_for
from flask.ext.api import FlaskAPI, status, exceptions
from webargs.flaskparser import FlaskParser
from webargs import Arg
from modularodm import Q

from neurotrends.config import (
    stats_collection,
    tag_counts_collection,
)
from neurotrends import model

from . import serializers, settings, utils


app = FlaskAPI(__name__)
parser = FlaskParser()


ARTICLE_PAGE_NUM_DEFAULT  = 1
ARTICLE_PAGE_SIZE_DEFAULT = 20
ARTICLE_PAGE_SIZE_OPTIONS = [10, 20, 50]
ARTICLE_SORT_DEFAULT      = 'title'

AUTHOR_PAGE_NUM_DEFAULT   = 1
AUTHOR_PAGE_SIZE_DEFAULT  = 20
AUTHOR_PAGE_SIZE_OPTIONS  = [10, 20, 50]
AUTHOR_SORT_DEFAULT       = 'lastname'


# Query args

strip = lambda x: x.strip()
strip_lower = lambda x: x.strip().lower()


def query_article_authors(values):
    if not values:
        return None
    rules = [
        {'$elemMatch': {'$regex': value}}
        for value in values
    ]
    return Q('_lrecord.FAU', 'all', rules)


def query_article_tags(values):
    if not values:
        return None
    rules = [
        {'$elemMatch': {'label': value}}
        for value in values
    ]
    return Q('tags', 'all', rules)


def query_article_fetched(value):
    if value:
        return Q('verified.0', 'exists', True)
    return None


article_query_args = {
    'doi': Arg(str, use=strip),
    'pmid': Arg(str, use=strip),
    'title': Arg(str, use=strip_lower),
    'journal': Arg(str, use=strip_lower),
    'authors': Arg(str, multiple=True, use=strip_lower),
    'tags': Arg(str, multiple=True, use=strip_lower),
    'fetched': utils.make_bool_arg(default=True),
}

article_query_translator = utils.QueryTranslator(
    model.Article,
    doi=utils.QueryFieldTranslator('doi'),
    pmid=utils.QueryFieldTranslator('pmid'),
    title=utils.QueryFieldTranslator('_lrecord.TI', 'contains'),
    journal=utils.QueryFieldTranslator('_lrecord.JT', 'contains'),
    authors=query_article_authors,
    tags=query_article_tags,
    fetched=query_article_fetched,
)


author_query_args = {
    'fullname': Arg(str, use=strip_lower),
}

author_query_translator = utils.QueryTranslator(
    model.Author,
    fullname=utils.QueryFieldTranslator('_lfull', 'contains'),
)

# Sorting and paging args

article_page_args = {
    'page_num': Arg(
        int,
        validate=lambda value: value > 0,
        default=ARTICLE_PAGE_NUM_DEFAULT,
    ),
    'page_size': Arg(
        int,
        validate=lambda value: value in ARTICLE_PAGE_SIZE_OPTIONS,
        default=ARTICLE_PAGE_SIZE_DEFAULT,
    ),
}

article_sort_args = {
    'sort': Arg(str, default=ARTICLE_SORT_DEFAULT),
}

article_sort_translator = utils.SortTranslator(
    title=utils.SortFieldTranslator('_lrecord.TI'),
    journal=utils.SortFieldTranslator('_lrecord.JT'),
)


author_page_args = {
    'page_num': Arg(
        int,
        validate=lambda value: value > 0,
        default=AUTHOR_PAGE_NUM_DEFAULT,
    ),
    'page_size': Arg(
        int,
        validate=lambda value: value in AUTHOR_PAGE_SIZE_OPTIONS,
        default=AUTHOR_PAGE_SIZE_DEFAULT,
    ),
}

author_sort_args = {
    'sort': Arg(str, default=AUTHOR_SORT_DEFAULT),
}

author_sort_translator = utils.SortTranslator(
    lastname=utils.SortFieldTranslator('last'),
)


tag_args = {
    'label': Arg(
        str,
        use=lambda value: value.strip()
    ),
}

tag_count_args = {
    'normalize': utils.make_bool_arg(default=False),
}


place_count_args = {
    'normalize': utils.make_bool_arg(default=False),
}


# View functions

@app.route('/articles/<article_id>/', methods=['GET'])
def article(article_id):
    return utils.get_record_by_id(
        article_id,
        model.Article,
        serializers.ArticleSerializer,
    )


@app.route('/articles/', methods=['GET'])
def articles():
    query_args = parser.parse(article_query_args, request)
    query = article_query_translator.translate(query_args)
    sort_args = parser.parse(article_sort_args, request)
    sort_keys = article_sort_translator.translate(sort_args.get('sort'))
    query = query.sort(*sort_keys)
    page_args = parser.parse(article_page_args, request)
    paginator = serializers.Paginator(query, page_args['page_size'])
    page = paginator.get_page(page_args['page_num'])
    serialized = serializers.ArticleQuerySerializer(page, many=True)
    return serialized.data


@app.route('/authors/<author_id>/', methods=['GET'])
def author(author_id):
    return utils.get_record_by_id(
        author_id,
        model.Author,
        serializers.AuthorSerializer,
    )


@app.route('/authors/<author_id>/tags/', methods=['GET'])
def author_tags(author_id):
    args = parser.parse(tag_count_args, request)
    counts = utils.get_tag_author_counts(author_id)
    if counts is None:
        abort(httplib.NOT_FOUND)
    return collections.OrderedDict([
        ('author', author_id),
        ('counts', counts),
    ])


@app.route('/authors/', methods=['GET'])
def authors():
    query_args = parser.parse(author_query_args, request)
    query = author_query_translator.translate(query_args)
    sort_args = parser.parse(author_sort_args, request)
    sort_keys = author_sort_translator.translate(sort_args.get('sort'))
    query = query.sort(*sort_keys)
    page_args = parser.parse(author_page_args, request)
    paginator = serializers.Paginator(query, page_args['page_size'])
    page = paginator.get_page(page_args['page_num'])
    serialized = serializers.AuthorQuerySerializer(page, many=True)
    return serialized.data


@app.route('/stats/', methods=['GET'])
def stats():
    data = stats_collection.find_one({'_id': 'stats'})
    del data['_id']
    return data


@app.route('/tags/', methods=['GET'])
def tags():
    """List tags.

    """
    query = {}
    args = parser.parse(tag_args, request)
    label = args.get('label')
    if label:
        pattern = re.compile(re.escape(args['label']), re.I)
        query.update({'_id': {'$regex': pattern}})
    tags = tag_counts_collection.find(query)
    return [
        collections.OrderedDict([
            ('label', tag['_id']),
            ('count', int(tag['value'])),
        ])
        for tag in tags
    ]


@app.route('/tags/<tag_id>/counts/', methods=['GET'])
def tag_counts(tag_id):
    """Get tag counts by year.

    """
    tag_id = tag_id.strip().lower()
    args = parser.parse(tag_count_args, request)
    counts = utils.get_tag_counts(tag_id, normalize=args['normalize'])
    return collections.OrderedDict([
        ('label', tag_id),
        ('counts', counts),
    ])


@app.route('/places/tags/top/', methods=['GET'])
def tag_counts_top_places():
    args = parser.parse(place_count_args, request)
    places = utils.get_places(limit=10)
    return collections.OrderedDict([
        (
            place['_id'],
            utils.get_tag_place_counts(
                place['_id'],
                normalize=args['normalize'],
            )
        )
        for place in places
    ])


# Set up CORS headers

@app.after_request
def add_cors_headers(response):
    response.headers.extend({
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST',
    })
    return response


# Configure application

if os.environ.get('NEUROTRENDS_ENV') == 'prod':
    app.config.from_object(settings.ProdConfig)
else:
    app.config.from_object(settings.DevConfig)

