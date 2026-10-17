import unittest
from pathlib import Path
from assistant.capacity_conflict import capacity_records, capacity_conflict
from assistant.extraction import extract_logistic_hints
from assistant.units import check_source_quotes
from evaluation.equivalent import cases


class EquivalentNumberTests(unittest.TestCase):
    def test_equal_spellings_with_original_quotes(self):
        for name in ('trailing_zero','leading_dot','signed','scientific','integer','same_invalid'):
            text=Path(f'examples/equivalent/{name}.txt').read_text()
            record=capacity_records(text)
            self.assertEqual(record['relation'],'equivalent')
            self.assertTrue(all(q in text for q in record['source_quotes']))
            self.assertEqual(len(record['raw_values']),2)
            self.assertIsNone(capacity_conflict(text))
            hints=extract_logistic_hints(text)
            self.assertIsNotNone(hints)
            source={**hints['values'],'source_quotes':hints['source_quotes'],'rate_unit':hints['rate_unit'],'duration_unit':hints['duration_unit']}
            check_source_quotes(source,text)

    def test_no_tolerance_or_float_rounding_merges_distinct_values(self):
        for a,b in (('0.5','0.5001'),('5e-1','6e-1'),('0.5','0.50000000000000000001')):
            text=f'Logistic初始1.5个，容量{a}个，K={b}个，增长率0.2每天，模拟30天'
            self.assertIsNotNone(capacity_conflict(text))
            self.assertIsNone(extract_logistic_hints(text))

    def test_same_value_does_not_prove_complete_or_valid(self):
        text=Path('examples/equivalent/missing_rate.txt').read_text()
        self.assertEqual(capacity_records(text)['relation'],'equivalent')
        self.assertIsNone(extract_logistic_hints(text))
        invalid=Path('examples/equivalent/same_invalid.txt').read_text()
        self.assertFalse(extract_logistic_hints(invalid)['parameter_domain']['valid'])

    def test_scope(self):
        for text in ('Logistic容量0.5个，K=0.5只','Logistic种群甲容量0.5个，种群乙容量1个',
                     Path('examples/equivalent/corrected.txt').read_text()):
            self.assertIsNone(capacity_records(text))
