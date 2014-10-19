# -*- coding: utf-8 -*-
from flask import url_for

import pytest

from tests import utils
from tests.fixtures import scratch_models  # noqa
from tests.test_models.factories import AuthorFactory, ArticleFactory

from neurotrends.api import serializers
from neurotrends.api.api import app
from neurotrends.model.article import Article
from neurotrends.model.author import Author


class TagFactory(utils.DictFactory):

    label = 'spm'
    category = 'tool'
    span = {
        'html': [100, 102],
        'pdf': [200, 202],
    }
    group = {
        'html': 'spm',
        'pdf': 'spm',
    }
    context = {
        'html': 'we used spm',
        'pdf': 'we used spm',
    }


class TestTagSchema:

    @pytest.fixture
    def schema(self):
        return serializers.TagSchema()

    def test_tag_serializer(self, schema):
        tag = TagFactory()
        serialized = schema.dump(tag).data
        assert serialized['label'] == 'spm'
        assert serialized['version'] is None
        assert serialized['value'] is None

    def test_version(self, schema):
        tag = TagFactory(version='2')
        serialized = schema.dump(tag).data
        assert serialized['version'] == '2'

    def test_value(self, schema):
        tag = TagFactory(value='2')
        serialized = schema.dump(tag).data
        assert serialized['value'] == '2'

@pytest.mark.usefixtures('scratch_models')
class TestAuthorSchema:

    @pytest.fixture
    def author(self):
        return AuthorFactory()

    @pytest.fixture
    def schema(self):
        return serializers.AuthorSchema()

    def test_author_schema_fields(self, schema, author):
        with app.test_request_context():
            data = schema.dump(author).data
            expected_url = url_for('author', author_id=author._id, _external=True)
        assert data['url'] == expected_url
        assert data['_id'] == author._id
        assert data['full'] == author._full
        assert data['first'] == author.first
        assert data['middle'] == author.middle
        assert data['suffix'] == author.suffix

@pytest.mark.usefixtures('scratch_models')
class TestArticleSchema:

    @pytest.fixture
    def article(self):
        return ArticleFactory(
            authors=[AuthorFactory(), AuthorFactory()],
            tags=[TagFactory(), TagFactory()]
        )

    @pytest.fixture
    def schema(self):
        return serializers.ArticleSchema()

    def test_article_schema_basic_fields(self, schema, article):
        with app.test_request_context():
            data = schema.dump(article).data
            expected_url = url_for('article', article_id=article._id, _external=True)
        assert data['url'] == expected_url
        assert data['_id'] == article._id
        assert data['record'] == article.record
        assert data['date'] == article.date
        assert data['pmid'] == article.pmid
        assert data['doi'] == article.doi

    def test_nested_authors(self, schema, article):
        data = schema.dump(article).data
        assert len(data['authors']) == 2
        first_author = article.authors[0]
        author_schema = serializers.AuthorSchema()
        author_serialized = author_schema.dump(first_author).data
        assert data['authors'][0] == author_serialized

    def test_nested_tags(self, schema, article):
        data = schema.dump(article).data
        assert len(data['tags']) == 2
        first_tag = article.tags[0]
        tag_schema = serializers.TagSchema()
        tag_serialized = tag_schema.dump(first_tag).data
        assert data['tags'][0] == tag_serialized


@pytest.mark.usefixtures('scratch_models')
class TestArticleQuerySchema:

    @pytest.fixture
    def scratch_articles(self):
        for _ in range(20):
            ArticleFactory()

    @pytest.fixture
    def schema(self):
        return serializers.ArticleQuerySchema(many=True)

    @pytest.fixture
    def query(self, scratch_articles):
        return Article.find()

    @pytest.fixture
    def paginator(self, query):
        return serializers.Paginator(query, page_size=5)

    @pytest.fixture
    def page(self, paginator):
        return paginator.get_page(2)

    def test_has_pages(self, schema, page, query, paginator):
        with app.test_request_context():
            data = schema.dump(page).data
        assert '?page_num=1' in data['prev']
        assert '?page_num=3' in data['next']
        assert data['count'] == query.count()

    def test_results(self, schema, page, query, paginator):
        with app.test_request_context():
            data = schema.dump(page).data
        results = data['results']
        assert len(results) == paginator.page_size
        first_article = page.contents[0]
        article_schema = serializers.ArticleSchema()
        expected = article_schema.dump(first_article).data
        assert results[0]['_id'] == expected['_id']


@pytest.mark.usefixtures('scratch_models')
class TestAuthorQuerySchema:

    @pytest.fixture
    def scratch_articles(self):
        for _ in range(20):
            AuthorFactory()

    @pytest.fixture
    def schema(self):
        return serializers.AuthorQuerySchema(many=True)

    @pytest.fixture
    def query(self, scratch_articles):
        return Author.find()

    @pytest.fixture
    def paginator(self, query):
        return serializers.Paginator(query, page_size=5)

    @pytest.fixture
    def page(self, paginator):
        return paginator.get_page(2)

    def test_has_pages(self, schema, page, query, paginator):
        with app.test_request_context():
            data = schema.dump(page).data
        assert '?page_num=1' in data['prev']
        assert '?page_num=3' in data['next']
        assert data['count'] == query.count()

    def test_results(self, schema, page, query, paginator):
        with app.test_request_context():
            data = schema.dump(page).data
        results = data['results']
        assert len(results) == paginator.page_size
        first_author = page.contents[0]
        author_schema = serializers.AuthorSchema()
        expected = author_schema.dump(first_author).data
        assert results[0]['_id'] == expected['_id']
