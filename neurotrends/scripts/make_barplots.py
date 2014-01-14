"""

"""

import re

from neurotrends import pattern
from neurotrends.config import mongo
from neurotrends.model.utils import verified_mongo
from neurotrends.analysis.groupby.naive import Key, summarize, summarize_custom
from neurotrends.analysis.groupby.naive import summarize_field_strength
from neurotrends.analysis.tabulate import get_versions, get_values
from neurotrends.analysis.plot.barplot import groups_by_year, tags_by_year

DATES = range(2000, 2014)

cursor = mongo['article'].find(
    verified_mongo,
    {'tags': 1, 'date': 1}
)
summary = summarize(cursor)

#

def get_labels(labels):
    return [
        {'label': label}
        for label in set(labels)
    ]

def get_version_labels(summary, label):
    return [
        {
            'label': label,
            'version': version,
        }
        for version in get_versions(summary, label)
    ]

summary_field_strength = summarize_custom(
    cursor, 'field_strength', summarize_field_strength
)

fields = get_values(summary_field_strength)

def formatter(field):
    def _formatter(key):
        if isinstance(key, Key):
            return '{0}'.format(getattr(key, field))
        return key
    return _formatter

def sort_value(value):
    return value.value

groups_by_year(
    'field', summary_field_strength, fields, DATES,
    min_prop=0.01,
    label_formatter=formatter('value'), sort_key=sort_value,
)

groups_by_year(
    'pkg', summary, get_labels(pattern.tag_groups['pkg'].labels), DATES,
    label_formatter=formatter('label'),
    min_prop=0.025,
)

groups_by_year(
    'mcc', summary,
    get_labels([
        label
        for label in pattern.tag_groups['mcc'].labels
        if label != 'alphasim'
    ]),
    DATES,
    label_formatter=formatter('label'),
    min_prop=0.025,
)

groups_by_year(
    'opsys', summary, get_labels(pattern.tag_groups['opsys'].labels), DATES,
    label_formatter=formatter('label'),
    min_prop=0.01,
)

groups_by_year(
    'stat', summary, get_labels(pattern.tag_groups['stat'].labels), DATES,
    label_formatter=formatter('label'),
    min_prop=0.01,
)

#

def fmt_version(key):
    if isinstance(key, Key):
        return '{0} {1}'.format(key.label, key.version)
    return key

def to_year(value):
    tail = re.search(r'[a-z]+$', value, re.I)
    if tail:
        value = re.sub(r'[a-z]+$', '', value, flags=re.I)
    if len(value) == 4:
        return value
    value = value.zfill(2)
    pad = '19' if value[0] > '1' else '20'
    value = pad + value
    if tail:
        value += tail.group()
    return value

def sort_version_year(value):
    return to_year(value.version)

def to_number(value):
    split = value.split('.')
    return split[0] + '.' + ''.join(split[1:])

def sort_version_number(value):
    return to_number(value.version)

groups_by_year(
    'spm-ver', summary, get_version_labels(summary, 'spm'), DATES,
    min_prop=0.01,
    include_none=True, none_mode='version',
    label_formatter=fmt_version,
    sort_key=sort_version_year,
    query={'tags.label': 'spm'},
)

groups_by_year(
    'fsl-ver', summary, get_version_labels(summary, 'fsl'), DATES,
    min_prop=0.001,
    label_formatter=fmt_version,
    sort_key=sort_version_number,
    query={'tags.label': 'fsl'},
)

groups_by_year(
    'mat-ver', summary, get_version_labels(summary, 'matlab'), DATES,
    min_prop=0.01,
    label_formatter=fmt_version,
    sort_key=sort_version_number,
    query={'tags.label': 'matlab'},
)

groups_by_year(
    'voyager-ver', summary, get_version_labels(summary, 'voyager'), DATES,
    min_prop=0.01,
    label_formatter=fmt_version,
    sort_key=sort_version_number,
    query={'tags.label': 'voyager'},
)

for tag in ['stc', 'realign', 'norm']:
    tags_by_year(tag, summary, {'label': tag}, DATES)
