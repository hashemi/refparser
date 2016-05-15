from .utils import cached_property
from .exceptions import ReferenceSyntaxError, UnknownReferenceFormat
from .normalizers import normalize_page_range, \
    normalize_text_value, \
    normalize_list_direction

class RISRecord:
    @classmethod
    def parse(cls, data):
        in_record = False
        record = ''

        for line in data:
            if line.startswith('TY  - '):
                if in_record:
                    raise ReferenceSyntaxError
                record = line
                in_record = True
            elif line.startswith('ER  - '):
                if not in_record:
                    raise ReferenceSyntaxError
                record += line
                in_record = False
                yield cls(record)
            else:
                if in_record:
                    record += line

        if in_record:
            # reached end of file with an open record
            raise ReferenceSyntaxError

    def __init__(self, raw_data):
        self._raw_data = raw_data

    def raw_fields(self):
        'Returns a generator of tuples containing each raw fields name and value.'
        for line in self._raw_data.splitlines():
            try:
                field, value = line.split('  - ', 1)
                if len(field) == 2:
                    yield (field, value)
            except ValueError: # couldn't split into 2
                pass

    @cached_property
    def _raw_fields_aggregate(self):
        aggregate = {}
        for field, value in self.raw_fields():
            if not field in aggregate:
                aggregate[field] = []
            aggregate[field].append(value)
        return aggregate

    def _first_raw_aggregate(self, *fields):
        """
        Retruns the first non-empty list values of within one field that match
        one of the field names passed or None if there was no match.
        """
        for field in fields:
            if field in self._raw_fields_aggregate:
                return self._raw_fields_aggregate[field]

    def _first_raw_value(self, *fields):
        """
        Retruns the first value of the first field that matches one of the
        field names passed or None if there was no match.
        """
        aggregate = self._first_raw_aggregate(*fields)
        if aggregate:
            return aggregate[0]

    def _all_raw_values(self, *fields):
        """
        Returns all values that match any of the passed fields or None if no values
        were found. The values are ordered by the order of the passed field names first
        then by the order in which they appear in the record.
        """
        values = []
        for field in fields:
            if field in self._raw_fields_aggregate:
                values += self._raw_fields_aggregate[field]
        if values: return values

    @cached_property
    def title(self):
        return self._first_raw_value('TI', 'T1')


    @cached_property
    def abstract(self):
        value = self._first_raw_aggregate('AB', 'N2')

        # some records break the abstract into several records
        if value: return '\n'.join(value)

    @cached_property
    def authors(self):
        return self._all_raw_values('AU', 'A1', 'A2', 'A3')

    @cached_property
    def journal_names(self):
        # a record may include multiple names (eg, abbreviated & full)
        value = self._all_raw_values('JA', 'JO', 'JF')
        if value:
            return set(value)

    @cached_property
    def issn(self):
        return self._first_raw_value('SN')

    @cached_property
    def volume(self):
        return self._first_raw_value('VL')

    @cached_property
    def issue(self):
        return self._first_raw_value('IS')

    @cached_property
    def _pages(self):
        start = self._first_raw_value('SP')
        end = self._first_raw_value('EP')
        if start and not end:
            if '-' in start:
                start, end = start.split('-', 1)
        return (start, end)

    @cached_property
    def start_page(self):
        return self._pages[0]

    @cached_property
    def end_page(self):
        return self._pages[1]

    @cached_property
    def authors_lastnames(self):
        def guess_lastname(author):
            if ',' in author:
                # Lastname, F. or Lastname, Firstname
                return author.split(',', 1)[0]
            elif author.endswith('.'):
                # Lastname F.
                return author.split(' ', 1)[0]
            else:
                # Firstname Lastname
                return author.rsplit(' ', 1)[-1]

        return [guess_lastname(author) for author in self.authors]

    @cached_property
    def location_fingerprint(self):
        """
        Returns a fingerprint of the record containing the journals ISSN,
        volume, issue and pages. Returns None if any of this data is missing.
        """
        if None in (self.start_page, self.issue, self.volume, self.issn):
            return None

        return '$'.join((
                (normalize_page_range(self.start_page, self.end_page)),
                self.volume,
                self.issue,
                self.issn,))

    @cached_property
    def title_authors_fingerprint(self):
        """
        Returns a fingerprint of the record composed of the title and list of
        authors lastnames. Authors lastnames are listed alphabetically to
        keep them canonical as some records list the authors in a reverse order.
        """
        if None in (self.title, self.authors_lastnames):
            return None

        lastnames = list(map(normalize_text_value, self.authors_lastnames))
        lastnames = normalize_list_direction(lastnames)
        lastnames = '.'.join(lastnames)

        title = normalize_text_value(self.title)

        return '$'.join((lastnames, title))
