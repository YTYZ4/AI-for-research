import unittest
from evaluation.full_regression import cases,classify

class FullRegressionTests(unittest.TestCase):
    def test_scope_no_duplicate_questions(self):
        cs=cases();self.assertEqual(len(cs),47);self.assertEqual(len({c['problem'] for c in cs}),47)
        self.assertEqual(sum(c['kind']=='original' for c in cs),8)
    def test_native_repaired_guarded_are_separate(self):
        row={'outcome':'pass'}
        native=classify(row,{'format_repair':{'raw_schema_valid':True,'action':'not_needed'}})
        fixed=classify(row,{'format_repair':{'raw_schema_valid':False,'action':'applied'}})
        guarded=classify(row,{'format_repair':{'raw_schema_valid':True,'action':'not_needed'},'local_validation':{'action':'needs_clarification'}})
        self.assertTrue(native['original_pass']);self.assertFalse(fixed['original_pass']);self.assertTrue(fixed['after_format_pass'])
        self.assertFalse(guarded['after_format_pass']);self.assertTrue(guarded['final_pass'])
    def test_valid_schema_with_wrong_math_is_not_pass(self):
        r=classify({'outcome':'fail'},{'format_repair':{'raw_schema_valid':True,'action':'not_needed'}})
        self.assertTrue(r['raw_schema_valid']);self.assertFalse(r['original_pass']);self.assertFalse(r['final_pass'])
