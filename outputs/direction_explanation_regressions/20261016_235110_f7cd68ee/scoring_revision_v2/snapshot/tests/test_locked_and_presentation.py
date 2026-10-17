import unittest
from evaluation.clarification import parameters_locked, locked_question_score
from modeling_assistant.presentation import presentation_record, system_description
from modeling_assistant.parameter_policy import enforce_parameter_lock
from pathlib import Path


class LockedAndPresentationTests(unittest.TestCase):
    def test_invalid_locked_logistic_preserves_original_response(self):
        text=Path('examples/development_variants/DYN02_error.txt').read_text()
        original={'status':'needs_clarification','questions':['请提供正实数容量K'],'model':None}
        result,audit=enforce_parameter_lock(text,original)
        self.assertEqual(result['status'],'unsupported')
        self.assertEqual(audit['original_envelope'],original)
        self.assertEqual(audit['evidence']['values']['equilibrium'],0)
        self.assertTrue(locked_question_score(result)['passed'])
        self.assertEqual(original['status'],'needs_clarification')

    def test_policy_does_not_override_missing_valid_or_unlocked(self):
        original={'status':'needs_clarification','questions':['请补充条件'],'model':None}
        for name in ('missing','above_capacity','zero'):
            text=Path(f'examples/capacity_boundaries/{name}.txt').read_text()
            if name!='zero':text+='不得改动参数。'
            result,audit=enforce_parameter_lock(text,original)
            self.assertIsNone(audit)
            self.assertEqual(result,original)

    def test_unsupported_template_does_not_request_changes(self):
        record={"envelope":{"status":"unsupported","model":None},"stages":[]}
        text=system_description(record)
        self.assertNotIn("补充",text)
        self.assertIn("原题条件保持不变",text)

    def test_lock_detection(self):
        for text in ('不得取绝对值或改动参数','不得替换容量数值','禁止修改参数'):
            self.assertTrue(parameters_locked(text))
        self.assertFalse(parameters_locked('如果参数无效请提供纠正建议'))

    def test_reject_previous_suggestion_and_replacement_requests(self):
        for text in ('请提供正的冷却系数数值，或说明是否应将符号视为笔误并修正为0.1？',
                     '是否允许修改参数？','请提供正实数容量K（可为小数）',
                     '不能修改参数，但可以取绝对值'):
            self.assertFalse(locked_question_score({'questions':[text]})['passed'],text)

    def test_explain_without_suggesting_replacement(self):
        for text in ('k=-0.1超出当前支持范围；按要求不修改参数，当前无法求解。',
                     'K=0导致除零，原题禁止替换数值，当前模型不支持。',
                     '不能取绝对值或改为正数；当前不支持负系数。'):
            self.assertTrue(locked_question_score({'questions':[text]})['passed'],text)

    def test_preserve_math_and_remove_implementation(self):
        math=['封闭系统，无迁入迁出','动态系统参数恒定','按CSV的train/test划分，不使用test选阶','留出集仅用于报告RMSE，不参与选阶']
        behavior=['增长率与时长单位不同时由求解器按给定单位换算。','系统输出不包含拟合系数','程序将小时换算为天']
        record={'envelope':{'model':{'assumptions':math+behavior}},'stages':[]}
        shown,audit=presentation_record(record)
        self.assertEqual(shown['envelope']['model']['assumptions'],math)
        self.assertEqual(record['envelope']['model']['assumptions'],math+behavior)
        self.assertEqual(len(audit['suppressed_display_only']),3)
