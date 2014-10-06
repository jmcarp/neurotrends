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


class _Jobs(object):

    def __init__(self):
        self.jobs = []

    def register(self, out, mapper, reducer=count_reducer, collection='article'):
        def job():
            config.mongo[collection].map_reduce(
                mapper,
                reducer,
                out={'replace': out.name},
                query={'tags': {'$ne': None}},
            )
        self.jobs.append(job)

    def run(self):
        for job in self.jobs:
            job()


Jobs = _Jobs()


Jobs.register(config.tag_counts_collection, tag_mapper)
Jobs.register(config.year_counts_collection, year_mapper)
Jobs.register(config.place_counts_collection, place_mapper)
Jobs.register(config.version_counts_collection, version_mapper)
Jobs.register(config.tag_year_counts_collection, tag_year_mapper)
Jobs.register(config.tag_place_counts_collection, tag_place_mapper)
Jobs.register(config.tag_author_counts_collection, tag_author_mapper)
Jobs.register(config.version_year_counts_collection, version_year_mapper)


if __name__ == '__main__':
    Jobs.run()

