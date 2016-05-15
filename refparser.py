class ReferenceSyntaxError(Exception):
    """
    Syntax error during parsing.
    """
    pass

class UnknownReferenceFormat(Exception):
    """
    The format of the refrences data file is unknown.
    """
    pass

from normalizers import normalize_page_range

class RISRecord:
    def __init__(self, raw_data):
        self._raw_data = raw_data

        self._raw_fields_aggregate = {}
        for field, value in self.raw_fields():
            if not field in self._raw_fields_aggregate:
                self._raw_fields_aggregate[field] = []
            self._raw_fields_aggregate[field].append(value)

    def raw_fields(self):
        'Returns a generator of tuples containing each raw fields name and value.'
        for line in self._raw_data.splitlines():
            try:
                field, value = line.split('  - ', 1)
                if len(field) == 2:
                    yield (field, value)
            except ValueError: # couldn't split into 2
                pass

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

    @property
    def title(self):
        return self._first_raw_value('TI', 'T1')


    @property
    def abstract(self):
        value = self._first_raw_aggregate('AB', 'N2')

        # some records break the abstract into several records
        if value: return '\n'.join(value)

    @property
    def authors(self):
        return self._all_raw_values('AU', 'A1', 'A2', 'A3')

    @property
    def journal_names(self):
        # a record may include multiple names (eg, abbreviated & full)
        value = self._all_raw_values('JA', 'JO', 'JF')
        if value:
            return set(value)

    @property
    def issn(self):
        return self._first_raw_value('SN')

    @property
    def volume(self):
        return self._first_raw_value('VL')

    @property
    def issue(self):
        return self._first_raw_value('IS')

    @property
    def _pages(self):
        start = self._first_raw_value('SP')
        end = self._first_raw_value('EP')
        if start and not end:
            if '-' in start:
                start, end = start.split('-', 1)
        return (start, end)

    @property
    def start_page(self):
        return self._pages[0]

    @property
    def end_page(self):
        return self._pages[1]

    @property
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

    @property
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

def parse_records(data_file, data_format):
    """
    Generates records in raw data from a file containing multiple records.
    Currently accepts RIS and PubMed file formats.
    """
    if data_format == 'RIS':
        return _parse_records_ris(data_file)
    elif data_format == 'PubMed':
        return _parse_records_pubmed(data_file)
    else:
        raise UnknownReferenceFormat

def _parse_records_ris(data_file):
    in_record = False
    record = ''

    for l in data_file:
        if l.startswith('TY  - '):
            if in_record:
                raise ReferenceSyntaxError
            record = l
            in_record = True
        elif l.startswith('ER  - '):
            if not in_record:
                raise ReferenceSyntaxError
            record += l
            in_record = False
            yield record
        else:
            if in_record:
                record += l

    if in_record:
        # reached end of file with an open record
        raise ReferenceSyntaxError

def _parse_records_pubmed(data_file):
    record = ''

    for l in data_file:
        if l.strip() == '':
            # records are seperated by empty lines
            if record != '':
                yield record
                record = ''
        else:
            record += l
    if record != '':
        yield record

def parse_fields(raw_record, data_format):
    """
    Generates fields from the raw data of a single record.
    Currently only accepts the RIS file format.
    """
    if data_format == 'RIS':
        return _parse_fields_ris(raw_record)
    elif data_format == 'PubMed':
        return _parse_fields_pubmed(raw_record)
    else:
        raise UnknownReferenceFormat

def _parse_fields_ris(raw_record):
    return RISRecord(raw_record).raw_fields()

def _parse_fields_pubmed(raw_record):
    for l in raw_record.splitlines():
        try:
            field, value = l.split('- ', 1)
            if len(field) == 4:
                field = field.strip()
                yield (field, value)
        except ValueError:
            pass
