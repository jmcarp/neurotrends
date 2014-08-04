"""
Identify problematic methods choices or combinations.
"""

from neurotrends import pattern
from neurotrends.config import mongo
from neurotrends.model.utils import verified_mongo
from neurotrends.analysis.order import compute_positions


def ffx(verbose=False):
    query = {
        'tags.label': 'ffx',
    }
    query.update(verified_mongo)
    cursor = mongo['article'].find(query)
    count = cursor.count()

    if verbose:
        print('Fixed-effects analysis')
        print('{0} articles'.format(count))

    return count


def low_highpass_cutoff(value=32, verbose=False):

    query = {
        'tags': {
            '$elemMatch': {
                'label': 'highpass_cutoff',
                'value': {
                    '$lt': value,
                }
            }
        }
    }

    query.update(verified_mongo)
    cursor = mongo['article'].find(query)
    count = cursor.count()

    if verbose:
        print('Low high-pass filter cutoff')
        print('{0} articles'.format(count))

    return count


def no_mcc(verbose=True):

    query = {
        'tags.label': {
            '$nin': pattern.tag_groups['mcc'].labels
        }
    }
    query.update(verified_mongo)
    cursor = mongo['article'].find(query)
    count = cursor.count()

    if verbose:
        print('No correction for multiple comparisons')
        print('{0} articles'.format(count))

    return count


def alphasim_not_estsmoo(verbose=False):

    query = {
        'tags.label': {
            '$in': [
                'alphasim',
            ],
            '$nin': [
                'estsmoo',
            ],
        }
    }
    query.update(verified_mongo)
    cursor = mongo['article'].find(query)
    bad = cursor.count()

    query_total = {
        'tags.label': 'alphasim',
    }
    query_total.update(verified_mongo)
    cursor_total = mongo['article'].find(query_total)
    total = cursor_total.count()

    if verbose:
        print('Alphasim without smoothness estimation')
        print('{0} articles of {1} using both steps ({2:.04f})'.format(
            bad, total, 100 * bad / total
        ))
    return bad, total


def fsl_stc(verbose=False):

    query = {
        'tags.label': 'stc',
        'tags': {
            '$elemMatch': {
                '$or': [
                    {
                        'label': 'fsl',
                        'version': '?',
                    },
                    {
                        'label': 'fsl',
                        'version': {
                            '$lt': '4.1.9',
                        }
                    },
                ],
            },
        },
    }
    query.update(verified_mongo)
    cursor = mongo['article'].find(query)
    count = cursor.count()

    if verbose:
        print('Slice-timing correction with FSL pre-4.1.9 or unknown')
        print('{0} articles'.format(count))

    return count


_filter_motreg_selectors = {
    'filter': {'label': 'filter'},
    'motreg': {'label': 'motreg'},
}
def _filter_first(tags):
    positions, _ = compute_positions(tags, _filter_motreg_selectors)
    return positions['filter'] < positions['motreg']

def filter_before_motreg(verbose=False):

    query = {
        'tags.label': {
            '$all': ['filter', 'motreg'],
        }
    }
    query.update(verified_mongo)
    cursor = mongo['article'].find(query, {'tags': 1})

    bad = len([
        article
        for article in cursor
        if _filter_first(article['tags'])
    ])

    total = cursor.count()

    if verbose:
        print('Filtering before motion regression')
        print('{0} articles of {1} using both steps ({2:.04f})'.format(
            bad, total, 100 * bad / total
        ))

    return bad, total


ffx(verbose=True)
low_highpass_cutoff(verbose=True)
no_mcc(verbose=True)
alphasim_not_estsmoo(verbose=True)
fsl_stc(verbose=True)
filter_before_motreg(verbose=True)
