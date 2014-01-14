"""

"""

from neurotrends.pattern.pkg import spm, fsl, afni, surfer, voyager

from . import build_tests

build_tests(
    spm,
    [
        ('spm', {'version': '?'}),
        ('statistical parametric mapping', {'version': '?'}),
        ('spm 5', {'version': '5'}),
        ('spm software version 5', {'version': '5'})
    ]
)

build_tests(
    fsl,
    [
        ('fsl', {'version': '?'}),
        ('fmrib software library', {'version': '?'}),
        ('fmribs software library', {'version': '?'}),
        ("fmrib's software library", {'version': '?'}),
        ('fsl 4.1.9', {'version': '4.1.9'}),
        ('fsl 4.1.0', {'version': '4.1'}),
    ]
)

build_tests(
    afni,
    [
        ('afni', {'version': '?'}),
        ('analysis of functional neuroimages', {'version': '?'}),
        ('afni version 2.31', {'version': '2.31'}),
        ('afni version 2008_07_18_1710', {'version': '2008_07_18_1710'}),
    ]
)

build_tests(
    surfer,
    [
        ('freesurfer', {'version': '?'}),
        ('free surfer', {'version': '?'}),
        ('freesurfer 4.0.0', {'version': '4'}),
        ('freesurfer 4.0.1', {'version': '4.0.1'}),
        ('freesurfer (4.0.1)', {'version': '4.0.1'}),
        ('freesurfer (v4.0.1)', {'version': '4.0.1'}),
        ('freesurfer (version 4.0.1)', {'version': '4.0.1'}),
    ]
)

build_tests(
    voyager,
    [
        ('brainvoyager', {'version': '?'}),
        ('brain voyager', {'version': '?'}),
        ('brain voyager 3.7', {'version': '3.7'}),
        ('brain voyager qx 2.1', {'version': '2.1'}),
        ('brain voyager 2000 (version 4.9)', {'version': '4.9'}),
    ]
)