# -*- coding: utf-8 -*-

import pytest
from webtest_plus import TestApp

from tests.utils import TestDatabase
from neurotrends.api.api import app


@pytest.fixture
def test_app():
    return TestApp(app)


@pytest.yield_fixture(scope='module')
def scratch_models():
    with TestDatabase('neurotrends_test'):
        yield

