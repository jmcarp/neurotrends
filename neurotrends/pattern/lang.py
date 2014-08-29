# -*- coding: utf-8 -*-

category = 'tool'

import os
import shelve

from neurotrends.config import re
from neurotrends.tagger import Looks, RexTagger, RexComboVersionTagger
from misc import delimiter, version_separator
from neurotrends import trendpath

python = RexTagger(
    'python', [r'python']
)

java = RexTagger(
    'java',
    [
        r'java(?!{dlm}script)'.format(dlm=delimiter),
    ]
)

rlang = RexTagger(
    'rlang',
    [
        r'\Wr{dlm}project'.format(dlm=delimiter),
        r'\Wr{dlm}development{dlm}(core)?{dlm}team'.format(dlm=delimiter),
        r'''
            \Wr{dlm}foundation{dlm}for{dlm}statistical{dlm}computing
        '''.format(dlm=delimiter),
        r'''
            (software|programming){dlm}(language|environment){dlm}r(?!\w)
        '''.format(dlm=delimiter),
        r'''
            \Wr{dlm}(software|programming){dlm}(language|senvironment)
        '''.format(dlm=delimiter),
        r'\Wr{dlm}statistical'.format(dlm=delimiter),
        r'\Wr{dlm}software'.format(dlm=delimiter),
        r'\Wr{dlm}library'.format(dlm=delimiter),
    ]
)

idl = RexTagger(
    'idl',
    [
        r'\Widl\W',
        r'interactive{dlm}data{dlm}language'.format(dlm=delimiter),
    ]
)

fortran = RexTagger(
    'fortran', [r'fortran']
)

octave = RexTagger(
    'octave', [r'octave']
)

import requests
from bs4 import BeautifulSoup

def get_matlab_versions(overwrite=False):
    """Get MATLAB versions from Wikipedia.

    :param overwrite: Overwrite existing data?
    :return: MATLAB versions

    """
    # Get version file
    version_file = os.path.join(trendpath.data_dir, 'matlab-versions.shelf')

    # Used saved versions if version file exists and not overwrite
    if os.path.exists(version_file) and not overwrite:
        shelf = shelve.open(version_file)
        versions = shelf['versions']
        shelf.close()
        return versions

    # Open Wikipedia page
    response = requests.get('http://en.wikipedia.org/wiki/MATLAB')
    soup = BeautifulSoup(response.content)

    # Find "Release History" table
    history_headline = soup.find(id='Release_history')
    history_table = history_headline.find_next(
        'table',
        class_=re.compile(r'wikitable'),
    )
    history_row = history_table.find_all('tr')

    # Initialize Matlab versions
    versions = {}

    for row in history_row[1:]:

        # Get <td> elements
        tds = row.findAll('td')

        # Get version number
        version_number = tds[0].text
        version_number = re.sub(r'matlab\s+', '', version_number, flags=re.I)

        # Get version name
        version_name = tds[1].text

        # Make "r" in e.g. "r2007a" optional
        version_name = re.sub('r', 'r?', version_name, flags=re.I)

        # "Service Pack" -> "sp"
        version_name = re.sub(
            r'{dlm}(sp|service pack){dlm}'.format(dlm=delimiter),
            'sp',
            version_name,
            flags=re.I
        )

        # Add to versions
        versions[version_number] = [version_number]
        if version_name:
            versions[version_number].append(version_name)

    # Save results to version file
    shelf = shelve.open(version_file)
    shelf['versions'] = versions
    shelf.close()

    # Return versions
    return versions


# Hack: Catch IOError in Shelve; breaks on serving API with uWSGI
try:
    matlab_versions = get_matlab_versions()
    matlab = RexComboVersionTagger(
        'matlab',
        [
            r'matlab',
        ],
        version_separator,
        # Only match against complete versions; e.g., don't confuse "matlab r14"
        # with "matlab r1"
        looks=Looks(negahead=r'(\d|\.[1-9]|st|nd|rd|th)'),
        versions=matlab_versions,
    )
except IOError:
    pass

