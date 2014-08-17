# -*- coding: utf-8 -*-

import os

from sciscrape.scrapetools.scrape import Scrape, UMScrape
from sciscrape.scrapetools.scrape import EXTENSIONS


SCRAPE_CLASS = UMScrape

USER_FILE = '/Users/jmcarp/private/ump'
SCRAPE_KWARGS = {
    'timeout': 30,
    'user_file': USER_FILE,
    'agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) '
             'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 '
             'Safari/537.36',
}
DOCUMENT_TYPES = ['pmc', 'html', 'pdf']
VERIFY_THRESHOLD = 0.9
DOCUMENT_TYPES_TO_FIELDS = {
    'html': 'publisher_html',
    'pdf': 'publisher_pdf',
    'pmc': 'pubmed_html',
}
BASE_SAVE_DIR = '/Users/jmcarp/Desktop/neurotrends-test'
SAVE_DIRS = {
    'html': os.path.join(BASE_SAVE_DIR, 'html'),
    'pdf': os.path.join(BASE_SAVE_DIR, 'pdf'),
    'pmc': os.path.join(BASE_SAVE_DIR, 'pmc'),
}
EXTRACT_SAVE_DIRS = {
    'html': os.path.join(BASE_SAVE_DIR, 'html_extract'),
    'pdf': os.path.join(BASE_SAVE_DIR, 'pdf_extract'),
    'pmc': os.path.join(BASE_SAVE_DIR, 'pmc_extract'),
}

OPENURL_URL = 'http://www.crossref.org/openurl/'
EMAIL_ADDR = 'jm.carp@gmail.com'

PDF_MIN_LENGTH = 1000

