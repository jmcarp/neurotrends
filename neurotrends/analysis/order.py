"""

"""

import collections
import numpy as np

from neurotrends.model.utils import verified_mongo

MIN_PROP = 0.05


def match_tag(tag, selector):
    """

    :param dict tag: Tag dictionary
    :param dict selector: Dictionary of tag properties, e.g.
        `{'realign': {'label': 'realign'}}`
    :return bool: Match

    """
    for key, value in selector.items():
        if tag.get(key) != value:
            return False
    return True


def compute_positions(tags, selectors):
    """Compute positions of tags in documents, averaging across all document
    types common to the tags of interest.

    :param list tags: List of tags
    :param dict selectors: Dictionary mapping label to dictionary of tag
        properties, e.g. `{'realign': {'label': 'realign'}}`
    :return tuple: Tuple of:
        positions: Dictionary mapping labels to average position
        documents: List of document types common to tags

    """
    documents = {'html', 'pdf', 'pmc'}
    match_tags = {}
    tag_positions = {}

    for name, selector in selectors.items():
        matches = [
            tag
            for tag in tags
            if match_tag(tag, selector)
        ]
        if len(matches) != 1:
            continue
        match = matches[0]
        match_tags[name] = match
        documents = documents.intersection(match['span'].keys())

    for name, tag in match_tags.items():
        avg = np.mean([
            np.mean(tag['span'][document])
            for document in documents
        ])
        tag_positions[name] = avg
    
    return tag_positions, documents


def compute_ranks(positions):
    """Compute normalized rank orders over a set of label positions. Ranks
    range from 0.0 (first in sequence) to 1.0 (last). Because a constant is
    added to each rank such that ranks average to 0.5, the first rank will
    always be slightly greater than 0.0, and the last less than 1.0

    :param list positions:
    :return dict: Dictionary mapping labels to ranks

    """
    sorted_names = sorted(
        positions.keys(),
        key=lambda x: positions[x]
    )

    offset = 0.5 / float(len(sorted_names))

    return {
        name: offset + idx / float(len(sorted_names))
        for idx, name in enumerate(sorted_names)
    }


def analyze_rank_order(summary, collection, query=None):

    avg_ranks = collections.defaultdict(list)

    query = query or {}
    query.update(verified_mongo)
    cursor = collection.find(
        query,
        {'_id': True}
    )
    total = cursor.count()

    for article in cursor:

        # Note: Article may not be in summary, e.g. if it contains none of the
        # tags of interest; skip articles absent from summary
        ranks = summary.get(article['_id'], {})
        for label, rank in ranks.items():
            avg_ranks[label].append(rank)

    return [
        {
            'label': label,
            'sum': len(ranks),
            'prop': float(len(ranks)) / total,
            'avg': np.mean(ranks),
        }
        for label, ranks in avg_ranks.items()
    ]
