# -*- coding: utf-8 -*-

import pytest

from neurotrends.pattern.pkg import spm, fsl, afni, surfer, voyager

from . import check_taggers


@pytest.mark.parametrize('input, expected', [
    ('spm', {'version': '?'}),
    ('statistical parametric mapping', {'version': '?'}),
    ('spm 5', {'version': '5'}),
    ('spm software version 5', {'version': '5'})
])
def test_spm(input, expected):
    check_taggers([spm], input, expected)


@pytest.mark.parametrize('input, expected', [
    ('fsl', {'version': '?'}),
    ('fmrib software library', {'version': '?'}),
    ('fmribs software library', {'version': '?'}),
    ("fmrib's software library", {'version': '?'}),
    ('fsl 4.1.9', {'version': '4.1.9'}),
    ('fsl 4.1.0', {'version': '4.1'}),
])
def test_fsl(input, expected):
    check_taggers([fsl], input, expected)


@pytest.mark.parametrize('input, expected', [
    ('afni', {'version': '?'}),
    ('analysis of functional neuroimages', {'version': '?'}),
    ('afni version 2.31', {'version': '2.31'}),
    ('afni version 2008_07_18_1710', {'version': '2008_07_18_1710'}),
])
def test_afni(input, expected):
    check_taggers([afni], input, expected)


@pytest.mark.parametrize('input, expected', [
    ('freesurfer', {'version': '?'}),
    ('free surfer', {'version': '?'}),
    ('freesurfer 4.0.0', {'version': '4'}),
    ('freesurfer 4.0.1', {'version': '4.0.1'}),
    ('freesurfer (4.0.1)', {'version': '4.0.1'}),
    ('freesurfer (v4.0.1)', {'version': '4.0.1'}),
    ('freesurfer (version 4.0.1)', {'version': '4.0.1'}),
])
def test_surfer(input, expected):
    check_taggers([surfer], input, expected)


@pytest.mark.parametrize('input, expected', [
    ('brainvoyager', {'version': '?'}),
    ('brain voyager', {'version': '?'}),
    ('brain voyager 3.7', {'version': '3.7'}),
    ('brain voyager qx 2.1', {'version': '2.1'}),
    ('brain voyager 2000 (version 4.9)', {'version': '4.9'}),
])
def test_voyager(input, expected):
    check_taggers([voyager], input, expected)

