# -*- coding: utf-8 -*-

import json

import requests
from bs4 import BeautifulSoup

from neurotrends.config import re, cache_collection
from neurotrends.pattern.misc import delimiter


version_subs = [
    # Handle whitespace
    (
        r'\s+',
        delimiter,
    ),
    # Make initial "r" (e.g. "r2011") optional
    (
        r'^r',
        'r?{dlm}'.format(dlm=delimiter),
    ),
    # Handle service pack information
    (
        r'sp(\d+)',
        r'{dlm}(sp|service{dlm}pack){dlm}\1'.format(dlm=delimiter),
    ),
]


def get_version_regex(value, flags=re.I):
    for sub in version_subs:
        value = re.sub(sub[0], sub[1], value, flags=flags)
    return value


def parse_version_row(row):
    """Get version number and labels from version table row.

    :return: Tuple of (number, [labels])
    """
    cols = row.find_all('td')
    if not cols:
        return

    version_number = cols[0].text
    version_name = cols[1].text

    version_values = [version_number]
    if version_name:
        version_values.append(version_name)

    version_number = re.sub(
        r'matlab', '', version_number, flags=re.I
    ).strip()

    return version_number, version_values


def fetch_versions():
    """Fetch version information from Wikipedia.

    :return: Dictionary mapping version numbers to lists of version labels
    """
    resp = requests.get('http://en.wikipedia.org/wiki/MATLAB')
    parsed = BeautifulSoup(resp.content)

    history_headline = parsed.find(id='Release_history')
    history_table = history_headline.find_next(
        'table',
        class_=re.compile(r'wikitable'),
    )
    history_rows = history_table.find_all('tr')

    return dict(
        filter(
            lambda item: item is not None,
            (parse_version_row(row) for row in history_rows),
        )
    )


def load_versions():
    """Load versions from database cache. Unserialize versions as JSON to avoid
    characters forbidden by MongoDB.
    """
    record = cache_collection.find_one({'_id': 'matlabVersions'})
    if record:
        return json.loads(record['value'])
    return None


def save_versions(versions):
    """Save versions to database cache. Serialize versions as JSON to avoid
    characters forbidden by MongoDB.
    """
    cache_collection.update(
        {'_id': 'matlabVersions'},
        {'$set': {'value': json.dumps(versions)}},
        upsert=True,
    )


def get_versions(overwrite=False):
    """Load or create MATLAB version information.

    :param bool overwrite: Overwrite existing values, if any
    """
    if not overwrite:
        versions = load_versions()
        if versions is not None:
            return versions
    versions = fetch_versions()
    save_versions(versions)
    return versions


def get_version_regexes(versions):
    """Format version information as regular expressions.
    """
    return {
        label: [get_version_regex(value) for value in values]
        for label, values in versions.iteritems()
    }


