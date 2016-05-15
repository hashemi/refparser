from .ris import RISRecord

def parse_records(data_file, data_format):
    """
    Generates records in raw data from a file containing multiple records.
    Currently accepts RIS and PubMed file formats.
    """
    if data_format == 'RIS':
        return (r._raw_data for r in RISRecord.parse(data_file))
    elif data_format == 'PubMed':
        return _parse_records_pubmed(data_file)
    else:
        raise UnknownReferenceFormat

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
