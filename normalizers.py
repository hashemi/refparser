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

from issn_mappings import _issn_mappings
def normalize_issn(issn):
    return _issn_mappings.get(issn, issn)
