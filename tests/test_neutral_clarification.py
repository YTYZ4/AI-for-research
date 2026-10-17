import unittest
from pathlib import Path
from assistant.capacity_conflict import apply_parameter_policy
from assistant.dimension_policy import fix_dimension_question, wrong_rate_capacity_comparison


class NeutralClarificationTests(unittest.TestCase):
    def test_conflict_removes_positive_value_hint(self):
        text=Path('examples/conflict/zero_positive.txt').read_text()
        for suffix in ('请提供正实数K','建议采用0.5','K必须大于0','请提供有效容量'):
            original={'status':'needs_clarification','questions':['容量0与0.5冲突，请核对。'+suffix],'model':None}
            result,audit=apply_parameter_policy(text,original)
            self.assertIsNotNone(audit)
            self.assertNotIn(suffix,result['questions'][0])
            self.assertEqual(audit['original_envelope'],original)

    def test_all_negative_still_neutral(self):
        text=Path('examples/conflict/all_negative.txt').read_text()
        result,audit=apply_parameter_policy(text,{'status':'unsupported','questions':['K必须为正'],'model':None})
        self.assertEqual(result['status'],'needs_clarification')
        self.assertIn('-1',result['questions'][0]);self.assertIn('-2',result['questions'][0])
        self.assertNotIn('正实数',result['questions'][0])

    def test_wrong_dimension_question_repaired_with_audit(self):
        text=Path('examples/conflict/missing.txt').read_text()
        original={'status':'needs_clarification','questions':['请确认增长率与容量K的单位是否一致'],'model':None}
        result,audit=fix_dimension_question(text,original)
        self.assertIsNotNone(audit)
        self.assertEqual(audit['original_envelope'],original)
        self.assertIn('不要求单位一致',result['questions'][0])
        self.assertFalse(wrong_rate_capacity_comparison(result['questions'][0]))

    def test_legitimate_unit_questions_unchanged(self):
        text=Path('examples/conflict/missing.txt').read_text()
        for q in ('请提供容量K及其数量单位','请核对初值与容量K的数量单位','请提供增长率的时间单位','增长率与容量K不要求单位一致'):
            original={'status':'needs_clarification','questions':[q],'model':None}
            result,audit=fix_dimension_question(text,original)
            self.assertIsNone(audit);self.assertEqual(result,original)

    def test_no_guess_when_rate_missing(self):
        text=Path('examples/conflict/missing_rate.txt').read_text()
        original={'status':'needs_clarification','questions':['请提供增长率及单位'],'model':None}
        result,audit=fix_dimension_question(text,original)
        self.assertIsNone(audit);self.assertEqual(result,original)
