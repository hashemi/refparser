import unittest
from refparser import parse_records, ReferenceSyntaxError

class TestRefParser(unittest.TestCase):
    def test_parse_ris_to_records(self):
        with open('test_data/ris/valid_first_record.ris', 'r') as first_record_file:
            expected_first_record = first_record_file.read()
            with open('test_data/ris/valid.ris', 'r') as data_file:
                parsed_first_record = next(parse_records(data_file, 'RIS'))
                self.assertEqual(parsed_first_record, expected_first_record)
    
    def test_parse_ris_to_records_last_record(self):
        with open('test_data/ris/valid_last_record.ris', 'r') as last_record_file:
            expected_last_record = last_record_file.read()
            with open('test_data/ris/valid.ris', 'r') as data_file:
                for parsed_last_record in parse_records(data_file, 'RIS'): pass
                self.assertEqual(parsed_last_record, expected_last_record)

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
        with open('test_data/pubmed/valid_first_record.txt', 'r') as first_record_file:
            expected_first_record = first_record_file.read()
            with open('test_data/pubmed/valid.txt', 'r') as data_file:
                parsed_first_record = next(parse_records(data_file, 'PubMed'))
                self.assertEqual(parsed_first_record, expected_first_record)
    
    def test_parse_pubmed_to_records_last_record(self):
        with open('test_data/pubmed/valid_last_record.txt', 'r') as last_record_file:
            expected_last_record = last_record_file.read()
            with open('test_data/pubmed/valid.txt', 'r') as data_file:
                for parsed_last_record in parse_records(data_file, 'PubMed'): pass
                self.assertEqual(parsed_last_record, expected_last_record)

if __name__ == '__main__':
    unittest.main()
