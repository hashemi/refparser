import unittest
from refparser.parsers import RISRecord, MedlineRecord, parse_records, \
    parse_fields
from refparser.exceptions import ReferenceSyntaxError


class TestParsers(unittest.TestCase):
    def setUp(self):
        with open('test_data/ris/complex_record.ris') as f:
            ris_record = f.read()
        self.complex_ris_record = RISRecord(ris_record)

        with open('test_data/pubmed/complex_record.txt') as f:
            medline_record = f.read()
        self.complex_medline_record = MedlineRecord(medline_record)

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
                    for last_record in parsed_records:
                        pass
                    for exp_fn, parsed_record in ((first_exp_fn, first_record),
                                                  (last_exp_fn, last_record)):
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
                with open('test_data/{}'.format(filename)) as data_file:
                    with self.assertRaises(ReferenceSyntaxError):
                        for _ in parse_records(data_file, data_format):
                            pass

    def test_parsing_fields(self):
        """
        Get the raw data of the first record from each file then parse that
        raw data into fields and compare it to the expected list of fields
        provided.
        """
        record_files_and_fields = (
            ('test_data/ris/valid.ris', 'RIS',
                [
                    ('TY', 'JOUR'),
                    ('ID', '123456'),
                    ('A1', 'Cushing, Harvey'),
                    ('ER', ''),
                ]),
            ('test_data/pubmed/valid.txt', 'PubMed',
                [
                    ('PMID', '123456'),
                    ('OWN', 'NLM'),
                    ('AB', 'This is an example of a long field where the field might actually end up\nbeing broken down over multiple lines.'),
                    ('STAT', 'Publisher'),
                ]),
        )
        for filename, data_format, expected_fields in record_files_and_fields:
            with self.subTest(filename=filename,
                              data_format=data_format,
                              expected_fields=expected_fields):
                with open(filename, 'r') as data_file:
                    first_record = next(parse_records(data_file, data_format))
                parsed_fields = list(parse_fields(first_record, data_format))
                self.assertEqual(parsed_fields, expected_fields)

    def test_all_raw_values(self):
        self.assertEqual(
            self.complex_ris_record._all_raw_values('AU', 'A1'),
            ['Zoidberg J.A.', 'Leela, T.', 'Bender Bending Rodríguez',
                'Conrad, H.', 'Fansworth H.'])

    def test_first_raw_aggregate(self):
        self.assertEqual(
            self.complex_ris_record._first_raw_aggregate('AU', 'A1'),
            ['Zoidberg J.A.'])

    def test_first_raw_value(self):
        self.assertEqual(
            self.complex_ris_record._first_raw_value('AU', 'A1'),
            'Zoidberg J.A.')

    def test_nonexistant_raw_value(self):
        self.assertIsNone(
            self.complex_ris_record._first_raw_value('A2')
        )

    def test_ris_record_data(self):
        r = self.complex_ris_record
        comparisons = (
            (r.title, 'A systematic review of the safety and efficacy of performing surgery on human subjects by alien surgeons'),
            (r.abstract, 'Objective: With the increasing human population and their unhealthy habits, there has been a relative shortage in  surgeons with human experience. Some humans have resorted to surgeons with a alien experience to cover the shortage. In this systematic review, we evaluated the literature on outcomes of human surgery performed by alien surgeons. Methods: A librarian (TL) performed a search of 2,422 databases. The Universal Translater was used to translate all results into gibberish for the purposes of duplicate discovered and removal. Further duplicate removal by hand was performed by one reviewer (HC). A robot was available (BBR). Two independent reviewers (HC and AW) then screened the unique citations by title and abstract then by full-text content. Results: the initial search resulted in 2.7e21. The Universal Translater removed 1.5e21 duplicates and another 1.2e21 duplicates were removed by hand. There were 1.2 million unique citations screened by title and abstract and 23 by full-text. Two citations met the inclusion criteria, both were from the same group (the authors group). Conclusion: Human surgery by alien surgeons is a promising alternative to cover the shortage of human surgeons. However, data on the safety of this practice are lacking. More research in this area is needed.'),
            (r.authors, ['Zoidberg J.A.', 'Leela, T.',
                         'Bender Bending Rodríguez', 'Conrad, H.',
                         'Fansworth H.']),
            (r.authors_lastnames, ['Zoidberg', 'Leela', 'Rodríguez', 'Conrad',
                                   'Fansworth']),
            (r.journal_names, {'Journal of Earth Creatures Surgery',
                               'J. Ear. Creat. Surg.'}),
            (r.issn, '9919-991X'),
            (r.volume, '23119'),
            (r.issue, '4'),
            (r.pages, ('370', '374')),
        )

        record_values, expected_values = zip(*comparisons)

        self.assertEqual(record_values, expected_values)

    def test_medline_record_data(self):
        self.maxDiff = None
        r = self.complex_medline_record
        comparisons = (
            (r.title, 'A systematic review of the safety and efficacy of performing surgery on human\nsubjects by alien surgeons'),
            (r.abstract,
                """Objective: With the increasing human population and their unhealthy habits,
there has been a relative shortage in  surgeons with human experience. Some
humans have resorted to surgeons with a alien experience to cover the shortage.
In this systematic review, we evaluated the literature on outcomes of human
surgery performed by alien surgeons. Methods: A librarian (TL) performed a
search of 2,422 databases. The Universal Translater was used to translate all
results into gibberish for the purposes of duplicate discovered and removal.
Further duplicate removal by hand was performed by one reviewer (HC). A robot
was available (BBR). Two independent reviewers (HC and AW) then screened the
unique citations by title and abstract then by full-text content. Results:
the initial search resulted in 2.7e21. The Universal Translater removed 1.5e21
duplicates and another 1.2e21 duplicates were removed by hand. There were 1.2
million unique citations screened by title and abstract and 23 by full-text.
Two citations met the inclusion criteria, both were from the same group (the
authors group). Conclusion: Human surgery by alien surgeons is a promising
alternative to cover the shortage of human surgeons. However, data on the safety
of this practice are lacking. More research in this area is needed."""),
            (r.authors, ['Zoidberg, JA', 'Leela, T', 'Rodríguez, BB',
                         'Conrad, H', 'Fansworth, H']),
            (r.authors_lastnames, ['Zoidberg', 'Leela', 'Rodríguez',
                                   'Conrad', 'Fansworth']),
            (r.journal_names, {'Journal of earth creatures surgery',
                               'J Ear Creat Surg'}),
            (r.issn, '9919-991X'),
            (r.volume, '23119'),
            (r.issue, '4'),
            (r.pages, ('370', '4')),
        )

        record_values, expected_values = zip(*comparisons)

        self.assertEqual(record_values, expected_values)

    def test_ris_record_location_fingerprint(self):
        for r in (self.complex_ris_record, self.complex_medline_record):
            with self.subTest(record_type=type(r).__name__):
                self.assertEqual(
                    r.location_fingerprint,
                    '370-374$23119$4$9919-991X'
                )

    def test_records_title_authors_fingerprint(self):
        for r in (self.complex_ris_record, self.complex_medline_record):
            with self.subTest(record_type=type(r).__name__):
                self.assertEqual(
                    r.title_authors_fingerprint,
                    'fansworth.conrad.rodriguez.leela.zoidberg$a systematic review of the safety and efficacy of performing surgery on human subjects by alien surgeons'
                )
