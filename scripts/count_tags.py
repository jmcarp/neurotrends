#!/usr/bin/env python
# encoding: utf-8

from bson import Code

from neurotrends import config


tag_mapper = Code('''function() {
    for (var i=0; i<this.tags.length; i++) {
        emit(this.tags[i].label, 1);
    }
}''')


year_mapper = Code('''function() {
    var year = this.date ? this.date.getFullYear() : null;
    if (this.verified.length) {
        emit(year, 1);
    }
}''')


place_mapper = Code('''function() {
    if (this.place && this.verified.length) {
        emit(this.place, 1);
    }
}''')


version_mapper = Code('''function() {
    var tag;
    for (var i=0; i<this.tags.length; i++) {
        tag = this.tags[i];
        if (tag.version) {
            emit(
                {
                    label: tag.label,
                    version: tag.version
                },
                1
            )
        }
    }
}''')


tag_year_mapper = Code('''function() {
    var year = this.date ? this.date.getFullYear() : null;
    for (var i=0; i<this.tags.length; i++) {
        emit(
            {
                year: year,
                label: this.tags[i].label,
            },
            1
        );
    }
}''')


tag_author_mapper = Code('''function() {
    for (var i=0; i<this.authors.length; i++) {
        for (var j=0; j<this.tags.length; j++) {
            emit(
                {
                    authorId: this.authors[i],
                    label: this.tags[j].label
                },
                1
            )
        }
    }
}''')


tag_place_mapper = Code('''function() {
    if (!this.place) {
        return;
    }
    for (var i=0; i<this.tags.length; i++) {
        emit(
            {
                place: this.place,
                label: this.tags[i].label
            },
            1
        )
    }
}''')


version_year_mapper = Code('''function() {
    var tag;
    var year = this.date ? this.date.getFullYear() : null;
    for (var i=0; i<this.tags.length; i++) {
        tag = this.tags[i];
        if (tag.version) {
            emit(
                {
                    year: year,
                    label: tag.label,
                    version: tag.version
                },
                1
            )
        }
    }
}''')


count_reducer = Code('''function(key, values) {
    var total = 0;
    for (var i=0; i<values.length; i++) {
        total += values[i];
    }
    return total;
}''')


def map_count_tags(mapper, output):
    config.article_collection.map_reduce(
        mapper,
        count_reducer,
        out={'replace': output.name},
        query={'tags': {'$ne': None}},
    )


count_jobs = [
    (tag_mapper, config.tag_counts_collection),
    (year_mapper, config.year_counts_collection),
    (place_mapper, config.place_counts_collection),
    (version_mapper, config.version_counts_collection),
    (tag_year_mapper, config.tag_year_counts_collection),
    (tag_place_mapper, config.tag_place_counts_collection),
    (tag_author_mapper, config.tag_author_counts_collection),
    (version_year_mapper, config.version_year_counts_collection),
]



def cache_counts():
    for job in count_jobs:
        map_count_tags(*job)
