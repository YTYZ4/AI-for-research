import unittest
from pathlib import Path
from evaluation.immutable_regression import cases
from modeling_assistant.parameter_policy import parameters_locked, enforce_parameter_lock


class ImmutableBoundaryTests(unittest.TestCase):
    def test_synonyms_and_permissions(self):
        for phrase in ('不允许修改参数','不允许替换参数', '不要修改任何参数','不准更改参数','全部参数必须保持原样','保持原值不能调整','参数原封不动'):
            self.assertTrue(parameters_locked(phrase),phrase)
        for phrase in ('可以修改参数','并非禁止修改参数','不允许修改初值，但可以调整容量','参数恒定','容量不得小于零'):
            self.assertFalse(parameters_locked(phrase),phrase)

    def test_all_control_cases_cannot_be_taken_over(self):
        original={'status':'needs_clarification','questions':['请确认条件'],'model':None}
        for c in cases():
            with self.subTest(case=c['id']):
                text=Path(c['problem']).read_text()
                result,audit=enforce_parameter_lock(text,original)
                self.assertEqual(audit is not None,c['guard_allowed'])
                if not c['guard_allowed']:self.assertEqual(result,original)

    def test_valid_ready_never_blocked(self):
        for c in cases():
            if not c['id'].startswith('valid_'):continue
            original={'status':'ready','questions':[],'model':{'equilibrium':c['capacity'],'initial':c['initial']}}
            result,audit=enforce_parameter_lock(Path(c['problem']).read_text(),original)
            self.assertEqual(result,original)
            self.assertIsNone(audit)

    def test_existing_unsupported_has_no_takeover(self):
        c=cases()[0];original={'status':'unsupported','questions':['保持原值无法求解'],'model':None}
        result,audit=enforce_parameter_lock(Path(c['problem']).read_text(),original)
        self.assertIsNone(audit)
        self.assertEqual(result,original)
