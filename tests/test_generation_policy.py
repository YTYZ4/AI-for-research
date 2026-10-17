import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from assistant.generation_policy import generation_policy_context
from assistant.capacity_conflict import apply_parameter_policy
from assistant.provider import generate
from evaluation.full import classify

BASE='封闭种群连续Logistic模型，初始1.5个，环境容量恒定0个，增长率0.2每天，模拟0到30天，求轨迹和最终数量。'


class GenerationPolicyTests(unittest.TestCase):
    def test_immutable_invalid_routes_and_quotes(self):
        for phrase in ['不得改动参数。','不要修改任何参数。','全部参数必须保持原样。','保持原值不能调整。','不允许修改参数。','不得替换容量数值。']:
            with self.subTest(phrase=phrase):
                c=generation_policy_context(BASE+phrase)
                self.assertEqual(c['route'],'immutable_invalid');self.assertTrue(c['restriction_quotes'])
                self.assertTrue(all(q in BASE+phrase for q in c['restriction_quotes']))

    def test_conflict_overrides_lock_and_permission(self):
        for values in [(-1,-2),(0,.5),(.5,1.5)]:
            for phrase in ['不得改动参数。','可以修改参数，但请先询问。']:
                text=BASE.replace('恒定0个',f'恒定{values[0]}个')+f'另一记录K={values[1]}个。'+phrase
                self.assertEqual(generation_policy_context(text)['route'],'neutral_conflict')

    def test_equal_invalid_zero_is_not_conflict(self):
        text=BASE.replace('恒定0个','恒定-0个')+'另一记录K=0.0个。不得改动参数。'
        self.assertEqual(generation_policy_context(text)['route'],'immutable_invalid')

    def test_valid_and_permission_controls(self):
        self.assertEqual(generation_policy_context(BASE+'可以修改参数，但请先询问。')['route'],'permission_before_change')
        for value in ['0.5','1.5','2.0']:
            c=generation_policy_context(BASE.replace('恒定0个','恒定'+value+'个')+'不得改动参数。')
            self.assertEqual(c['route'],'valid_parameters')

    def test_missing_is_distinct_from_immutable_value(self):
        self.assertEqual(generation_policy_context(BASE.replace('环境容量恒定0个','环境容量未知')+'不得修改已有参数。')['route'],'missing_capacity')

    def test_ambiguous_and_unsupported_not_forced(self):
        for suffix in ['求阈值时间。','如果允许再修改参数。','两个种群。','容量更正为0.5个。','并非禁止修改参数。','参数估计。']:
            self.assertIsNone(generation_policy_context(BASE+suffix))
        self.assertIsNone(generation_policy_context('有向网络，容量0，不允许改值。'))

    def test_request_context_is_audited_and_native_is_unmodified(self):
        env={'status':'unsupported','model':None,'questions':['K=0使当前Logistic模型无效。原题禁止改动参数，保留原值，停止求解。']}
        response={'choices':[{'finish_reason':'stop','message':{'content':json.dumps(env)}}]}
        with tempfile.TemporaryDirectory() as d,patch('assistant.provider.credentials',return_value=('dummy','test')),patch('urllib.request.urlopen') as request:
            request.return_value.__enter__.return_value.read.return_value=json.dumps(response).encode()
            e,m=generate(BASE+'不得改动参数。',backend='deepseek',audit_path=Path(d)/'api.json')
            self.assertEqual(e,env);self.assertEqual(m['generation_policy_context']['route'],'immutable_invalid')
            self.assertIn('immutable_invalid',m['request']['messages'][1]['content'])
            self.assertNotIn('local_validation',m)
            self.assertTrue(classify({'outcome':'pass'},m)['original_pass'])

    def test_bad_response_still_uses_existing_guard(self):
        env={'status':'needs_clarification','model':None,'questions':['请提供正实数容量K（可为小数）。']}
        e,a=apply_parameter_policy(BASE+'不得改动参数。',env)
        self.assertEqual(e['status'],'unsupported');self.assertIsNotNone(a)
        self.assertEqual(classify({'outcome':'pass'},{'format_repair':{'raw_schema_valid':True},'local_validation':a})['pass_path'],'local_guard')

    def test_conflict_guard_is_not_weakened(self):
        env={'status':'needs_clarification','model':None,'questions':['K=-1和-2冲突，请核对并提供正实数容量。']}
        e,a=apply_parameter_policy(BASE.replace('恒定0个','恒定-1个')+'另一记录K=-2个。不得改动参数。',env)
        self.assertIsNotNone(a);self.assertIn('冲突',e['questions'][0]);self.assertNotIn('正实数',e['questions'][0])

    def test_all_eleven_historical_raw_responses_still_guarded(self):
        from evaluation.guards import cases,flow_refusal_check
        from evaluation.full import apply_question_checks
        root=Path(__file__).resolve().parents[1]
        old=root/'outputs/full_regressions/20261016_221715_01b77856'
        for case in cases():
            if case['group']!='historical_guard':continue
            with self.subTest(case=case['id']),tempfile.TemporaryDirectory() as d,patch('assistant.provider.credentials',return_value=('dummy','test')),patch('urllib.request.urlopen') as request:
                response=json.loads((old/case['id']/'api.json').read_text())['response']
                request.return_value.__enter__.return_value.read.return_value=json.dumps(response).encode()
                env,meta=generate((root/case['problem']).read_text(),backend='deepseek')
                self.assertIn(env['status'],case['expected_envelopes']);self.assertIn('local_validation',meta)
                folder=Path(d);(folder/'generation_record.json').write_text(json.dumps({'envelope':env}))
                self.assertTrue(apply_question_checks(case,{'outcome':'pass'},folder)['passed'])
                if case['id']=='graph_units_fractional_flow':self.assertTrue(flow_refusal_check(env)['passed'])
                self.assertFalse(classify({'outcome':'pass'},meta)['original_pass'])

    def test_flow_refusal_checker_rejects_unit_change_suggestion(self):
        from evaluation.guards import flow_refusal_check
        bad={'status':'unsupported','model':None,'questions':['换算到指定单位后容量不是整数，建议改单位再求解。']}
        good={'status':'unsupported','model':None,'questions':['换算后容量不满足整数限制，不能改单位或取整，当前不支持。']}
        self.assertFalse(flow_refusal_check(bad)['passed']);self.assertTrue(flow_refusal_check(good)['passed'])
