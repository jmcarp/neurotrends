import collections

from neurotrends import pattern
from neurotrends.model import mongo

variance_groups = {
    name: group.labels
    for name, group in pattern.tag_groups.items()
}

def cat_labels(names, groups):
    return sum([
        groups[name].labels
        for name in names
    ], [])

variance_groups['all'] = cat_labels(
    pattern.tag_groups.keys(),
    pattern.tag_groups
)

variance_groups['collection'] = cat_labels(
    ['mag', 'pulse', 'task', 'des'],
    pattern.tag_groups
)

variance_groups['analysis'] = cat_labels(
    ['pkg', 'proc', 'mod', 'mcc', 'tech'],
    pattern.tag_groups
)

articles = mongo['article'].find({'tags': {'$ne': []}}, {'tags': 1, 'date': 1})

def count_pipelines(articles):
    """Count number of pipelines and number of pipelines per year.
    Represents pipelines as nested tuples, e.g.

    ((('label', 'spm'), ('version', '5')), (('label', 'realign')))

    :param articles: Iterable of articles (PyMongo Cursor or list)
    :return: Dictionary mapping pipelines to counts; dictionary mapping
        count dictionaries to years

    """
    # Initialize counts
    count = collections.defaultdict(
        lambda: collections.defaultdict(int)
    )
    count_year= collections.defaultdict(
        lambda: collections.defaultdict(
            lambda: collections.defaultdict(int)
        )
    )

    for article in articles:

        date = article.get('date')
        year = date.year if date else None

        flat_groups = collections.defaultdict(tuple)

        for tag in article['tags']:

            # Flatten tag to list of tuples, excluding context
            flat_tag = [
                (key, value)
                for key, value in tag.items()
                if key != 'context'
            ]

            # Add flattened tag to matching groups
            for group, labels in variance_groups.items():
                if tag['label'] in labels:
                    flat_groups[group] += tuple(flat_tag)

        # Increment group counts
        for group in variance_groups:
            flat_tags = flat_groups[group]
            if flat_tags:
                count[group][flat_tags] += 1
                count_year[group][year][flat_tags] += 1

    # Return counts
    return count, count_year