# -*- coding: utf-8 -*-

import json
import pytest

from tests.fixtures import test_app, scratch_models

from neurotrends import model

def test_articles_returns_200_response(test_app, scratch_models):
    for _ in range(3):
        model.Article().save()
    resp = test_app.get('/articles/')
    assert resp.status_code == 200

def test_article(test_app, scratch_models):
    article = model.Article()
    article.save()
    resp = test_app.get('/articles/{0}/'.format(article._id))
    assert resp.json['_id'] == article._id


def test_article_not_found(test_app, scratch_models):
    resp = test_app.get('/articles/missing/', expect_errors=True)
    assert resp.status_code == 404


def test_author(test_app, scratch_models):
    author = model.Author()
    author.save()
    resp = test_app.get('/authors/{0}/'.format(author._id))
    assert resp.json['_id'] == author._id

def test_authors_returns_200_response(test_app, scratch_models):
    for _ in range(3):
        model.Author().save()
    resp = test_app.get('/authors/')
    assert resp.status_code == 200

def test_author_not_found(test_app, scratch_models):
    resp = test_app.get('/authors/missing/', expect_errors=True)
    assert resp.status_code == 404


def test_extract_tags(test_app):
    text = 'we used slice timing correction in SPM 8'
    resp = test_app.post(
        '/extract/',
        params=json.dumps({'text': text}),
        headers={'Content-Type': 'application/json'},
    )
    tags = resp.json['tags']
    assert len(tags) == 2
    assert set([tag['label'] for tag in tags]) == set(('stc', 'spm'))


def test_extract_tags_with_no_text_raises_400(test_app):
    resp = test_app.post('/extract/', expect_errors=True)
    assert resp.status_code == 400

