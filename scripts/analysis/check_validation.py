#!/usr/bin/env python
# encoding: utf-8

import numpy as np
import pandas as pd

from neurotrends import validate as val
from neurotrends.analysis.plot.utils import file_name


def to_hist(result, groups=None):
    groups = groups or result.keys()
    dprimes = []
    for group in groups:
        dprimes.append([
            tag['dprime']
            for tag in result[group].itervalues()
            if tag['dprime'] is not None
        ])
    return dprimes, groups


def to_frame(result):
    data = []
    for _, tags in result.iteritems():
        data.extend([
            {'tag': tag, 'dprime': info['dprime']}
            for tag, info in tags.iteritems()
        ])
    return pd.DataFrame(data).sort('dprime')


print('{0} articles included in both sets'.format(
    len(val.pmids)
))
print('{0} articles included in both sets, excluding supplements'.format(
    len(val.pmids_no_supplement)
))


# Validate categorical values

validation = val.validate()
dprimes, groups = to_hist(validation)
frame = to_frame(validation)
val.validate_hist(
    dprimes, bins=5, labels=groups, title='Supplements included', xlabel='D-Prime',
    outname=file_name(['dprime-supplements'], path='validate')
)
frame.to_csv(file_name(['dprime-supplements'], path='validate'), ext='.csv')
print('Categorical Validation: Supplements Included')
print(np.mean(sum(dprimes, [])))


validation = val.validate(no_supplement=True)
dprimes, groups = to_hist(validation)
frame = to_frame(validation)
val.validate_hist(
    dprimes, bins=5, labels=groups, title='Supplements excluded', xlabel='D-Prime',
    outname=file_name(['dprime-no-supplements'], path='validate')
)
frame.to_csv(file_name(['dprime-no-supplements'], path='validate', ext='.csv'))
print('Categorical Validation: Supplements Excluded')
print(np.mean(sum(dprimes, [])))

# Validate continuous values

_, rp_smooth_kernel, nt_smooth_kernel, = val.validate_continuous(
    val.rp_extract_smooth_kernel,
    val.nt_extract_smooth_kernel,
)
print('Continuous Validation: Smoothing Kernel')
print(val.format_continuous_validation(
    rp_smooth_kernel,
    nt_smooth_kernel,
))


_, rp_highpass_cutoff, nt_highpass_cutoff, = val.validate_continuous(
    val.rp_extract_highpass_cutoff,
    val.nt_extract_highpass_cutoff,
)
print('Continuous Validation: High-pass Cutoff')
print val.format_continuous_validation(
    rp_highpass_cutoff,
    nt_highpass_cutoff,
)
