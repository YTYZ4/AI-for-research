import json
import tempfile
import unittest
from pathlib import Path
from evaluation.full_regression import cases, apply_question_checks, classify


class UnifiedRegressionTests(unittest.TestCase):
    def test_all_cases_unique_and_present(self):
        items=cases()
        self.assertEqual(len(items),47)
        self.assertEqual(len({c['id'] for c in items}),47)
        self.assertEqual(sum(c['kind']=='boundary' for c in items),12)
        for c in items:self.assertTrue(Path(c['problem']).is_file())

    def check_question(self,case_id,text):
        case=next(c for c in cases() if c['id']==case_id)
        row={'outcome':'pass'}
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            (p/'generation_record.json').write_text(json.dumps({'envelope':{'status':'needs_clarification','questions':[text],'model':None}}))
            audit=apply_question_checks(case,row,p)
        return row,audit

    def test_original_and_boundary_both_reject_integer_restriction(self):
        for name in ('DYN02_missing','capacity_zero','capacity_missing'):
            with self.subTest(name=name):
                row,audit=self.check_question(name,'请提供正整数容量K')
                self.assertEqual(row['outcome'],'fail')
                self.assertFalse(classify(row,{'format_repair':{'raw_schema_valid':True,'action':'not_needed'}})['original_pass'])
                row,audit=self.check_question(name,'请提供正实数容量K（可为小数，不要求整数）')
                self.assertTrue(audit['passed'])
                self.assertEqual(row['outcome'],'pass')

    def test_complete_case_rejects_unnecessary_confirmation(self):
        row,audit=self.check_question('capacity_above_capacity','请确认容量K=0.5是正实数')
        self.assertFalse(audit['passed'])
        self.assertEqual(row['outcome'],'fail')
