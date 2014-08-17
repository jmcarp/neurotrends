# -*- coding: utf-8 -*-

import os
import logging

from nameparser import HumanName
from pyquery import PyQuery
import dateutil.parser
import requests

from modularodm import StoredObject, Q, fields, storage
from sciscrape.utils import pubtools
from sciscrape.exceptions import ScrapeError

from neurotrends import pattern, tagger, util
from neurotrends.config import mongo, re

from .config import (
    VERIFY_THRESHOLD, SAVE_DIRS, EXTENSIONS, DOCUMENT_TYPES, OPENURL_URL,
    EMAIL_ADDR, SCRAPE_CLASS, SCRAPE_KWARGS, DOCUMENT_TYPES_TO_FIELDS,
)
from .document import HTMLDocument, PDFDocument
from .author import Author
from .utils import make_oid, get_institution


logger = logging.getLogger(__name__)
dateparser = dateutil.parser.parser()


DOCUMENT_MAP = {
    'pmc': {
        'class': HTMLDocument,
        'field': 'pubmed_html',
    },
    'html': {
        'class': HTMLDocument,
        'field': 'publisher_html',
    },
    'pdf': {
        'class': PDFDocument,
        'field': 'publisher_pdf',
    },
}


class Article(StoredObject):

    _id = fields.StringField(default=make_oid)

    record = fields.DictionaryField()
    _lrecord = fields.DictionaryField()
    date = fields.DateTimeField(index=True)
    pmid = fields.StringField(index=True)
    doi = fields.StringField(index=True)
    place = fields.StringField()

    authors = fields.ForeignField('Author', list=True, backref='wrote')

    publisher = fields.StringField()
    publisher_url = fields.StringField()

    pubmed_html = fields.ForeignField('HTMLDocument', backref='scraped')
    publisher_html = fields.ForeignField('HTMLDocument', backref='scraped')
    publisher_pdf = fields.ForeignField('PDFDocument', backref='scraped')
    verified = fields.StringField(list=True)

    tags = fields.DictionaryField('Tag', list=True)

    def _get_doi_openurl(self, save=True):
        """Look up DOI using CrossRef's OpenURL service. Pass enough
        information for unambiguous resolution.

        :param bool save: Save record if DOI is found

        """
        # Check required fields
        try:
            title = self.record['TI']
            aulast = self.authors[0].last
            year = self.date.year
        except:
            raise Exception('Article must include title, first author, and year.')

        # Note: OpenURL requests tend to get dropped; must set manual timeout,
        # else requests may never terminate
        data = requests.get(
            OPENURL_URL,
            params={
                'atitle': title,
                'aulast': aulast,
                'year': year,
                'noredirect': 'true',
                'pid': EMAIL_ADDR,
            },
            timeout=10
        )

        data_parsed = PyQuery(
            data.content.replace(' xmlns:', ' xmlnamespace:')
        )
        doi = data_parsed('doi').text()
        if doi:
            self.doi = doi
            if save:
                self.save()

    @classmethod
    def from_record(cls, record, doi=None):
        """Create instance of Article from a PubMed record.

        :param dict record: PubMed record from pubtools
        :param str doi: Optional DOI
        :return: New article

        """
        article = Article()

        # Store original record
        article.record = record

        # Add authors
        # FAU -> Full Author
        for author_name in record.get('FAU', []):
            human = HumanName(author_name)
            try:
                author = Author.find_one(
                    Q('last', 'eq', human.last) &
                    Q('first', 'eq', human.first) &
                    Q('middle', 'eq', human.middle) &
                    Q('suffix', 'eq', human.suffix)
                )
            except:
                author = Author(
                    last=human.last,
                    first=human.first,
                    middle=human.middle,
                    suffix=human.suffix,
                )
                author.save()
            article.authors.append(author)

        # Add date
        try:
            # DP -> Date of Publication
            article.date = dateparser.parse(record['DP'])
        except:
            pass

        # Add PMID
        article.pmid = record['PMID']

        # Get DOI from CrossRef
        if doi is None:
            try:
                article._get_doi_openurl(save=False)
            except:
                pass

        article.save()
        return article

    @classmethod
    def from_pmid(cls, pmid):
        records = pubtools.download_pmids([pmid])
        return cls.from_record(records[0])

    @classmethod
    def from_doi(cls, doi):
        pass

    def _get_filepath(self, document_type):
        """Build filepath.

        :param str document_type: Document type (html, pdf, pmc)
        :return str: Path to file

        """
        return os.path.join(
            SAVE_DIRS[document_type],
            '{}.{}'.format(
                self.pmid,
                EXTENSIONS[document_type]
            )
        )

    def _add_document(self, document_type, save=True):
        """Create document field corresponding to stored file.

        :param str document_type: Document type (html, pdf, pmc)
        :param bool save: Save record after update

        """
        filepath = self._get_filepath(document_type)
        if not os.path.exists(filepath):
            raise ValueError('File does not exist')
        document_class = DOCUMENT_MAP[document_type]['class']
        document_search = document_class.find(Q('filepath', 'eq', filepath))
        if document_search.count():
            document = document_search[0]
        else:
            document = DOCUMENT_MAP[document_type]['class'](
                filepath=filepath,
                document_type=document_type,
            )
            document.save()
        setattr(self, DOCUMENT_MAP[document_type]['field'], document)
        if save:
            self.save()

    def _remove_document(self, document_type):
        """Remove document field and any existing stored files.

        :param str document_type: Document type (html, pdf, pmc)

        """
        document_attr = DOCUMENT_MAP[document_type]['field']
        document = getattr(self, document_attr)
        if document:
            setattr(self, document_attr, None)
            document.remove_one(document)
            if document.filepath and os.path.exists(document.filepath):
                os.remove(document.filepath)
            if document.extract_filepath and os.path.exists(document.extract_filepath):
                os.remove(document.extract_filepath)

    def get_institution(self, save=True):
        affiliation = self.record.get('AD')
        if affiliation is None:
            return
        self.place = get_institution(affiliation)
        if save:
            self.save()

    def scrape(self, scraper=None, document_types=None, overwrite=False):
        """Fetch and save documents, then add to document fields.

        :param Scrape scraper: Article scraper; created if `None`
        :param list document_types: Document types to scrape; may include
            'pmc', 'html', and 'pdf'
        :param bool overwrite: Overwrite existing files

        """
        # Get default arguments
        scraper = scraper or SCRAPE_CLASS(**SCRAPE_KWARGS)
        document_types = document_types or DOCUMENT_TYPES

        # Skip files if document field and associated file already exist
        if not overwrite:
            for document_type in document_types:
                document = getattr(self, DOCUMENT_MAP[document_type]['field'])
                filepath = self._get_filepath(document_type)
                if document:
                    if filepath and os.path.exists(filepath):
                        # Document is complete; remove from fetch list
                        document_types.remove(document_type)
                    else:
                        # Document field exists, but file is missing; remove
                        # document and keep in fetch list
                        self._remove_document(document_type)
                else:
                    if os.path.exists(filepath):
                        # Document file exists, but field is empty; create
                        # document field pointing to file
                        self._add_document(document_type, save=False)

        # Delete existing documents fields and files
        else:
            for document_type in DOCUMENT_TYPES:
                self._remove_document(document_type)

        # Scrape files
        try:
            info = scraper.scrape(
                pmid=self.pmid,
                doi=self.doi,
                fetch_types=document_types,
            )
        except ScrapeError:
            logger.info('Could not scrape article')
            return

        # Save scraped files
        saved = info.save(self.pmid, save_dirs=SAVE_DIRS)

        # Create document objects and add to self
        for document_type in saved:
            self._add_document(document_type, save=False)

        # Add publisher information
        self.publisher = info.publisher
        self.publisher_url = info.pub_link

        self.save()

    def verify(self, threshold=VERIFY_THRESHOLD, overwrite=False, save=True):
        """Verify referenced documents.

        :param float threshold: Verification threshold
        :param bool overwrite: Overwrite existing verification info
        :param bool save: Save record after update

        """
        self.verified = [
            name
            for name, field in DOCUMENT_TYPES_TO_FIELDS.iteritems()
            if getattr(self, field) is not None
            and getattr(self, field).verify(threshold, overwrite=overwrite)
        ]
        if save:
            self.save()

    def tag(self, tag_groups=None, overwrite=False, save=True):
        """Add tags to article.

        :param list tag_groups: List of TagGroup objects
        :param bool overwrite: Overwrite existing tags
        :param bool save: Save record after update
        :return list: New or modified extracted tags

        """
        tag_groups = tag_groups or pattern.tag_groups.values()

        if overwrite:
            self.tags = []
            existing_tags = []
        else:
            existing_tags = [
                tagger.Tag(tag)
                for tag in self.tags
            ]

        new_tags = []

        self.verify(save=False)

        for document_type in self.verified:

            document_field = DOCUMENT_TYPES_TO_FIELDS[document_type]
            document = getattr(self, document_field)

            # Quit if document not set
            if document is None:
                continue

            doc = document.read()

            # Quit if document empty or fails verification
            if not doc:
                continue

            # Clean document text
            # TODO: Refactor as helper function
            doc = doc.replace(u'\u2044', '/')
            doc = doc.replace(u'\u2212', '-')
            doc = re.sub(r'[\s\-,]+', ' ', doc)

            for tag_group in tag_groups:

                # Extract tags
                tags = tagger.tag(tag_group, doc)

                for tag in tags:

                    # Build context documents
                    context_data = {document_type: tag['context']}
                    group_data = {document_type: tag['group']}
                    span_data = {document_type: tag['span']}

                    # Update existing tag with context
                    if tag in existing_tags:
                        idx = existing_tags.index(tag)
                        if document_type not in existing_tags[idx]['context']:
                            existing_tags[idx]['context'].update(context_data)
                            existing_tags[idx]['group'].update(group_data)
                            existing_tags[idx]['span'].update(span_data)
                            new_tags.append(existing_tags[idx])
                    # Create new tag in database
                    else:
                        tag['context'] = context_data
                        tag['group'] = group_data
                        tag['span'] = span_data
                        existing_tags.append(tag)
                        new_tags.append(tag)

        # Cast tags to dictionaries for ODM compatibility
        self.tags = [
            dict(tag)
            for tag in existing_tags
        ]

        if save:
            self.save()

        return new_tags

    def clear_tags(self, labels, save=True):
        """Delete all tags matching any of the provided labels.

        :param list labels: Labels of tags to delete
        :param bool save: Save record after update

        """
        self.tags = [
            tag
            for tag in self.tags
            if tag['label'] not in labels
        ]
        if save:
            self.save()


lrecord_fields = ['TI', 'JT']

@Article.subscribe('before_save')
def update_lrecord(schema, instance):
    lrecord = {
        key: instance.record[key]
        for key in lrecord_fields
        if key in instance.record
    }
    instance._lrecord = util.apply_recursive(
        util.string_lower,
        lrecord,
    )


Article.set_storage(storage.MongoStorage(mongo, 'article'))

