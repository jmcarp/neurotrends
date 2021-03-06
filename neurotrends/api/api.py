#!/usr/bin/env python
# encoding: utf-8

import os
import functools
import collections

from flask import request, url_for
from flask.ext.api import FlaskAPI, status, exceptions
from flask.ext.cors import CORS

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
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app)

parser = FlaskParser()


ARTICLE_PAGE_NUM_DEFAULT  = 1
ARTICLE_PAGE_SIZE_DEFAULT = 20
ARTICLE_PAGE_SIZE_OPTIONS = [10, 20, 50]
ARTICLE_SORT_DEFAULT      = 'title'

AUTHOR_PAGE_NUM_DEFAULT   = 1
AUTHOR_PAGE_SIZE_DEFAULT  = 20
AUTHOR_PAGE_SIZE_OPTIONS  = [10, 20, 50]
AUTHOR_SORT_DEFAULT       = 'lastname'

STATS_FIELDS = ['firstYear', 'lastYear', 'numArticles', 'numTags']


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
    'label': Arg(str, default='', use=lambda value: value.strip()),
    'versions': utils.make_bool_arg(default=False),
}

tag_count_args = {
    'normalize': utils.make_bool_arg(default=False),
}

order_reverse_map = {
    'asc': False,
    'desc': True,
}

tag_distance_args = {
    'metric': Arg(str, default='cosine'),
    'reverse': Arg(
        bool,
        use=lambda value: order_reverse_map.get(value),
        validate=lambda value: value is not None,
        source='order',
        default=False,
    ),
}


version_count_args = {
    'normalize': utils.make_bool_arg(default=False),
    'threshold': Arg(float, default=0.0),
}


place_count_args = {
    'normalize': utils.make_bool_arg(default=False),
}


extract_args = {
    'text': Arg(
        unicode,
        required=True,
        use=lambda value: value.strip()
    ),
}


# View functions

@app.route('/', methods=['GET'])
def index():
    return {
        'message': 'Welcome to the NeuroTrends API',
        '_links': collections.OrderedDict([
            ('articles', url_for('articles', _external=True)),
            ('authors', url_for('authors', _external=True)),
            ('statistics', url_for('stats', _external=True)),
        ]),
    }


@app.route('/articles/<article_id>/', methods=['GET'])
def article(article_id):
    return utils.get_record_by_id(
        article_id,
        model.Article,
        serializers.ArticleSchema,
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
    serialized = serializers.article_query_schema.dump(page)
    return serialized.data


@app.route('/authors/<author_id>/', methods=['GET'])
def author(author_id):
    return utils.get_record_by_id(
        author_id,
        model.Author,
        serializers.AuthorSchema,
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
    result = serializers.author_query_schema.dump(page)
    return result.data


@app.route('/stats/', methods=['GET'])
def stats():
    data = stats_collection.find_one({'_id': 'stats'})
    return collections.OrderedDict([
        (key, data[key])
        for key in STATS_FIELDS
    ])


@app.route('/tags/', methods=['GET'])
def tags():
    """List tags.
    """
    args = parser.parse(tag_args, request)
    return utils.get_tags_by_label(args['label'], args['versions'])


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


@app.route('/tags/<tag_id>/versions/', methods=['GET'])
def tag_version_counts(tag_id):
    tag_id = tag_id.strip().lower()
    args = parser.parse(version_count_args, request)
    counts = utils.get_tag_version_counts(
        tag_id,
        normalize=args['normalize'],
        threshold=args['threshold'],
    )
    return collections.OrderedDict([
        ('label', tag_id),
        ('counts', counts),
    ])


@app.route('/tags/<tag_id>/distances/', methods=['GET'])
def get_tag_distances(tag_id):
    """Get distances between `tag_id` and all other tags using the requested
    distance metric.
    """
    tag_id = tag_id.strip().lower()
    args = parser.parse(tag_distance_args, request)
    distances = utils.get_tag_distances(tag_id, **args)
    return collections.OrderedDict([
        ('tag', tag_id),
        ('distances', distances),
    ])


@app.route('/places/<place_id>/', methods=['GET'])
def tag_counts_place(place_id):
    """Get tag counts by place.
    """
    place_id = place_id.strip()
    args = parser.parse(place_count_args, request)
    counts = utils.get_tag_place_counts(
        place_id,
        normalize=args['normalize'],
    )
    return collections.OrderedDict([
        ('place', place_id),
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


@app.route('/extract/', methods=['POST'])
def extract_tags():
    args = parser.parse(extract_args, request, targets=('json',))
    tags = utils.extract_tags(args['text'])
    return {'tags': tags}


# Configure application

if os.environ.get('NEUROTRENDS_ENV') == 'prod':
    app.config.from_object(settings.ProdConfig)
else:
    app.config.from_object(settings.DevConfig)

