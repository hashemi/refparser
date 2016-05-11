import unittest
from refparser import parse_records, parse_fields, ReferenceSyntaxError

class TestRefParser(unittest.TestCase):
    def test_parsing_records(self):
        """
        Parse all the records contained within a file and compare the first and
        last records to the contents of files containing the expected results.
        """
        records_files = (
            (
                'test_data/ris/valid.ris',
                'RIS',
                'test_data/ris/valid_first_record.ris',
                'test_data/ris/valid_last_record.ris',
            ),
            (
                'test_data/pubmed/valid.txt',
                'PubMed',
                'test_data/pubmed/valid_first_record.txt',
                'test_data/pubmed/valid_last_record.txt',
            )
        )

        for data_fn, data_format, first_exp_fn, last_exp_fn in records_files:
            with self.subTest(data_fn=data_fn, data_format=data_format):
                with open(data_fn, 'r') as data_file:
                    parsed_records = parse_records(data_file, data_format)
                    first_record = next(parsed_records)
                    last_record = first_record
                    for last_record in parsed_records: pass
                    for exp_fn, parsed_record in ((first_exp_fn, first_record), (last_exp_fn, last_record)):
                        with self.subTest(exp_fn=exp_fn):
                            with open(exp_fn, 'r') as exp_file:
                                exp_record = exp_file.read()
                            self.assertEqual(exp_record, parsed_record)

    def test_parsing_invalid_files(self):
        """
        Try to parse the records of invalid files and assert that they
        raise ReferenceSyntaxError as expected.
        """
        invalid_files = (
            ('ris/unclosed_first_record.ris', 'RIS'),
            ('ris/unclosed_last_record.ris', 'RIS'),
            ('ris/unopened_first_record.ris', 'RIS'),
            ('ris/unopened_last_record.ris', 'RIS'),
        )
        for filename, data_format in invalid_files:
            with self.subTest(filename=filename, data_format=data_format):
                with open('test_data/{filename}'.format(filename=filename)) as data_file:
                    with self.assertRaises(ReferenceSyntaxError):
                        for _ in parse_records(data_file, data_format): pass

    def test_parsing_fields(self):
        """
        Get the raw data of the first record from each file then parse that
        raw data into fields and compare it to the expected list of fields provided.
        """
        record_files_and_fields = (
            ('test_data/ris/valid.ris', 'RIS',
                [
                    ('TY', 'JOUR'),
                    ('ID', '123456'),
                    ('A1', 'Cushing, Harvey'),
                    ('ER', ''),
                ]
            ),
            ('test_data/pubmed/valid.txt', 'PubMed',
                [
                    ('PMID', '123456'),
                    ('OWN' , 'NLM'),
                    ('STAT', 'Publisher'),
                ]
            ),
        )
        for filename, data_format, expected_fields in record_files_and_fields:
            with self.subTest(filename=filename,
                data_format=data_format, expected_fields=expected_fields):
                with open(filename, 'r') as data_file:
                    first_record = next(parse_records(data_file, data_format))
                parsed_fields = list(parse_fields(first_record, data_format))
                self.assertEqual(parsed_fields, expected_fields)

if __name__ == '__main__':
    unittest.main()
