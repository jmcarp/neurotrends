# -*- coding: utf-8 -*-

import nameparser
from modularodm import StoredObject, fields, storage
from modularodm.query.querydialect import DefaultQueryDialect as Q

from neurotrends.config import mongo
from .utils import make_oid


name_parts = ['last', 'first', 'middle', 'suffix']


class Author(StoredObject):

    _id = fields.StringField(default=make_oid)

    last = fields.StringField()
    first = fields.StringField()
    middle = fields.StringField()
    suffix = fields.StringField()
    _full = fields.StringField()

    def update_name_parts(self, fullname):
        human_name = nameparser.HumanName(fullname)
        for attr in name_parts:
            value = getattr(human_name, attr) or None
            setattr(self, attr, value)

    def update_fullname(self):
        human_name = nameparser.HumanName('')
        for attr in name_parts:
            value = getattr(self, attr) or ''
            setattr(human_name, attr, value)
        self._full = unicode(human_name)


@Author.subscribe('before_save')
def update_fullname(schema, instance):
    instance.update_fullname()


Author.set_storage(storage.MongoStorage(mongo, 'author'))

