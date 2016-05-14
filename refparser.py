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

class RISRecord:
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
