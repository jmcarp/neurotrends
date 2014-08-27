# -*- coding: utf-8 -*-

from tests.test_models import factories
from tests.fixtures import scratch_models


def test_record_factory(scratch_models):
    record = factories.RecordFactory()
    assert record['TI']
    assert record['JT']


def test_author_factory(scratch_models):
    author = factories.AuthorFactory()
    assert author.last
    assert author.first
    assert author.middle


def test_article_factory(scratch_models):
    article = factories.ArticleFactory()
    assert article.pmid
    assert article.doi
    assert article.record['TI']
    assert article.record['JT']
    assert len(article.authors) == 3

