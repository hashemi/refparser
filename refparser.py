def parse_records(data_file, data_format):
    if data_format != 'RIS':
        raise Exception
    in_record = False
    record = ''
    for l in data_file:
        if l.startswith('TY  - '):
            if in_record:
                raise Exception
            record = l
            in_record = True
        elif l.startswith('ER  - '):
            if not in_record:
                raise Exception
            record += l
            in_record = False
            yield record
        else:
            if in_record:
                record += l
