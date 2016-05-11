import unittest
import io
from refparser import parse_records

class TestRefParser(unittest.TestCase):
    def test_ris_to_records(self):
        ris_data = \
"""
TY  - JOUR
ID  - 123456
A1  - Cushing, Harvey
ER  - 

Data in between

TY  - JOUR
ID  - 654321
A1  - Hashimoto, Hakaru
ER  - 
"""
        expected_first_record = \
"""TY  - JOUR
ID  - 123456
A1  - Cushing, Harvey
ER  - 
"""
        ris_file = io.StringIO(ris_data)
        parsed_first_record = next(parse_records(ris_file, 'RIS'))
        self.assertEqual(parsed_first_record, expected_first_record)

if __name__ == '__main__':
    unittest.main()
