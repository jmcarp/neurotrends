"""

"""

from neurotrends.config import mongo
from neurotrends.model.utils import verified_mongo
from neurotrends.analysis.groupby.naive import summarize_custom
from neurotrends.analysis.groupby.naive import summarize_smooth_kernel, summarize_highpass_cutoff
from neurotrends.analysis.plot.histplot import hist
from neurotrends.analysis.plot.utils import file_name

import numpy as np

cursor = mongo['article'].find(
    verified_mongo,
    {'tags': 1, 'date': 1}
)

summary_smooth_kernel = summarize_custom(
    cursor, 'smooth_kernel', summarize_smooth_kernel
)
summary_highpass_cutoff = summarize_custom(
    cursor, 'highpass_cutoff', summarize_highpass_cutoff
)

hist(
    summary_smooth_kernel, bins=np.arange(0.5, 19.5, 1), xlabel='Smoothing Kernel',
    outname=file_name(['smooth-kernel'], path='hist')
)

hist(
    summary_highpass_cutoff, xlog=True, xlabel='High-pass Filter Cutoff',
    outname=file_name(['highpass-cutoff'], path='hist')
)
