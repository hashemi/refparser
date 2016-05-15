import unittest
from refparser.normalizers import *

class TestNormalizers(unittest.TestCase):
    def test_normalize_page_range(self):
        cases = (
            ((None, None), None),
            (('123', None), '123-123'),
            (('123', ''), '123-123'),
            ((None, '123'), None),
            (('123', '4'), '123-124'),
            (('111', '22'), '111-122'),
            (('123', '456'), '123-456'),
            (('99', '100'), '99-100'),
            (('123-34', None), '123-134'),
            (('123-34', ''), '123-134'),
        )
        for args, expected_result in cases:
            with self.subTest(args=args):
                self.assertEqual(
                    normalize_page_range(*args),
                    expected_result
                )

    def test_issn_mappings(self):
        cases = (
            ('1111-111Z', '1111-111Z'),
            (None, None),
            ('2151-4658', '2151-464X'),
            ('2151-464X', '2151-464X'),

        )
        for issn, expected_result in cases:
            with self.subTest(issn=issn):
                self.assertEqual(
                    normalize_issn(issn),
                    expected_result
                )

    def test_normalize_text_valie(self):
        cases = (
            ('Rodríguez', 'rodriguez'),
            (
                'Alcohol for robot lubrication — a systmeatic review.',
                'alcohol for robot lubrication a systmeatic review'
            ),
            (
                'Testing: when is it safe to stop?',
                'testing when is it safe to stop'
            ),
            (
                'Objectives: To test our theory.\nMethodology: Reasonable.',
                'objectives to test our theory methodology reasonable'
            )
        )
        for text, expected in cases:
            with self.subTest():
                self.assertEqual(
                    normalize_text_value(text),
                    expected
                )
