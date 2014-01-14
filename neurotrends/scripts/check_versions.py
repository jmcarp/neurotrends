"""

"""

from __future__ import division

import datetime

from neurotrends.config import mongo
from neurotrends.model.utils import verified_mongo

def add_dicts(*dicts):
    rv = {}
    for d in dicts:
        rv.update(d)
    return rv

def version_proportion(label):

    total = mongo['article'].find(
        add_dicts(
            verified_mongo,
            {
                'tags': {
                    '$elemMatch': {
                        'label': label,
                    }
                }
            }
        )
    ).count()

    version = mongo['article'].find(
        add_dicts(
            verified_mongo,
            {
                'tags': {
                    '$elemMatch': {
                        'label': label,
                        'version': {
                            '$ne': '?',
                        },
                    }
                }
            }
        )
    ).count()

    return version / total


def get_current_version(releases, date):

    released = [
        release
        for release in releases
        if releases[release] <= date
    ]

    if released:
        return sorted(
            released,
            key=lambda r: releases[r],
            reverse=True
        )[0]


def check_version_delay(label, releases, version_proc=None):

    currents = []
    delays_date = []
    delays_idx = []

    sorted_releases = sorted(
        releases.keys(),
        key=lambda r: releases[r]
    )

    articles = mongo['article'].find({
        'tags': {
            '$elemMatch': {
                'label': label,
                'version': {
                    '$ne': '?',
                }
            }
        }
    })

    for article in articles:

        version = [
            tag['version']
            for tag in article['tags']
            if tag['label'] == label
        ][0]

        if article['date']:
            current = get_current_version(releases, article['date'])
            if version_proc:
                current = version_proc(current)
            currents.append(version == current)
            if version == current:
                delays_date.append(datetime.timedelta(0))
                delays_idx.append(0)
            else:
                date_current = releases.get(current)
                date_version = releases.get(version)
                if date_current and date_version:
                    delays_date.append(date_current - date_version)
                    delays_idx.append(
                        sorted_releases.index(current) -
                        sorted_releases.index(version)
                    )

    return currents, delays_date, delays_idx


spm_releases = {
    '96': datetime.datetime(1997, 4, 9), # http://www.fil.ion.ucl.ac.uk/spm/software/spm96/
    '97': datetime.datetime(1998, 7, 31), # http://www.fil.ion.ucl.ac.uk/spm/software/spm96/#ER96
    '99': datetime.datetime(2000, 1, 25), # http://www.fil.ion.ucl.ac.uk/spm/software/spm99/
    '2': datetime.datetime(2003, 1, 1), # Day and month unknown
    '5': datetime.datetime(2005, 12, 1),
    '8': datetime.datetime(2009, 4, 1), # Day unknown
}

spm_version_proc = lambda v: v.strip('b') if isinstance(v, basestring) else v

currents, delays_date, delays_idx = check_version_delay(
    'spm', spm_releases, spm_version_proc
)
