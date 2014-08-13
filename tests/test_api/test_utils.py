# -*- coding: utf-8 -*-

import mock
import pytest
from tests.fixtures import scratch_models

from flask.ext.api import exceptions
from modularodm import Q

from neurotrends import model
from neurotrends.api import utils
from neurotrends.api import serializers


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

