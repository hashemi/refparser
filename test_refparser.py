import unittest
from refparser import parse_records, parse_fields, ReferenceSyntaxError

class TestRefParser(unittest.TestCase):
    def match_parsed_records(self, data_filename, data_format, expected_record_filename,
        match_first_record=False, match_last_record=False):
        # one and only one can be true
        if match_first_record == match_last_record:
            raise

        with open(expected_record_filename, 'r') as expected_record_file:
            expected_record = expected_record_file.read()

        with open(data_filename, 'r') as data_file:
            parsed_records = parse_records(data_file, data_format)
            if match_first_record:
                parsed_record = next(parsed_records)
            elif match_last_record:
                for parsed_record in parsed_records: pass
        self.assertEqual(expected_record, parsed_record)

    def test_parse_ris_to_records(self):
        self.match_parsed_records('test_data/ris/valid.ris', 'RIS',
            'test_data/ris/valid_first_record.ris', match_first_record=True)

    def test_parse_ris_to_records_last_record(self):
        self.match_parsed_records('test_data/ris/valid.ris', 'RIS',
            'test_data/ris/valid_last_record.ris', match_last_record=True)

    def parse_invalid_ris(self, filename):
        with open('test_data/ris/{filename}'.format(filename=filename)) as data_file:
            with self.assertRaises(ReferenceSyntaxError):
                for _ in parse_records(data_file, 'RIS'): pass
    
    def test_parse_unclosed_first_record_ris(self):
        self.parse_invalid_ris('unclosed_first_record.ris')
    
    def test_parse_unclosed_last_record_ris(self):
        self.parse_invalid_ris('unclosed_last_record.ris')
    
    def test_parse_unopened_first_record_ris(self):
        self.parse_invalid_ris('unopened_first_record.ris')

    def test_parse_unopened_last_record_ris(self):
        self.parse_invalid_ris('unopened_last_record.ris')

    def test_parse_pubmed_to_records_first_record(self):
        self.match_parsed_records('test_data/pubmed/valid.txt', 'PubMed',
            'test_data/pubmed/valid_first_record.txt', match_first_record=True)
    
    def test_parse_pubmed_to_records_last_record(self):
        self.match_parsed_records('test_data/pubmed/valid.txt', 'PubMed',
            'test_data/pubmed/valid_last_record.txt', match_last_record=True)
    
    def test_parse_ris_fields(self):
        with open('test_data/ris/valid.ris', 'r') as data_file:
            first_record = next(parse_records(data_file, 'RIS'))
        parsed_fields = list(parse_fields(first_record, 'RIS'))
        expected_fields = [
            ('TY', 'JOUR'),
            ('ID', '123456'),
            ('A1', 'Cushing, Harvey'),
            ('ER', ''),
        ]
        self.assertEqual(parsed_fields, expected_fields)

if __name__ == '__main__':
    unittest.main()
