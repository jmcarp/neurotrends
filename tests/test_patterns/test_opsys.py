"""

"""

from neurotrends.pattern.opsys import windows_context

from . import build_tests

build_tests(
    windows_context,
    [
        ('windows xp', {}),
        ('windows operating system', {}),
    ],
    [
        'time windows',
        # Shouldn't match "nt" within another word
        'windows untested',
    ]
)
