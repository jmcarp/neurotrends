# -*- coding: utf-8 -*-

import factory
from faker import Faker
from tests.utils import DictFactory, ModularOdmFactory

from neurotrends import model


fake = Faker()


class AuthorFactory(ModularOdmFactory):

    FACTORY_FOR = model.Author

    last = factory.LazyAttribute(lambda x: fake.last_name())
    first = factory.LazyAttribute(lambda x: fake.first_name())
    middle = factory.LazyAttribute(lambda x: fake.first_name())


class RecordFactory(DictFactory):

    TI = factory.Sequence(
        lambda x: 'Structure of tobacco mosaic virus {0}'.format(x)
    )
    JT = factory.Sequence(lambda x: 'Nature {0}'.format(x))


class HTMLDocumentFactory(ModularOdmFactory):

    FACTORY_FOR = model.HTMLDocument


class PDFDocumentFactory(ModularOdmFactory):

    FACTORY_FOR = model.PDFDocument


class ArticleFactory(ModularOdmFactory):

    FACTORY_FOR = model.Article

    pmid = factory.Sequence(lambda x: str(x))
    doi = factory.Sequence(
        lambda x: '10.1016/j.neuroimage.2012.07.{0}'.format(x)
    )
    record = factory.SubFactory(RecordFactory)

    @factory.post_generation
    def authors(self, create, extracted, **kwargs):
        if create:
            if extracted:
                self.authors = extracted
            else:
                self.authors = [AuthorFactory() for _ in range(3)]

