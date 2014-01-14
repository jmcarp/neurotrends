"""

"""

import datetime
import collections

from neurotrends.config import mongo
from neurotrends.model.utils import verified_mongo
from neurotrends.analysis.groupby.naive import Key

def count_tags(summary, labels, total, date=None, display_labels=None, include_none=False, none_mode='missing'):
    """

    """
    display_labels = display_labels or labels

    label_counts = collections.defaultdict(int)
    any_ids = set()
    none_ids = set()
    for label in labels:
        date_label = ensure_key(label)._replace(date=date)
        ids = summary.get(date_label, [])
        value = float(len(ids))
        key = label if label in display_labels else 'other'
        label_counts[key] += value
        any_ids.update(ids)
        if include_none and none_mode == 'version':
            none_label = label._replace(date=date, version='?')
            none_ids.update(summary.get(none_label), [])

    if include_none:
        if none_mode == 'missing':
            label_counts['none'] = total - len(any_ids)
        elif none_mode == 'version':
            label_counts['none'] = len(none_ids)

    return label_counts, float(len(any_ids))


def get_display_labels(counts, labels, min_count, include_none):
    """Get labels to be displayed in plot.

    :param dict counts:
    :param list labels:
    :param int min_count:
    :param bool include_none:

    """
    display_labels = []
    if min_count:
        include_other = False
        for label in labels:
            if counts[label] > min_count:
                display_labels.append(label)
            elif not include_other:
                include_other = True
        if include_other:
            display_labels.append('other')
    else:
        # Note: Copy labels to avoid changing a mutable reference
        display_labels = list(labels)
    if include_none:
        display_labels.append('none')

    return display_labels


def get_versions(summary, label):
    """Get list of observed versions for label.

    :param dict summary: Group-by summary
    :param str label: Label to get versions for
    :return set: Unique versions

    """
    return set([
        key.version
        for key in summary
        if key.label == label
            and key.version
            and key.version != '?'
    ])


def get_values(summary):
    """Get list of observed versions for label.

    :param dict summary: Custom group-by summary
    :return set: Unique values

    """
    return set([
        key
        for key in summary.keys()
        if key.date is None
            and key.version is None
    ])


def ensure_key(label):
    """Build summary key from label dictionary.

    """

    if isinstance(label, Key):
        return label
    if isinstance(label, dict):
        return Key(**label)
    if isinstance(label, basestring):
        return Key(label)

    raise ValueError('Label must be `Key`, `dict`, or `basestring`.')

def tag_group(summary, labels, sorted_labels=None, sort_key=None, sort_reverse=None, query=None, min_prop=None, include_none=False, none_mode='missing'):
    """

    """
    labels = [
        ensure_key(label)
        for label in labels
    ]

    counts = {
        label: float(len(set(summary.get(label, []))))
        for label in labels
    }

    if sorted_labels is None:
        if sort_key:
            sorted_labels = sorted(
                labels,
                key=sort_key,
                reverse=sort_reverse if sort_reverse is not None else False,
            )
        else:
            sorted_labels = sorted(
                labels,
                key=lambda x: counts[x],
                reverse=True
            )

    _query = query or {}
    _query.update(verified_mongo)
    total = mongo['article'].find(_query).count()
    min_count = total * min_prop if min_prop else 0

    display_labels = get_display_labels(counts, sorted_labels, min_count, include_none)

    count_date, _ = count_tags(
        summary, sorted_labels, total,
        display_labels=display_labels, include_none=include_none,
        none_mode=none_mode,
    )

    return count_date, display_labels


def tag_year(summary, label, dates):
    """

    """
    return {
        date: float(len(set(summary.get((label, date), []))))
        for date in dates
    }


def tag_group_year(summary, labels, dates, sorted_labels=None, query=None, sort_key=None, min_prop=None, include_none=False, none_mode='missing'):
    """

    :param summary:
    :param labels: List of labels
    :param dates: List of dates
    :param min_prop: Minimum proportion of labels overall

    """
    labels = [
        ensure_key(label)
        for label in labels
    ]

    # Count articles by year
    date_counts = {}
    for date in dates:
        start_date = datetime.datetime(year=int(date), month=1, day=1)
        stop_date = datetime.datetime(year=int(date)+1, month=1, day=1)
        _query = {
            'date': {
                '$gte': start_date,
                '$lt': stop_date,
            }
        }
        _query.update(verified_mongo)
        _query.update(query or {})
        date_counts[date] = mongo['article'].find(_query).count()

    # Compute overall counts and proportions per label
    counts, display_labels = tag_group(
        summary, labels, sorted_labels=sorted_labels, sort_key=sort_key, min_prop=min_prop,
        include_none=include_none, none_mode=none_mode, query=query,
    )

    # Summarize data for plotting
    data = {}
    any_data = {}

    for date in dates:

        count_date, any_count_date = count_tags(
            summary, labels, date_counts[date], date,
            display_labels=display_labels, include_none=include_none,
            none_mode=none_mode,
        )
        data[date] = count_date
        any_data[date] = any_count_date

    return data, any_data, dates, date_counts, display_labels


def norm_counts(counts, date_counts=None):
    """Normalize count data by date.

    :param dict counts: Dict mapping dates to value-count dicts
    :param dict date_counts: Optional dict mapping counts to total counts; use
        sum across `counts` if not provided.
    :return dict: Normalized counts

    """
    values = {}

    for date, count in counts.items():
        total = date_counts[date] if date_counts else sum(count.values())
        if total:
            values[date] = {
                label: item / total
                for label, item in count.items()
            }
        else:
            values[date] = {
                label: 0
                for label in count
            }

    return values


def norm_any_counts(counts, date_counts):
    """Normalize any-count data by date.

    :param counts: Dict mapping dates to any-counts
    :param date_counts: Dict mapping dates to total counts
    :return: Normalized any-counts

    """
    return {
        date: counts[date] / date_counts[date]
        for date in counts
    }
