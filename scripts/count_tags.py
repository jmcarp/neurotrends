# -*- coding: utf-8 -*-

from bson import Code

from neurotrends.config import mongo, tag_counts


mapper = Code('''function() {
    for (var i=0; i<this.tags.length; i++) {
        emit(this.tags[i].label, 1);
    }
}''')


reducer = Code('''function(key, values) {
    var total = 0;
    for (var i=0; i<values.length; i++) {
        total += values[i];
    }
    return total;
}''')


if __name__ == '__main__':
    mongo['article'].map_reduce(
        mapper,
        reducer,
        out={'replace': tag_counts},
    )

