"""

"""

from neurotrends import validate as val

# Validate boolean values
validation = val.validate()
dprimes = {
    tag: stats['dprime']
    for tag, stats in validation.iteritems()
}
val.validate_hist(dprimes, 'D-Prime')

# Validate continuous values

_, rp_smooth_kernel, nt_smooth_kernel, = val.validate_continuous(
    val.rp_extract_smooth_kernel,
    val.nt_extract_smooth_kernel,
)
print 'Continuous Validation: Smoothing Kernel'
print val.format_continuous_validation(
    rp_smooth_kernel,
    nt_smooth_kernel,
)

_, rp_highpass_cutoff, nt_highpass_cutoff, = val.validate_continuous(
    val.rp_extract_highpass_cutoff,
    val.nt_extract_highpass_cutoff,
)
print 'Continuous Validation: High-pass Cutoff'
print val.format_continuous_validation(
    rp_highpass_cutoff,
    nt_highpass_cutoff,
)
