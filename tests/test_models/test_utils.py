import inspect
from nose.tools import *

from neurotrends.model.utils import get_institution

@nottest
def build_test(name, func, expected, *args, **kwargs):
    def test():
        actual = func(*args, **kwargs)
        assert_equal(actual, expected)
    idx = 0
    caller = inspect.stack()[1]
    module = inspect.getmodule(caller[0])
    while True:
        test_name = 'test_{0}_{1}'.format(name, idx)
        if not hasattr(module, test_name):
            break
        idx += 1
    test.__name__ = test_name
    setattr(module, test_name, test)

@nottest
def build_institution_tests(fixtures):
    for fixture in fixtures:
        build_test(
            'institution',
            get_institution,
            fixture[1],
            fixture[0],
        )

build_institution_tests([
    (
        'Department of Psychology, University of Michigan, Ann Arbor, MI, USA.',
        'University of Michigan',
    ),
    (
        'Imaging Research Center, University of Texas at Austin, Austin, TX 78712. malecek@utexas.edu poldrack@utexas.edu www.poldracklab.org.',
        'University of Texas at Austin',
    ),
    (
        'University of Illinois at Urbana-Champaign, USA. Electronic address: mfabiani@illinois.edu.',
        'University of Illinois at Urbana-Champaign',
    ),
    (
        'Department of Psychology, University of Victoria, Victoria, British Columbia, V8W 3P5, Canada. holroyd@uvic.ca http://web.uvic.ca/~lccl/',
        'University of Victoria',
    ),
    (
        'Department of Pharmacology, Graduate Program University of Virginia School of Medicine, Charlottesville, Virginia, U.S.A',
        'University of Virginia',
    ),
])
