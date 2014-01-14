"""
Group articles by permuations of tags, versions, years, and custom fields
using map-reduce in MongoDB.
"""

from bson.code import Code

map_func = Code('''
    function () {
        var tag, year;
        for (var idx = 0; idx < this.tags.length; idx++) {
            tag = this.tags[idx];
            date = this.date ? this.date.getFullYear() : null;
            emit({
                label: tag.label,
            }, {ids: [this._id]});
            emit({
                date: date,
                label: tag.label,
            }, {ids: [this._id]});
            emit({
                date: date,
                label: tag.label,
                version: tag.version,
            }, {ids: [this._id]});
        }
    }
''')

reduce_func = Code('''
    function (key, values) {
        var ids = [];
        for (var vidx = 0; vidx < values.length; vidx++) {
            ids.concat(values[vidx].ids);
        }
        return {ids: ids};
    }
''')
