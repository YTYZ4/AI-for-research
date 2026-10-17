import unittest
from evaluation.clarification import parameters_locked, locked_question_score
from modeling_assistant.presentation import presentation_record


class LockedAndPresentationTests(unittest.TestCase):
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
