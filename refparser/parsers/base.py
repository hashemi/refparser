from ..utils import cached_property
from ..normalizers import normalize_page_range, \
    normalize_text_value, normalize_list_direction


class BaseRecord:
    title = abstract = authors = journal_names = issn = volume = issue = \
        property(lambda self: None)
    pages = property(lambda self: (None, None))

    def __init__(self, raw_data):
        self._raw_data = raw_data

    def raw_fields(self):
        """Returns a generator of tuples containing each raw fields name and
        value."""
        pass

    @cached_property
    def _raw_fields_aggregate(self):
        aggregate = {}
        for field, value in self.raw_fields():
            if field not in aggregate:
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
        Returns all values that match any of the passed fields or None if no
        values were found. The values are ordered by the order of the passed
        field names first then by the order in which they appear in the record.
        """
        values = []
        for field in fields:
            if field in self._raw_fields_aggregate:
                values += self._raw_fields_aggregate[field]
        if values:
            return values

    @cached_property
    def authors_lastnames(self):
        if self.authors is None:
            return None

        def guess_lastname(author):
            if not author:
                return author
            elif ',' in author:
                # Lastname, F. or Lastname, Firstname
                return author.split(',', 1)[0]
            elif author.endswith('.') or author[-1].isupper():
                # Lastname F. or Lastname F
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
        if None in (self.pages[0], self.issue, self.volume, self.issn):
            return None

        return '$'.join((
                (normalize_page_range(*self.pages)),
                self.volume,
                self.issue,
                self.issn,))

    @cached_property
    def title_authors_fingerprint(self):
        """
        Returns a fingerprint of the record composed of the title and list of
        authors lastnames. Authors lastnames are listed alphabetically to
        keep them canonical as some records list the authors in reverse order.
        """
        if None in (self.title, self.authors_lastnames):
            return None

        lastnames = list(map(normalize_text_value, self.authors_lastnames))
        lastnames = normalize_list_direction(lastnames)
        lastnames = '.'.join(lastnames)

        title = normalize_text_value(self.title)

        return '$'.join((lastnames, title))
