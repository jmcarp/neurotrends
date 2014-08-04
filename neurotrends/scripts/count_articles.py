"""
Get basic statistics about the number of documents downloaded and verified
by document type.
"""

from __future__ import division

from collections import defaultdict

from neurotrends.config import mongo

from neurotrends.model import Article
from neurotrends.model.utils import verified_mongo
from neurotrends.model.config import DOCUMENT_TYPES_TO_FIELDS


def count_verified():
    """Count the number of downloaded and verified documents across all
    articles.

    :return: Tuple of total and verified dictionaries, each mapping document
    types to counts

    """
    count = defaultdict(int)
    verified = defaultdict(int)

    for article in Article.find():
        for type, field in DOCUMENT_TYPES_TO_FIELDS.iteritems():
            value = getattr(article, field)
            if value:
                count[type] += 1
                if value.verification_score > 0.9:
                    verified[type] += 1

    return count, verified

if __name__ == '__main__':

    total = mongo['article'].count()
    publisher_pdf = mongo['article'].find({'verified': 'pdf'}).count()
    publisher_html = mongo['article'].find({'verified': 'html'}).count()
    pmc_html = mongo['article'].find({'verified': 'pmc'}).count()
    any_document = mongo['article'].find(verified_mongo).count()

    print(
        'Total articles: {total}\n'
        'With publisher PDF: {pdf} ({pdf_ratio:.04f})\n'
        'With publisher HTML: {html} ({html_ratio:.04f})\n'
        'With PubMed HTML: {pmc} ({pmc_ratio:.04f})\n'
        'With any document: {any} ({any_ratio})'.format(
            total=total,
            pdf=publisher_pdf,
            pdf_ratio=publisher_pdf/total,
            html=publisher_html,
            html_ratio=publisher_html/total,
            pmc=pmc_html,
            pmc_ratio=pmc_html/total,
            any=any_document,
            any_ratio=any_document/total,
        )
    )

    print('')

    count, verified = count_verified()
    print(
        'Verified articles:\n'
        'Publisher PDF: {pdf_verified} of {pdf_total} ({pdf_ratio:0.4f})\n'
        'Publisher HTML: {html_verified} of {html_total} ({html_ratio:0.4f})\n'
        'PubMed HTML: {pmc_verified} of {pmc_total} ({pmc_ratio:0.4f})\n'.format(
            pdf_verified=verified['pdf'],
            pdf_total=count['pdf'],
            pdf_ratio=verified['pdf']/count['pdf'],
            html_verified=verified['html'],
            html_total=count['html'],
            html_ratio=verified['html']/count['html'],
            pmc_verified=verified['pmc'],
            pmc_total=count['pmc'],
            pmc_ratio=verified['pmc']/count['pmc'],
        )
    )
