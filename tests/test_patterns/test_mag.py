"""

"""

from neurotrends.pattern.mag.mag import ge, ge_context, varian
from neurotrends.pattern.mag.est_field_strength import field_strength

from . import build_tests

build_tests(
    field_strength,
    [
        ('field strength of 3.0 tesla', {'value': 3.0}),
        ('field strength of 3.0 T', {'value': 3.0}),
    ],
    [
        'field strength of 3.0 Tinkerbells',
        'field strength of 100 tesla',
    ]
)

build_tests(
    ge,
    [
        ('general electric', {}),
    ]
)

build_tests(
    ge_context,
    [
        ('GE scanner', {}),
    ],
    [
        'GE Hoffman',
    ]
)

build_tests(
    varian,
    [
        ('varian scanner', {}),
    ],
    [
        'analysis of variance',
    ]
)

