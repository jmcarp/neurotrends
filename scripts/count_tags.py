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
    emit(year, 1);
}''')


tag_year_mapper = Code('''function() {
    var year = this.date ? this.date.getFullYear() : null;
    for (var i=0; i<this.tags.length; i++) {
        emit(
            {
                label: this.tags[i].label,
                year: year
            },
            1
        );
    }
}''')


count_reducer = Code('''function(key, values) {
    var total = 0;
    for (var i=0; i<values.length; i++) {
        total += values[i];
    }
    return total;
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


if __name__ == '__main__':
    count_tags()
    count_by_year()
    count_tags_by_year()

