"""

"""

from __future__ import division

import re

import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm, pearsonr

from neurotrends.config import mongo
from neurotrends.model.utils import verified_mongo

# Import fmri-report
import sys
sys.path.append('/Users/jmcarp/Dropbox/projects/fmri-report/scripts')
import reportproc as rp

report = rp.ezread()

rp_pmids = [
    article['pmid']
    for article in report
]

rp_pmids_no_supplement = [
    article['pmid']
    for article in report
    if article['supplement'] == 'no'
]

nt_pmids = [
    article['pmid']
    for article in mongo['article'].find(
        verified_mongo, {'pmid': 1}
    )
]

pmids = set(rp_pmids).intersection(nt_pmids)
pmids_no_supplement = set(rp_pmids_no_supplement).intersection(nt_pmids)

class Validator(object):

    def __init__(self, tag, rp_column, rp_value='TRUE'):
        self.tag = tag
        self.rp_column = rp_column
        self.rp_value = rp_value

    def _get_nt_pmids(self, pmids):
        articles = mongo['article'].find(
            {
                'pmid': {
                    '$in': list(pmids),
                },
                'tags': {
                    '$elemMatch': self.tag
                }
            },
            {'pmid': 1}
        )
        return [
            article['pmid']
            for article in articles
        ]

    def _get_rp_pmids(self, pmids):
        return [
            article['pmid']
            for article in report
            if article['pmid'] in pmids
                and re.search(self.rp_value, article[self.rp_column])
        ]

    @staticmethod
    def _nonzero(value, precision=0.001):
        return max(
            precision,
            min(
                1 - precision,
                value
            )
        )

    def validate(self, no_supplement=False):

        _pmids = pmids_no_supplement if no_supplement else pmids

        nt_pmids = set(self._get_nt_pmids(_pmids))
        rp_pmids = set(self._get_rp_pmids(_pmids))

        true_pos = nt_pmids.intersection(rp_pmids)
        false_pos = nt_pmids.difference(rp_pmids)

        nt_neg = _pmids.difference(nt_pmids)
        rp_neg = _pmids.difference(rp_pmids)

        true_neg = nt_neg.intersection(rp_neg)
        false_neg = rp_pmids.difference(nt_pmids)

        if not true_pos and not false_pos:

            dprime = None

        else:

            phit, pfal = [self._nonzero(0)] * 2

            if true_pos:
                phit = self._nonzero(
                    len(true_pos) / (len(true_pos) + len(false_neg))
                )

            if len(false_pos):
                pfal = self._nonzero(
                    len(false_pos) / (len(true_neg) + len(false_pos))
                )

            dprime = norm.ppf(phit) - norm.ppf(pfal)

        return {
            'true_pos': true_pos,
            'false_pos': false_pos,
            'true_neg': true_neg,
            'false_neg': false_neg,
            'dprime': dprime,
        }


