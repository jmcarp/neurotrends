import re

import unittest
from nose.tools import *

from neurotrends.tagger import rex_compile, rex_flex, rex_ctx


class TestRexCompile(unittest.TestCase):

    def test_compile_pattern(self):
        rex = rex_compile(r'foo', flags=re.I)
        assert_equal(rex.pattern, r'foo')
        assert_equal(rex.flags, re.I)

    def test_compile_rex(self):
        rex = rex_compile(re.compile(r'foo', flags=re.I))
        assert_equal(rex.pattern, r'foo')
        assert_equal(rex.flags, re.I)


class TestRexFlex(unittest.TestCase):

    def test_search_pattern(self):
        result = rex_flex(r'foo', 'foo')
        assert_equal(
            bool(result),
            bool(re.search(r'foo', 'foo'))
        )

    def test_search_rex(self):
        result = rex_flex(re.compile(r'foo', re.I), 'foo')
        assert_equal(
            bool(result),
            bool(re.search(r'foo', 'foo'))
        )

    def test_search_rex_ignore_flags(self):
        """  """
        result = rex_flex(re.compile('foo'), 'FOO')
        assert_false(result)

    def test_finditer(self):
        result = rex_flex(r'foo', 'foo foo foo', fun=re.finditer)
        assert_equal(
            len(list(result)),
            3
        )

    def test_pad(self):
        """  """
        result = rex_flex('\Wfoo\W', 'foo')
        assert_true(result)


class TestRexCtx(unittest.TestCase):

    def setUp(self):
        self.pattern = r'bar'
        self.text = 'foo bar baz'

    def test_match(self):
        match = rex_flex(self.pattern, self.text)
        result = rex_ctx(match, self.text)
        assert_equal(result[0], self.text)
        assert_equal(result[1], ((4, 7)))

    def test_nomatch(self):
        result = rex_ctx(txt=self.text, ptn=self.pattern)
        assert_equal(result[0], self.text)
        assert_equal(result[1], (4, 7))

    def test_nchar(self):
        result = rex_ctx(txt=self.text, ptn=self.pattern, nchar=2)
        assert_equal(
            result[0],
            'o bar b'
        )
        assert_equal(
            result[1],
            (4, 7)
        )

    def test_nchar_pre(self):
        result = rex_ctx(txt=self.text, ptn=self.pattern, nchar_pre=2)
        assert_equal(
            result[0],
            'o bar baz'
        )
        assert_equal(
            result[1],
            (4, 7)
        )

    def test_nchar_post(self):
        result = rex_ctx(txt=self.text, ptn=self.pattern, nchar_post=2)
        assert_equal(
            result[0],
            'foo bar b'
        )
        assert_equal(
            result[1],
            (4, 7)
        )

    def test_nchar_pre_zero(self):
        """Regression test. Check for bug by which `nchar_pre=0` is equivalent
        to `nchar_pre=None`.

        """
        result = rex_ctx(txt=self.text, ptn=self.pattern, nchar_pre=0)
        assert_equal(
            result[0],
            'bar baz'
        )
        assert_equal(
            result[1],
            (4, 7)
        )

    def test_nchar_post_zero(self):
        """Regression test. Check for bug by which `nchar_post=0` is equivalent
        to `nchar_post=None`.

        """
        result = rex_ctx(txt=self.text, ptn=self.pattern, nchar_post=0)
        assert_equal(
            result[0],
            'foo bar'
        )
        assert_equal(
            result[1],
            (4, 7)
        )


def test_rex_named():

    pass
