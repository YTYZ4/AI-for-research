import unittest
from pathlib import Path
from evaluation.conflict import cases
from assistant.capacity_conflict import capacity_conflict, apply_parameter_policy


class CapacityConflictTests(unittest.TestCase):
    def test_conflicts_and_controls(self):
        for c in cases():
            with self.subTest(case=c['id']):
                evidence=capacity_conflict(Path(c['problem']).read_text())
                self.assertEqual(evidence is not None,bool(c['conflict_values']))
                if evidence:self.assertEqual(set(evidence['values']),set(c['conflict_values']))

    def test_conflict_precedes_invalid_locked_stop_and_ready(self):
        text=Path('examples/conflict/zero_positive.txt').read_text()
        for status in ('unsupported','ready'):
            original={'status':status,'questions':[],'model':None if status=='unsupported' else {'equilibrium':.5}}
            result,audit=apply_parameter_policy(text,original)
            self.assertEqual(result['status'],'needs_clarification')
            self.assertIsNone(result['model'])
            self.assertEqual(audit['original_envelope'],original)
            self.assertIn('0.5',result['questions'][0])

    def test_correct_clarification_is_native(self):
        text=Path('examples/conflict/zero_positive.txt').read_text()
        original={'status':'needs_clarification','questions':['容量K=0和0.5相互冲突，请核对哪条记录准确？'],'model':None}
        result,audit=apply_parameter_policy(text,original)
        self.assertEqual(result,original);self.assertIsNone(audit)

    def test_correction_multiple_populations_units_not_guessed(self):
        for text in ('Logistic种群甲容量0个，种群乙容量1个',
                     'Logistic容量0个，容量1只',
                     'Logistic容量0个，更正容量0.5个，以0.5个为准'):
            self.assertIsNone(capacity_conflict(text))

    def test_identical_invalid_still_stops(self):
        text=Path('examples/conflict/same_invalid.txt').read_text()
        result,audit=apply_parameter_policy(text,{'status':'needs_clarification','questions':['请提供新K'],'model':None})
        self.assertEqual(result['status'],'unsupported')
        self.assertNotIn('冲突',audit['reason'])
