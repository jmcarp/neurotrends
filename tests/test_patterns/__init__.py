# -*- coding: utf-8 -*-

from neurotrends.tagger import TagGroup, tag


def check_taggers(taggers, input, expected):
    tag_group = TagGroup(taggers, '')
    tags = tag(tag_group, input)
    if expected is not None:
        assert tags is not None
        if isinstance(tags, list):
            assert len(tags) == 1
            tags = tags[0]
        for key, value in expected.iteritems():
            assert tags[key] == value
    else:
        assert (tags is None or tags == [])

