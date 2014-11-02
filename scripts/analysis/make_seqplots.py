"""

"""

from neurotrends import pattern
from neurotrends.config import mongo

from neurotrends.analysis.groupby.naive import summarize_ranks
from neurotrends.analysis import order
from neurotrends.analysis.plot import seqplot
from neurotrends.analysis.plot.utils import file_name

labels = [
    label
    for label in pattern.tag_groups['proc'].labels
    if label not in ['highpass_cutoff', 'smooth_kernel']
]

labels = list(set(labels))

summary, labels = summarize_ranks(
    mongo['article'], labels, min_prop=0.05,
)

ranks = order.analyze_rank_order(summary, mongo['article'])

ranks_spm = order.analyze_rank_order(summary, mongo['article'], {'tags.label': 'spm'})
ranks_fsl = order.analyze_rank_order(summary, mongo['article'], {'tags.label': 'fsl'})
ranks_afni = order.analyze_rank_order(summary, mongo['article'], {'tags.label': 'afni'})

seqplot.rank_plot(ranks, outname=file_name(['seq'], path='seq'))

seqplot.multi_rank_plot(
    ranks,
    [
        'spm',
        'fsl',
        'afni',
    ],
    [
        ranks_spm,
        ranks_fsl,
        ranks_afni,
    ],
    outname=file_name(['seq', 'pkg'], path='seq')
)

#years = range(2000, 2014)
#ranks_year = []
#
#for year in years:
#
#    query = {
#        'date': {
#            '$gte': datetime.datetime(year, 1, 1),
#            '$lt': datetime.datetime(year + 1, 1, 1),
#        }
#    }
#
#    ranks_year.append(order.analyze_rank_order(
#        summary, mongo['article'], query
#    ))
#
#seqplot.multi_rank_plot(
#    ranks,
#    years,
#    ranks_year,
#    outname=file_name(['seq', 'year'], path='seq')
#)
