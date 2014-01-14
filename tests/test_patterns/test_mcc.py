"""

"""

from neurotrends.pattern.mcc import monte, monte_context

from . import build_tests

build_tests(
    [monte, monte_context],
    [
        ('alpha sim', {}),
        ('monte carlo correction', {}),
        ('clustsim', {}),
        ('3dclustsim', {}),
        # From PMID 23178958
        ('This extent threshold was computed using a Monte Carlo simulation', {}),
        # From PMID 19158105
        ('In a Monte Carlo simulation within the AFNI software package', {}),
    ],
    [
        'monte carlo simulation',
    ]
)
