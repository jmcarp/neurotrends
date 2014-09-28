# -*- coding: utf-8 -*-

import pytest

from neurotrends.pattern import misc


def test_clean_unicode():
    assert misc.clean_unicode(u'os\u20442') == u'os/2'
    assert misc.clean_unicode(u'dunning\u2212kruger') == u'dunning-kruger'


def test_clean_delimiters():
    assert misc.clean_delimiters('bold-signal') == 'bold signal'
    assert misc.clean_delimiters('bold,signal') == 'bold signal'
    assert misc.clean_delimiters('bold\tsignal') == 'bold signal'
    assert misc.clean_delimiters('bold-  signal') == 'bold signal'


def test_clean():
    assert misc.clean(u'bold\u2212  signal') == 'bold signal'

