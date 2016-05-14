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
