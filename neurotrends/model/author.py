from modularodm import StoredObject, fields, storage
from modularodm.query.querydialect import DefaultQueryDialect as Q

from neurotrends.config import mongo
from .utils import make_oid

class Author(StoredObject):

    _id = fields.StringField(default=make_oid)

    last = fields.StringField()
    first = fields.StringField()
    middle = fields.StringField()
    suffix = fields.StringField()

Author.set_storage(storage.MongoStorage(mongo, 'author'))
