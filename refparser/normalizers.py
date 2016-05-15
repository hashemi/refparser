import unicodedata
import re

def normalize_page_range(start, end):
    if start is None:
        return None

    if not end:
        if '-' in start:
            start, end = start.split('-', 1)
        else:
            end = ''

    if len(end) < len(start):
        end = start[:len(start)-len(end)] + end

    return '{}-{}'.format(start, end)

from .issn_mappings import _issn_mappings
def normalize_issn(issn):
    return _issn_mappings.get(issn, issn)

# From http://stackoverflow.com/q/34753821
def remove_accents(text):
    """This method removes all diacritic marks from the given string"""
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if not unicodedata.combining(c))
    return unicodedata.normalize('NFC', text)

def normalize_text_value(text):
    text = remove_accents(text)
    text = text.replace('&', ' and ')
    text = re.sub(r'[^a-zA-Z0-9\s]+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    text = text.lower()
    return text
