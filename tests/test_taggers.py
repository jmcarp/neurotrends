import unittest
from nose.tools import *

from neurotrends.tagger import Tag, CustomTagger, RexTagger

class TestCustomTagger(unittest.TestCase):

    def setUp(self):
        def tag_func(text):
            return {
                'value': text[::-1],
                'context': text,
                'span': (0, len(text) - 1)
            }
        self.tagger = CustomTagger(
            'custom', tag_func
        )

    def test(self):
        text = 'asdf'
        result = self.tagger.tag(text)
        assert_equal(
            result,
            Tag({
                'label': 'custom',
                'value': 'fdsa',
                'context': 'asdf',
                'span': (0, len(text) - 1),
            })
        )

class TestRexTagger(unittest.TestCase):

    def setUp(self):
        self.tagger = RexTagger(
            'foo',
            [
                r'foo',
            ]
        )

    def test_match(self):
        text = 'foo bar baz'
        tag = self.tagger.tag(text)
        assert_equal(
            tag,
            Tag({
                'label': 'foo',
                'context': 'foo bar baz',
                'span': (0, 3),
            })
        )
