"""

"""

from __future__ import division

from subprocess import CalledProcessError
from bs4 import BeautifulSoup
import HTMLParser
import os
import re

from modularodm import StoredObject, fields, storage

from neurotrends.pdf.pdfxtract import pdfminer_extract, pypdf_extract
from neurotrends.pdf.pdfocr import pdf_ocr
from neurotrends.config import mongo
from neurotrends.util import mkdir_p

from .config import EXTRACT_SAVE_DIRS, PDF_MIN_LENGTH
from .utils import make_oid, to_unicode

parser = HTMLParser.HTMLParser()

class Document(StoredObject):

    _id = fields.StringField(default=make_oid)
    document_type = fields.StringField()

    filepath = fields.StringField()
    extract_filepath = fields.StringField()
    url = fields.StringField()

    verification_score = fields.FloatField()

    extract_path = fields.StringField()
    extracted = fields.BooleanField()

    _meta = {
        'abstract': True,
    }

    def read(self):
        raise NotImplementedError

    def text_file_name(self):

        _, tail = os.path.split(self.filepath)
        root, _= os.path.splitext(tail)
        return '{}.txt'.format(root)

    def save_extract(self, text, save=True, **kwargs):

        path = EXTRACT_SAVE_DIRS[self.document_type]
        if not os.path.exists(path):
            mkdir_p(path)

        filepath = os.path.join(path, self.text_file_name())
        self.extract_filepath = filepath
        self.extracted = True

        for key, value in kwargs.iteritems():
            setattr(self, key, value)

        open(filepath, 'w').write(
            to_unicode(text).encode('utf-8')
        )

        if save:
            self.save()

    def verify(self, threshold, overwrite=False):
        """Verify that the document matches the target article: checks that
        the document contains a minimum fraction of words in the article
        abstract.

        :param float threshold: Minimum fraction of abstract words present
        :param bool overwrite: Recalculate existing verification score
        :return bool: Article is verified

        """
        # Return stored
        if self.verification_score and not overwrite:
            return self.verification_score > threshold

        text = self.read()

        # Load target article
        try:
            article = self.article__scraped[0]
        except IndexError:
            return False

        # AB -> Abstract
        abstract = article. record.get('AB', None)

        if not text or not abstract:
            return False

        text = text.lower()
        abstract = abstract.lower()

        abstract_tokens = re.split(r'\s+', abstract)
        tokens_contained = [
            token
            for token in abstract_tokens
            if token in text
        ]
        prop_contained = len(tokens_contained) / len(abstract_tokens)

        self.verification_score = prop_contained
        self.save()

        return prop_contained >= threshold

class HTMLDocument(Document):

    def read(self, overwrite=False):

        # Read from extracted file if exists
        if not overwrite:
            if self.extract_filepath and os.path.exists(self.extract_filepath):
                return to_unicode(open(self.extract_filepath).read())

        if not self.filepath or not os.path.exists(self.filepath):
            return

        # Convert to plain text
        html = open(self.filepath, 'r').read()

        # Pad TDs
        html = re.sub(
            r'<td(.*?)>(.*?)</td>',
            r'<td\\1> \\2 </td>',
            html,
            flags=re.I
        )

        # Parse HTML
        soup = BeautifulSoup(html)

        # Remove <script> tags
        for elm in soup.findAll('script'):
            elm.extract()

        # Extract text
        text = ''.join(soup.findAll(text=True))

        # Unescape HTML
        text = parser.unescape(text)

        self.save_extract(text)

        # Update document
        self.save()

        return text

HTMLDocument.set_storage(storage.MongoStorage(mongo, 'htmldocument'))

class PDFDocument(Document):

    extract_method = fields.StringField()

    def read(self, overwrite=False):

        # Read from extracted file if exists
        if not overwrite:
            if self.extract_filepath and os.path.exists(self.extract_filepath):
                return to_unicode(open(self.extract_filepath).read())

        if not self.filepath or not os.path.exists(self.filepath):
            return

        text = None

        # Try extracting using PDFMiner; wrap in try-except in case of
        # unpredictable errors
        try:
            text = pdfminer_extract(self.filepath)
        except:
            pass
        if text and len(text) > PDF_MIN_LENGTH:
            self.save_extract(text, extract_method='pdfminer')
            return to_unicode(text)

        # Try extracting using PyPDF2
        try:
            text = pypdf_extract(self.filepath)
        except:
            pass
        if text and len(text) > PDF_MIN_LENGTH:
            self.save_extract(text, extract_method='pypdf2')
            return to_unicode(text)

        # Extract using Tesseract, catching miscellaneous subprocess errors
        try:
            text = pdf_ocr(self.filepath)
        except CalledProcessError:
            pass
        if text and len(text) > PDF_MIN_LENGTH:
            self.save_extract(text, extract_method='tesseract')
            return to_unicode(text)

PDFDocument.set_storage(storage.MongoStorage(mongo, 'pdfdocument'))
