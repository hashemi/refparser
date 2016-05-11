class ReferenceSyntaxError(Exception):
    """
    Syntax error during parsing.
    """
    pass

def parse_records(data_file, data_format):
    """
    Generates records in raw data from a file containing multiple records.
    Currently only accepts the RIS file format.    
    """
    if data_format != 'RIS':
        raise ReferenceSyntaxError
    
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
