"""

"""

import inspect
from nose.tools import *

from neurotrends.tagger import TagGroup, tag

@nottest
def build_test(module, taggers, input, output):
    def test():
        tags = tag(taggers, input)
        if output is not None:
            assert_true(tags is not None)
            if isinstance(tags, list):
                assert_equal(len(tags), 1)
                tags = tags[0]
            for key, value in output.iteritems():
                assert_equal(
                    tags[key], value
                )
        else:
            assert_true(tags is None or len(tags) == 0)
    idx = 0
    while True:
        test_name = 'test_{0}_{1}'.format(taggers.taggers[0].label, idx)
        if not hasattr(module, test_name):
            break
        idx += 1
    test.__name__ = test_name
    setattr(module, test_name, test)

@nottest
def build_tests(taggers, positives, negatives=None):
    if not isinstance(taggers, list):
        taggers = [taggers]
    taggers = TagGroup(taggers, '')
    caller = inspect.stack()[1]
    module = inspect.getmodule(caller[0])
    for positive in positives:
        build_test(module, taggers, positive[0], positive[1])
    for negative in negatives or []:
        build_test(module, taggers, negative, None)
