import json
import tempfile
import unittest
from pathlib import Path
from evaluation.full_regression import cases, apply_question_checks, classify, check_quote_repair


class UnifiedRegressionTests(unittest.TestCase):
    def test_all_cases_unique_and_present(self):
        items=cases()
        self.assertEqual(len(items),89)
        self.assertEqual(len({c['id'] for c in items}),89)
        self.assertEqual(sum(c['kind']=='boundary' for c in items),12)
        self.assertEqual(sum(len(c['origins']) for c in items),91)
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

    def test_new_conflict_and_missing_semantics(self):
        row,audit=self.check_question('immutable_conflicting_capacity','容量0和0.5存在冲突，请核对哪条准确？')
        self.assertTrue(audit['passed'])
        row,audit=self.check_question('immutable_conflicting_capacity','容量0和0.5存在冲突，请提供正实数K')
        self.assertFalse(audit['passed'])
        row,audit=self.check_question('conflict_missing_rate','请提供增长率r及其时间单位')
        self.assertTrue(audit['passed'])

    def test_quote_audit_rejects_changed_math(self):
        case={'problem':'examples/equivalent_boundaries/leading_dot.txt'}
        before={'equilibrium':.5,'source_quotes':{'equilibrium':'错误引用'}}
        after={'equilibrium':.5,'source_quotes':{'equilibrium':'环境容量恒定.5个'}}
        audit={'original_model':before,'changes':[{'field':'equilibrium','original':'错误引用','replacement':'环境容量恒定.5个'}]}
        metadata={'source_quote_repair':audit,'source_model':after,'response':{'choices':[{'message':{'content':json.dumps({'model':before})}}]}}
        with tempfile.TemporaryDirectory() as d:
            self.assertTrue(check_quote_repair(case,metadata,Path(d))['passed'])
            after['equilibrium']=.6
            self.assertFalse(check_quote_repair(case,metadata,Path(d))['passed'])