validators = {

    # Software packages
    'spm':     Validator({'label': 'spm'}, 'misc-softpck', 'spm'),
    'fsl':     Validator({'label': 'fsl'}, 'misc-softpck', 'fsl'),
    'afni':    Validator({'label': 'afni'}, 'misc-softpck', 'afni'),
    'voyager': Validator({'label': 'voyager'}, 'misc-softpck', 'voyager'),
    'surfer':  Validator({'label': 'surfer'}, 'misc-softpck', 'freesurfer'),

    # Software versions
    'spm96': Validator({'label': 'spm', 'version': '96'}, 'misc-softcom', 'spm 96'),
    'spm99': Validator({'label': 'spm', 'version': '99'}, 'misc-softcom', 'spm 99'),
    'spm2':  Validator({'label': 'spm', 'version': '2'}, 'misc-softcom', 'spm 2'),
    'spm5':  Validator({'label': 'spm', 'version': '5'}, 'misc-softcom', 'spm 5'),
    'spm8':  Validator({'label': 'spm', 'version': '8'}, 'misc-softcom', 'spm 8'),

    # Design
    'event': Validator({'label': 'event'}, 'des-edes-destype', 'event'),
    'block': Validator({'label': 'block'}, 'des-edes-destype', 'block'),
    'mixed': Validator({'label': 'mixed'}, 'des-edes-destype', 'mixed'),

    # Basis functions
    'hrf':    Validator({'label': 'hrf'}, 'mod-smod-basis', 'hrf'),
    'tmpdrv': Validator({'label': 'tmpdrv'}, 'mod-smod-basis', 'td'),
    'dspdrv': Validator({'label': 'dspdrv'}, 'mod-smod-basis', 'disp'),
    'fir':    Validator({'label': 'fir'}, 'mod-smod-basis', 'fir'),

    # Processing
    'evtopt':   Validator({'label': 'desopt'}, 'des-edes-eventopt-bool'),
    'stc':      Validator({'label': 'stc'}, 'proc-slicetime-bool'),
    'realign':  Validator({'label': 'realign'}, 'proc-mc-bool'),
    'coreg':    Validator({'label': 'coreg'}, 'proc-coreg-bool'),
    'strip':    Validator({'label': 'strip'}, 'proc-skullstrip-bool'),
    'norm':     Validator({'label': 'norm'}, 'proc-norm-bool'),
    'spatsmoo': Validator({'label': 'spatsmoo'}, 'proc-smooth-bool'),
    'filter':   Validator({'label': 'filter'}, 'mod-smod-filter-bool'),
    'acf':      Validator({'label': 'autocorr'}, 'mod-smod-acf-bool'),
    'roi':      Validator({'label': 'roi'}, 'mod-roi-bool'),
    'motreg':   Validator({'label': 'motreg'}, 'mod-smod-regress', 'movement params'),

    # Multiple comparison correction
    'fdr':      Validator({'label': 'fdr'}, 'mod-gmod-mccorrect-mccmethod', 'fdr'),
    'fwe':      Validator({'label': 'fwe'}, 'mod-gmod-mccorrect-mccmethod', 'fwe'),
    'bon':      Validator({'label': 'bon'}, 'mod-gmod-mccorrect-mccmethod', 'bon'),
    'alphasim': Validator({'label': 'alphasim'}, 'mod-gmod-mccorrect-mccmethod', 'alphasim'),

    # Task presentation software
    'eprime':       Validator({'label': 'eprime'}, 'des-edes-taskprog', 'eprime'),
    'presentation': Validator({'label': 'presentation'}, 'des-edes-taskprog', 'presentation'),
    'cogent':       Validator({'label': 'cogent'}, 'des-edes-taskprog', 'cogent'),
    'psyscope':     Validator({'label': 'psyscope'}, 'des-edes-taskprog', 'psyscope'),
    'psychtoolbox': Validator({'label': 'psychtoolbox'}, 'des-edes-taskprog', 'psychtoolbox'),

}

def validate(no_supplement=False):

    results = {
        name: validator.validate(no_supplement=no_supplement)
        for name, validator in validators.iteritems()
    }
    return results

def rp_select(pmid):
    for row in report:
        if row['pmid'] == pmid:
            return row

def nt_select(pmid):
    return mongo['article'].find_one({'pmid': pmid})

# Extractors

def rp_extract_smooth_kernel(item):
    raw = item.get('proc-smooth-kernel', '')
    if 'mm fwhm' in raw:
        value = raw.split('mm fwhm')[0]
        try:
            return float(value)
        except ValueError:
            pass

def nt_extract_smooth_kernel(item):
    for tag in item['tags']:
        if tag['label'] == 'smooth_kernel':
            return tag['value']

def rp_extract_highpass_cutoff(item):
    if item['mod-smod-filter-filttype'] != 'high-pass':
        return
    raw = item.get('mod-smod-filter-filtband', '').lower()
    if 'hz' in raw:
        value = raw.split('hz')[0]
        try:
            return 1 / float(value)
        except ValueError:
            return
    elif re.search(r'^\d.*?s$', raw):
        value = raw.strip('s')
        try:
            return float(value)
        except ValueError:
            return

def nt_extract_highpass_cutoff(item):
    for tag in item['tags']:
        if tag['label'] == 'highpass_cutoff':
            return tag['value']

def validate_continuous(rp_extract, nt_extract):

    valid_pmids = []
    rp_values, nt_values = [], []

    for pmid in pmids:

        rp_data = rp_select(pmid)
        if not rp_data:
            continue
        rp_value = rp_extract(rp_data)

        nt_data = nt_select(pmid)
        if not nt_data:
            continue
        nt_value = nt_extract(nt_data)

        if rp_value and nt_value:
            valid_pmids.append(pmid)
            rp_values.append(rp_value)
            nt_values.append(nt_value)

    return valid_pmids, rp_values, nt_values

def format_continuous_validation(rp_values, nt_values):
    rval, pval = pearsonr(rp_values, nt_values)
    return 'r({df}) = {rval:.04f}; p = {pval:.04f}'.format(
        df=len(rp_values)-2,
        rval=rval,
        pval=pval,
    )

def validate_hist(values, xlabel=None, outname=None):

    ax = plt.hist(values)

    if xlabel:
        ax.set_xlabel(xlabel)

    if outname:
        plt.savefig(outname)
