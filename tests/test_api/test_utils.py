# -*- coding: utf-8 -*-

import collections

import mock
import pytest
from tests.fixtures import scratch_models

from flask import Flask
from flask.ext.api import exceptions
from webargs import Arg, ValidationError
from webargs.flaskparser import FlaskParser
from modularodm import Q

from neurotrends import model
from neurotrends import config
from neurotrends.api import utils
from neurotrends.api import serializers


@pytest.fixture
def app():
    return Flask('test_app')


@pytest.fixture
def parser():
    return FlaskParser()


def test_bool_arg_true(app, parser):
    arg = utils.make_bool_arg()
    request = app.test_request_context('/?test_bool=true').request
    assert parser.parse_arg('test_bool', arg, request) is True


def test_bool_arg_false(app, parser):
    arg = utils.make_bool_arg()
    request = app.test_request_context('/?test_bool=false').request
    assert parser.parse_arg('test_bool', arg, request) is False


def test_bool_arg_invalid(app, parser):
    arg = utils.make_bool_arg()
    request = app.test_request_context('/?test_bool=nope').request
    with pytest.raises(ValidationError):
        parser.parse_arg('test_bool', arg, request)


def test_bool_arg_default(app, parser):
    arg = utils.make_bool_arg(default=True)
    request = app.test_request_context('/').request
    assert parser.parse_arg('test_bool', arg, request) is True



def test_get_record_by_id(scratch_models):
    article = model.Article()
    article.save()
    serialized = utils.get_record_by_id(
        article._id,
        model.Article,
        serializers.ArticleSerializer,
    )
    expected = serializers.ArticleSerializer(article).data
    assert serialized == expected


def test_get_record_by_id_not_found(scratch_models):
    with pytest.raises(exceptions.NotFound):
        utils.get_record_by_id(
            None,
            model.Article,
            serializers.ArticleSerializer
        )


def scratch_record_factory(collection, records):
    @pytest.yield_fixture
    def fixture(scratch_models):
        collection.insert(records)
        yield
        for record in records:
            collection.remove(record)
    return fixture


scratch_tag_author_counts = scratch_record_factory(
    config.tag_author_counts_collection,
    [
        {
            '_id': {
                'authorId': '12345',
                'label': 'smooth',
            },
            'value': 2,
        },
        {
            '_id': {
                'authorId': '12345',
                'label': 'normalize',
            },
            'value': 5,
        },
    ]
)


scratch_place_counts = scratch_record_factory(
    config.place_counts_collection,
    {'_id': 'London', 'value': 10}
)


scratch_tag_place_counts = scratch_record_factory(
    config.tag_place_counts_collection,
    [
        {
            '_id': {
                'place': 'London',
                'label': 'spm',
            },
            'value': 5,
        },
        {
            '_id': {
                'place': 'London',
                'label': 'fsl',
            },
            'value': 1,
        },
    ]
)


def test_get_tags_by_author(scratch_tag_author_counts):
    serialized = utils.get_tag_author_counts('12345')
    assert serialized == collections.OrderedDict([
        ('normalize', 5),
        ('smooth', 2),
    ])


def test_get_tags_by_place(scratch_tag_place_counts):
    serialized = utils.get_tag_place_counts('London', normalize=False)
    assert serialized == collections.OrderedDict([
        ('fsl', 1),
        ('spm', 5),
    ])


def test_get_tags_by_place_normalize(scratch_tag_place_counts, scratch_place_counts):
    serialized = utils.get_tag_place_counts('London', normalize=True)
    assert serialized == collections.OrderedDict([
        ('fsl', 0.1),
        ('spm', 0.5),
    ])


@pytest.fixture
def query_field_translator_default_operator():
    return utils.QueryFieldTranslator('year')


@pytest.fixture
def query_field_translator_custom_operator():
    return utils.QueryFieldTranslator('title', 'icontains')


def test_query_field_translator_operator_default(query_field_translator_default_operator):
    translator = query_field_translator_default_operator
    assert translator.field == 'year'
    assert translator.operator == 'eq'


def test_query_field_translator_operator_custom(query_field_translator_custom_operator):
    translator = query_field_translator_custom_operator
    assert translator.field == 'title'
    assert translator.operator == 'icontains'


def test_query_field_translator_translated_default(query_field_translator_default_operator):
    translator = query_field_translator_default_operator
    translated = translator('2007')
    assert translated.attribute == 'year'
    assert translated.operator == 'eq'
    assert translated.argument == '2007'


def test_query_field_translator_translated_custom(query_field_translator_custom_operator):
    translator = query_field_translator_custom_operator
    translated = translator('fmri')
    assert translated.attribute == 'title'
    assert translated.operator == 'icontains'
    assert translated.argument == 'fmri'


@pytest.fixture
def query_translator_empty():
    return utils.QueryTranslator(model.Article)


@pytest.fixture
def query_translator():
    return utils.QueryTranslator(
        model.Article,
        year=utils.QueryFieldTranslator('year'),
        title=utils.QueryFieldTranslator('title', 'icontains'),
    )


def capture_inputs(*args, **kwargs):
    return args, kwargs


@pytest.fixture
def patch_find(monkeypatch):
    mock_find = mock.Mock(side_effect=capture_inputs)
    monkeypatch.setattr(model.Article, 'find', mock_find)


def test_query_translator_empty(query_translator_empty, patch_find):
    assert query_translator_empty.translate({}) == ((None,), {})


def test_query_translator_no_kwargs(query_translator, patch_find):
    assert query_translator.translate({}) == ((None,), {})


def test_query_translator(query_translator, patch_find):
    kwargs = {
        'year': 2007,
        'title': 'fmri',
    }
    # Pull query from return value of `capture_inputs`
    translated = query_translator.translate(kwargs)[0][0]
    expected = Q('year', 'eq', 2007) & Q('title', 'icontains', 'fmri')
    # Hack: until `Query::__eq__` is implemented, use `__repr__` for comparison
    assert repr(translated) == repr(expected)


# Test dictionary helpers

def test_filter_dict():
    data = {key: key ** 2 for key in range(5)}
    predicate = lambda key, value: key % 2 == 0
    expected = {0: 0, 2: 4, 4: 16}
    assert expected == utils.filter_dict(data, predicate)


def test_sort_dict_keys():
    data = {key: -key ** 2 for key in range(5)}
    key = lambda pair: pair[0]
    result = utils.sort_dict(data, key)
    assert result.keys() == range(5)


def test_sort_dict_keys_reversed():
    data = {key: -key ** 2 for key in range(5)}
    key = lambda pair: pair[0]
    result = utils.sort_dict(data, key, reverse=True)
    assert result.keys() == range(5)[::-1]


def test_sort_dict_values():
    data = {key: -key ** 2 for key in range(5)}
    key = lambda pair: pair[1]
    result = utils.sort_dict(data, key)
    assert result.keys() == range(5)[::-1]

