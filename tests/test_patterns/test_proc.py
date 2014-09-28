# -*- coding: utf-8 -*-

import pytest

from neurotrends.pattern.proc import taggers
from neurotrends.pattern.proc.est_highpass_cutoff import highpass_cutoff
from neurotrends.pattern.proc.est_smooth_kernel import smooth_kernel

from . import check_taggers

@pytest.mark.parametrize('input, expected', [
    # Positives
    ('slice timing correction', {}),
    ('correction for differences in slice timing', {}),
    ('slice dependent time shift', {}),
    ('slice dependent phase shift', {}),
    ('compensate for asynchronous slice timing', {}),
    ('adjusted data for timing differences between slices', {}),
    ('corrected data for asynchronous slice timing', {}),
    ('corrected functional images for asynchronous slice timing', {}),
    ('TR alignment', {}),
    ('slicetimer', {}),
    ('3dtshift', {}),
    # Should be matched by stc_context
    ('removed slice differences using spline interpolation', {}),
    ('slices were temporally aligned', {}),
    # Negatives
    ('tr alignment', None),
    ('spline interpolation', None),
    ('stimuli were temporally aligned', None),
    ('reslice using sinc interpolation', None),
    ('sliced using spline interpolation', None),
])
def test_stc(input, expected):
    check_taggers([taggers.stc, taggers.stc_context], input, expected)


@pytest.mark.parametrize('input, expected', [
    # Positives
    ('corrected for head movement', {}),
    ('corrected for subject movement', {}),
    ('corrected for subjects movement', {}),
    ('corrected for bulk movement', {}),
    ('corrected for whole head movement', {}),
    ('correction for slice timing and head motion', {}),
])
def test_realign(input, expected):
    check_taggers([taggers.realign], input, expected)


@pytest.mark.parametrize('input, expected', [
    # Positives
    ('spatial smoothing', {}),
    ('spatially smoothed', {}),
    ('smoothed at 8 mm3', {}),
    # Negatives
    ('smoothing', None),
])
def test_spatsmoo(input, expected):
    check_taggers([taggers.spatsmoo], input, expected)


@pytest.mark.parametrize('input, expected', [
    # Positives
    ('head motion regression', {}),
    ('head motion regressor', {}),
    ('head movement regressed', {}),
    ('head movement covariate', {}),
    # Should be matched by motreg_context
    ('account for residual effects of movement', {}),
    ('account for head motion', {}),
    # Should be matched by motreg_context_strict
    ('movement included in the design', {}),
    ('motion parameters included in model', {}),
    # Negatives
    ('account for eye movement', None),
    ('model limb motion', None),
])
def test_motreg(input, expected):
    check_taggers(
        [taggers.motreg, taggers.motreg_context, taggers.motreg_context_strict],
        input,
        expected,
    )


@pytest.mark.parametrize('input, expected', [
    # Positives
    ('high pass filter 1 / 128 hz', {'value': 128}),
    ('high pass filter cutoff of 1 / 128 hz', {'value': 128}),
    ('high pass filter 128 s', {'value': 128}),
    ('high pass filter 64 seconds', {'value': 64}),
    # Negatives
    ('low pass filter', None),
    ('high pass low pass filter 128 s', None),
    ('high pass filter 1 hz eeg', None),
    ('high pass filter stimuli 10 s', None),
    ('high pass filter 1 s 1', None),
    ('high pass filter 0 001 hz', None),
    ('high pass filter 0 hz', None),
    ('high pass filter 0 / 128 hz', None),
    ('high pass filter 128 / 0 hz', None),
    ('high pass filter 001 hz', None),
    ('high pass filter 128 spelunkers', None),
])
def test_highpass_cutoff(input, expected):
    check_taggers([highpass_cutoff], input, expected)


@pytest.mark.parametrize('input, expected', [
    # Positives
    ('smoothing kernel of 8 mm fwhm', {'value': 8.0}),
    ('smoothing kernel of 8 millimeters fwhm', {'value': 8.0}),
    ('smooth kernel of 8 millimeters full width', {'value': 8.0}),
    # Negatives
    ('smoothing kernel of 8 fwhm', None),
    ('smoothing kernel of 8 mm', None),
    ('smoothing kernel of 50 mm fwhm', None),
    ('smoothing kernel of 6 .5 mm fwhm', None),
])
def test_smooth_kernel(input, expected):
    check_taggers([smooth_kernel], input, expected)

