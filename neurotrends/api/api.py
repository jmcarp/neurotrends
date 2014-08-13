# -*- coding: utf-8 -*-

import os
import re
import functools

from flask import request, url_for
from flask.ext.api import FlaskAPI, status, exceptions
from webargs.flaskparser import FlaskParser
from webargs import Arg
from modularodm import Q

from neurotrends import model

from . import serializers
from . import settings
from . import utils


app = FlaskAPI(__name__)
parser = FlaskParser()


ARTICLE_PAGE_NUM_DEFAULT  = 1
ARTICLE_PAGE_SIZE_DEFAULT = 20
ARTICLE_PAGE_SIZE_OPTIONS = [10, 20, 50]
ARTICLE_SORT_DEFAULT      = 'title'

AUTHOR_PAGE_NUM_DEFAULT   = 1
AUTHOR_PAGE_SIZE_DEFAULT  = 20
AUTHOR_PAGE_SIZE_OPTIONS  = [10, 20, 50]
AUTHOR_SORT_DEFAULT       = 'last'


# Query translators

# TODO: Consider searching on `record.AU` instead
def query_article_authors(value):
    author_query = model.Author.find(Q('last', 'icontains', value))
    author_ids = author_query._to_primary_keys()
    return Q('authors', 'all', author_ids)


def query_article_tags(value):
    rules = [
        {'$elemMatch': {'label': label.strip()}}
        for label in value.split(',')
    ]
    return Q('tags', 'all', rules)


article_query_translator = utils.QueryTranslator(
    model.Article,
    doi=utils.QueryFieldTranslator('doi'),
    pmid=utils.QueryFieldTranslator('pmid'),
    title=utils.QueryFieldTranslator('record.TI', 'icontains'),
    journal=utils.QueryFieldTranslator('record.JT', 'icontains'),
    authors=query_article_authors,
    tags=query_article_tags,
)

author_query_translator = utils.QueryTranslator(
    model.Author,
    name=utils.QueryFieldTranslator('_full', 'icontains'),
)

article_sort_translator = utils.SortTranslator(
    title=utils.SortFieldTranslator('_lrecord.TI'),
    journal=utils.SortFieldTranslator('_lrecord.JT'),
)

author_sort_translator = utils.SortTranslator(
    lastname=utils.SortFieldTranslator('last'),
)


# Query filters

article_page_args = {
    'page_num': Arg(
        int,
        validate=lambda value: value > 1,
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

author_page_args = {
    'page_num': Arg(
        int,
        validate=lambda value: value > 1,
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


# View functions

@app.route('/article/<article_id>/', methods=['GET'])
def article(article_id):
    return utils.get_record_by_id(
        article_id,
        model.Article,
        serializers.ArticleSerializer,
    )


@app.route('/articles/', methods=['GET'])
def articles():
    query = article_query_translator.translate(request.args)
    sort_args = parser.parse(article_sort_args, request)
    sort_keys = article_sort_translator.translate(sort_args.get('sort'))
    query = query.sort(*sort_keys)
    page_args = parser.parse(article_page_args, request)
    paginator = serializers.Paginator(query, page_args['page_size'])
    page = paginator.get_page(page_args['page_num'])
    serialized = serializers.ArticleQuerySerializer(page, many=True)
    return serialized.data


@app.route('/author/<author_id>/', methods=['GET'])
def author(author_id):
    return utils.get_record_by_id(
        author_id,
        model.Author,
        serializers.AuthorSerializer,
    )


@app.route('/authors/', methods=['GET'])
def authors():
    query = author_query_translator.translate(request.args)
    sort_args = parser.parse(author_sort_args, request)
    sort_keys = author_sort_translator.translate(sort_args.get('sort'))
    query = query.sort(*sort_keys)
    page_args = parser.parse(author_page_args, request)
    paginator = serializers.Paginator(query, page_args['page_size'])
    page = paginator.get_page(page_args['page_num'])
    serialized = serializers.AuthorQuerySerializer(page, many=True)
    return serialized.data


# Configure application

if os.environ.get('NEUROTRENDS_ENV') == 'prod':
    app.config.from_object(settings.ProdConfig)
else:
    app.config.from_object(settings.DevConfig)

