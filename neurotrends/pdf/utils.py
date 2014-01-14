from bs4 import UnicodeDammit
import re

def pdf_clean(text):

    text = UnicodeDammit(text).unicode_markup
    text = re.sub(u'[\-\u2014]\n', '', text)
    text = re.sub('\s+', ' ', text)

    return text
