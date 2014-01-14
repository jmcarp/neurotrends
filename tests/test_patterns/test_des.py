
from neurotrends.pattern import des

from . import build_tests

build_tests(
    [des.block],
    [
        ('block design', {}),
        ('blocked paradigm', {}),
        ('epoch based', {}),
        ('epoched analysis', {}),
        # From PMID 21625502
        ('we used a blocked factorial design', {}),
    ]
)
