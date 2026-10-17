import copy
import json
import unittest
from pathlib import Path
from modeling_assistant.parameter_policy import has_replacement_suggestion
from modeling_assistant.capacity_conflict import capacity_conflict,conflict_question_ok,apply_parameter_policy
from modeling_assistant.graph_units import normalize_graph
from modeling_assistant.graphs import solve_graph
from modeling_assistant.model import ModelClarificationError
from evaluation.clarification import locked_question_score
from evaluation.response_language import conflict_checks

BASE='封闭种群连续Logistic模型，初始1.5个，环境容量恒定0个，增长率0.2每天，模拟0到30天。不得修改参数。'
GOOD_NEGATIONS=[
 '不能取绝对值或改为正数；当前不支持负系数。',
 'K=0无效，保持原值，也不请求修改或替代数值。',
 '不要求提供新的容量，也不会修改参数。',
 '不得修改K，不建议取绝对值。',
 '不会将K改为0.5，原值保持不变。',
 '不请求修改原值；当前模型不支持。',
 '无需修改参数，也不索要替代容量。',
 '按要求不修改参数，当前无法求解。',
 '不需要修改K，原值保持不变。',
 '并非建议修改参数，当前不求解。',
]
BAD_SUGGESTIONS=[
 '不修改K，再取绝对值。',
 '不能取绝对值或建议改为正数。',
 '请提供正实数容量K。',
 '不能不修改容量K。',
 '不得不调整参数。',
 '不是不能修改K。',
 '不请求修改初值，但请提供新的容量。',
 '不建议修改初值，但是可以将K改为0.5。',
 '不会修改K，也建议取绝对值。',
 '不请求修改参数请提供新的容量。',
 '不建议修改K建议取绝对值。',
 '不修改初值；提供一个正实数容量K。',
 '不请求修改参数，是否允许调整K？',
]


