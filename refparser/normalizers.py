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

def is_head_heavy(items):
    """
    This algorthm takes a list of items and returns True if the first item is
    larger than the last item and False otherwise. If the items are equal,
    it repeats the test working its way from the outermost to inner most pair
    of items. If the list is symmetrical it returns False.
    """
    head = 0
    tail = len(items) - 1
    while head < tail:
        if items[head] > items[tail]:
            return True
        elif items[head] < items[tail]:
            return False
        head += 1
        tail -= 1
    return False

def normalize_list_direction(items):
    """
    Returns the list of items in ordered in a canonical direction. Given lists
    x and y, where y is in reverse order as x, this function should result in the
    same list when given either x or y.
    """
    return list(reversed(items)) if is_head_heavy(items) else items
