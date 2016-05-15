from ..exceptions import UnknownReferenceFormat
from .ris import RISRecord
from .medline import MedlineRecord

def parse_records(data_file, data_format):
    """
    Generates records in raw data from a file containing multiple records.
    Currently accepts RIS and PubMed file formats.
    """
    if data_format == 'RIS':
        return (r._raw_data for r in RISRecord.parse(data_file))
    elif data_format == 'PubMed':
        return (r._raw_data for r in MedlineRecord.parse(data_file))
    else:
        raise UnknownReferenceFormat

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
    return MedlineRecord(raw_record).raw_fields()
