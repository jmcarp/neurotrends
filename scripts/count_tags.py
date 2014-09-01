# -*- coding: utf-8 -*-

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
    var counts = {};
    for (var i=0; i<this.tags.length; i++) {
        counts[this.tags[i].label] = 1;
    }
    for (var i=0; i<this.authors.length; i++) {
        emit(this.authors[i], counts);
    }
}''')


count_reducer = Code('''function(key, values) {
    var total = 0;
    for (var i=0; i<values.length; i++) {
        total += values[i];
    }
    return total;
}''')


count_object_reducer = Code('''function(key, values) {
    var counts = {};
    var labels, label, count;
    for (var i=0; i<values.length; i++) {
        labels = Object.keys(values[i]);
        for (var j=0; j<labels.length; j++) {
            label = labels[j];
            count = values[i][label];
            counts[label] = counts[label] ? counts[label] + count : count;
        }
    }
    return counts;
}''')


def count_tags():
    config.mongo['article'].map_reduce(
        tag_mapper,
        count_reducer,
        out={'replace': config.tag_counts_collection.name},
    )


def count_by_year():
    config.mongo['article'].map_reduce(
        year_mapper,
        count_reducer,
        out={'replace': config.year_counts_collection.name},
    )


def count_tags_by_year():
    config.mongo['article'].map_reduce(
        tag_year_mapper,
        count_reducer,
        out={'replace': config.tag_year_counts_collection.name},
    )


def count_tags_by_author():
    config.mongo['article'].map_reduce(
        tag_author_mapper,
        count_object_reducer,
        out={'replace': config.tag_author_counts_collection.name},
    )


if __name__ == '__main__':
    count_tags()
    count_by_year()
    count_tags_by_year()
    count_tags_by_author()

