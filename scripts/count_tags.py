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


def count_tags_by_place():
    config.mongo['article'].map_reduce(
        tag_place_mapper,
        count_reducer,
        out={'replace': config.tag_place_counts_collection.name},
    )


def count_tags_by_author():
    config.mongo['article'].map_reduce(
        tag_author_mapper,
        count_reducer,
        out={'replace': config.tag_author_counts_collection.name},
    )


if __name__ == '__main__':
    count_tags()
    count_by_year()
    count_tags_by_year()
    count_tags_by_place()
    count_tags_by_author()

