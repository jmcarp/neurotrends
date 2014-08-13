# -*- coding: utf-8 -*-

import pytest

from tests.fixtures import test_app, scratch_models

from neurotrends import model


def test_article(test_app, scratch_models):
    article = model.Article()
    article.save()
    resp = test_app.get('/article/{0}/'.format(article._id))
    assert resp.json['_id'] == article._id


def test_article_not_found(test_app, scratch_models):
    resp = test_app.get('/article/missing/', expect_errors=True)
    assert resp.status_code == 404


def test_author(test_app, scratch_models):
    author = model.Author()
    author.save()
    resp = test_app.get('/author/{0}/'.format(author._id))
    assert resp.json['_id'] == author._id


def test_author_not_found(test_app, scratch_models):
    resp = test_app.get('/author/missing/', expect_errors=True)
    assert resp.status_code == 404

