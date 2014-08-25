# -*- coding: utf-8 -*-

import pytest

from tests import utils

from neurotrends.api import serializers


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



def test_tag_serializer():
    tag = TagFactory()
    serialized = serializers.TagSerializer(tag).data
    assert serialized['label'] == 'spm'
    assert serialized['version'] is None
    assert serialized['value'] is None


def test_tag_serializer_version():
    tag = TagFactory(version='2')
    serialized = serializers.TagSerializer(tag).data
    assert serialized['version'] == '2'


def test_tag_serializer_value():
    tag = TagFactory(value='2')
    serialized = serializers.TagSerializer(tag).data
    assert serialized['value'] == '2'

