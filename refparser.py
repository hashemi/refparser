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
        else:
            record += l
    if record != '':
        yield record