class FalseInterceptionTests(unittest.TestCase):
    def test_labeled_negations_runtime_and_independent_evaluator(self):
        for q in GOOD_NEGATIONS:
            with self.subTest(q=q):
                self.assertFalse(has_replacement_suggestion(q))
                self.assertTrue(locked_question_score({'questions':[q]})['passed'])
                env={'status':'unsupported','model':None,'questions':[q]}
                self.assertEqual(apply_parameter_policy(BASE,env),(env,None))

    def test_labeled_suggestions_are_not_released(self):
        for q in BAD_SUGGESTIONS:
            with self.subTest(q=q):
                self.assertTrue(has_replacement_suggestion(q))
                self.assertFalse(locked_question_score({'questions':[q]})['passed'])
                e,a=apply_parameter_policy(BASE,{'status':'unsupported','model':None,'questions':[q]})
                self.assertIsNotNone(a);self.assertFalse(has_replacement_suggestion('；'.join(e['questions'])))

    def evidence(self):
        return capacity_conflict(BASE.replace('恒定0个','恒定-1个')+'另一记录K=-2个。')

    def test_implicit_conflicts_accepted_with_all_values_and_neutral_question(self):
        for q in ['环境容量有两条记录：容量-1个、K=-2个。请核对哪一条准确？',
                  '环境容量K有两条同单位但数值不同的记录：容量恒定-1个、K=-2个。请核对哪一条准确？',
                  '容量-1与-2存在冲突，请核对哪条准确。']:
            e={'status':'needs_clarification','model':None,'questions':[q]}
            self.assertTrue(conflict_question_ok(e,self.evidence()))
            self.assertTrue(all(conflict_checks(q,[-1,-2],'needs_clarification').values()))

    def test_implicit_conflict_false_release_controls(self):
        bad=[
          '容量有两条记录：-1和-2。采用-1，请核对哪条准确？',
          '容量有两条记录：-1和-2。请核对哪条准确，再提供正实数容量。',
          '容量有两条记录：-1。请核对哪条准确？',
          '容量有两条记录：-1与-2。',
          '容量有两条记录：-1与-2，没有冲突。请核对哪条准确？',
          '容量有两条记录：-1与-2，记录一致。请核对哪条准确？',
          '容量有两条记录：-1与-2，以-1为准，请核对哪条准确。',
          '容量有两条记录：-1与-2，取K=-1，请核对哪条准确。',
          '容量有两条记录：-1与-2，按-1计算，请核对哪条准确。',
          '容量有两条记录：-1与-2，我认为-1准确，请核对哪条准确。',
          '容量有两条记录：-1，初值=-2。请核对哪条准确？',
        ]
        for q in bad:
            with self.subTest(q=q):
                e={'status':'needs_clarification','model':None,'questions':[q]}
                self.assertFalse(conflict_question_ok(e,self.evidence()))
                self.assertFalse(all(conflict_checks(q,[-1,-2],'needs_clarification').values()))

    def test_conflict_requires_nonready_and_correct_all_values(self):
        q='容量有两条记录：-1与-2，请核对哪条准确？'
        self.assertFalse(conflict_question_ok({'status':'ready','model':{},'questions':[q]},self.evidence()))
        evidence=copy.deepcopy(self.evidence());evidence['exact_values']=['-1','-2','-3']
        self.assertFalse(conflict_question_ok({'status':'needs_clarification','model':None,'questions':[q]},evidence))

    def test_historical_false_interceptions_now_preserved(self):
        root=Path(__file__).resolve().parents[1];old=root/'outputs/guard_cause_regressions/20261016_222912_c4d79f9a'
        for name,repeat in [('immutable_lock_cannot',1),('remaining_permission_conflict',1),('conflict_two_positive',1),('conflict_all_negative',3)]:
            record=json.loads((old/f'round_{repeat}'/name/'generation_record.json').read_text())
            raw=json.loads(record['generation']['response']['choices'][0]['message']['content'])
            e,a=apply_parameter_policy(record['input'],raw)
            self.assertEqual(e,raw);self.assertIsNone(a)

    def test_integral_unit_conversion_support_and_limits(self):
        for value,unit,target,expected in [(1000,'升/小时','立方米/小时',1),(.001,'立方米/小时','升/小时',1),(1,'升/小时','升/小时',1),(2000,'升/小时','立方米/小时',2)]:
            quote=f'S到T容量{value}{unit}'
            s=dict(task_type='graph_input',name='flow',problem='max_flow',nodes=['S','T'],source='S',target='T',unit=target,assumptions=[],edges=[dict(source='S',target='T',weight=value,unit=unit,source_quote=quote,unit_quote=quote)])
            m,a=normalize_graph(s,quote);self.assertEqual(solve_graph(m)['value'],expected)
        for value,unit,target in [(1,'升/小时','立方米/小时'),(.5,'立方米/小时','立方米/小时'),(1,'桶/小时','立方米/小时')]:
            s['edges'][0].update(weight=value,unit=unit);s['unit']=target
            with self.assertRaises(ModelClarificationError):normalize_graph(s)

    def test_historical_valid_conversion_refusal_not_silently_rewritten(self):
        from unittest.mock import patch
        from modeling_assistant.provider import generate
        old=Path('outputs/guard_cause_regressions/20261016_222912_c4d79f9a/round_3/flow_integer_conversion')
        record=json.loads((old/'generation_record.json').read_text())
        response=record['generation']['response']
        with patch('modeling_assistant.provider.credentials',return_value=('dummy','test')),patch('urllib.request.urlopen') as request:
            request.return_value.__enter__.return_value.read.return_value=json.dumps(response).encode()
            env,meta=generate(record['input'],backend='deepseek')
        self.assertEqual(env,json.loads(response['choices'][0]['message']['content']))
        self.assertEqual(env['status'],'unsupported')
        self.assertNotIn('local_validation',meta)

    def test_targeted_unknown_unit_oracle(self):
        from evaluation.false_interception_regression import unknown_unit_check,cases
        self.assertEqual(len(cases()),22)
        for status,q,expected in [
            ('needs_clarification','请提供桶与立方米的换算系数。',True),
            ('unsupported','桶的体积未知，无法换算。',True),
            ('unsupported','默认一桶等于一立方米。',False),
            ('ready','请提供桶与立方米换算系数。',False),
        ]:
            self.assertEqual(unknown_unit_check({'status':status,'questions':[q]})['passed'],expected)
