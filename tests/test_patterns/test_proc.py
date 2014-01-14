"""

"""

from neurotrends.pattern.proc import proc
from neurotrends.pattern.proc.est_highpass_cutoff import highpass_cutoff
from neurotrends.pattern.proc.est_smooth_kernel import smooth_kernel

from . import build_tests

build_tests(
    [proc.stc, proc.stc_context],
    [
        # Should be matched by stc
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
    ],
    [
        'tr alignment',
        'spline interpolation,'
        'stimuli were temporally aligned',
        'reslice using sinc interpolation',
        'sliced using spline interpolation',
    ]
)

build_tests(
    proc.realign,
    [
        ('corrected for head movement', {}),
        ('corrected for subject movement', {}),
        ('corrected for subjects movement', {}),
        ('corrected for bulk movement', {}),
        ('corrected for whole head movement', {}),
        ('correction for slice timing and head motion', {}),
    ],
)

build_tests(
    proc.spatsmoo,
    [
        ('spatial smoothing', {}),
        ('spatially smoothed', {}),
        ('smoothed at 8 mm3', {}),
    ],
    [
        'smoothing',
    ]
)

build_tests(
    [proc.motreg, proc.motreg_context, proc.motreg_context_strict],
    [
        # Should be matched by motreg
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
    ],
    [
        'account for eye movement',
        'model limb motion',
    ]
)

build_tests(
    highpass_cutoff,
    [
        (
            'high pass filter 1 / 128 hz',
            {'value': 128}
        ),
        (
            'high pass filter cutoff of 1 / 128 hz',
            {'value': 128}
        ),
        (
            'high pass filter 128 s',
            {'value': 128}
        ),
        (
            'high pass filter 64 seconds',
            {'value': 64}
        ),
    ],
    [
        'low pass filter',
        'high pass low pass filter 128 s',
        'high pass filter 1 hz eeg',
        'high pass filter stimuli 10 s',
        'high pass filter 1 s 1',
        'high pass filter 0 001 hz',
        'high pass filter 0 hz',
        'high pass filter 0 / 128 hz',
        'high pass filter 128 / 0 hz',
        'high pass filter 001 hz',
        'high pass filter 128 spelunkers'
    ]
)

build_tests(
    smooth_kernel,
    [
        ('smoothing kernel of 8 mm fwhm', {'value': 8.0}),
        ('smoothing kernel of 8 millimeters fwhm', {'value': 8.0}),
        ('smooth kernel of 8 millimeters full width', {'value': 8.0}),
    ],
    [
        'smoothing kernel of 8 fwhm',
        'smoothing kernel of 8 mm',
        'smoothing kernel of 50 mm fwhm',
        'smoothing kernel of 6 .5 mm fwhm',
    ]
)
