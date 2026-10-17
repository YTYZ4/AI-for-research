import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from modeling_assistant.missing_capacity import augment_missing_capacity_question,missing_capacity_evidence
from modeling_assistant.capacity_conflict import apply_parameter_policy
from modeling_assistant.provider import generate
from evaluation.full_regression import classify
from evaluation.capacity_regression import question_score

TEXT='封闭种群连续Logistic模型，初始1.5个，环境容量未知，增长率0.2每天，模拟0到30天，求轨迹和最终数量。'
ENV={'status':'needs_clarification','questions':['请提供环境容量K的值及单位（该参数当前缺失）。'],'model':None}


class MissingCapacityTests(unittest.TestCase):
    def test_omitted_domain_added_with_original_preserved(self):
        before=copy.deepcopy(ENV);e,a=apply_parameter_policy(TEXT,ENV)
        self.assertEqual(ENV,before);self.assertEqual(a['original_envelope'],before)
        self.assertEqual(e['questions'][0],before['questions'][0]);self.assertTrue(question_score(e)['passed'])
        self.assertIsNone(e['model']);self.assertFalse(a['model_executed'])

    def test_missing_wordings(self):
        for phrase in ['容量尚未提供','环境容量未给出','K 未给定','承载能力未知','未说明环境承载量','容量缺失']:
            with self.subTest(phrase=phrase):
                text=TEXT.replace('环境容量未知',phrase)
                self.assertIsNotNone(missing_capacity_evidence(text))
                self.assertTrue(question_score(apply_parameter_policy(text,ENV)[0])['passed'])

    def test_missing_with_permission_and_immutable_values(self):
        for suffix in ['可以修改参数，但请先询问。','不得修改已有参数。','所有已知数值保持原样。']:
            e,a=apply_parameter_policy(TEXT+suffix,ENV)
            self.assertTrue(question_score(e)['passed']);self.assertEqual(a['action'],'augment_missing_capacity_domain')

    def test_preserves_other_missing_questions(self):
        env={**ENV,'questions':['请提供初值和增长率。','请提供环境容量K。']}
        e,a=apply_parameter_policy(TEXT.replace('初始1.5个','初值未知'),env)
        self.assertEqual(e['questions'][:2],env['questions'])
        self.assertTrue(question_score(e)['passed'])

    def test_correct_domain_is_not_local_repair(self):
        for q in ['请提供正实数容量K。','请提供正数容量K，可为小数。','请提供正实数容量K，不要求整数。']:
            env={**ENV,'questions':[q]};self.assertEqual(apply_parameter_policy(TEXT,env),(env,None))

    def test_positive_number_without_fraction_explanation_is_completed(self):
        e,a=apply_parameter_policy(TEXT,{**ENV,'questions':['请提供正数容量K。']})
        self.assertIsNotNone(a);self.assertTrue(question_score(e)['passed'])

    def test_explicit_bad_restrictions_not_masked_by_appending(self):
        for q in ['请提供正整数容量K。','请提供非正容量K。','容量记录冲突，请确认。','K至少1，请提供数值。']:
            env={**ENV,'questions':[q]};e,a=augment_missing_capacity_question(TEXT,env)
            self.assertIsNone(a);self.assertEqual(e,env)

    def test_present_values_expressions_and_later_answers_are_not_missing(self):
        for suffix in ['补充K=0.5个。','容量为5e-1个。','K=N0+1。','K>0。','容量随时间变化。','容量更正为0.5个。']:
            self.assertIsNone(missing_capacity_evidence(TEXT+suffix))
            self.assertIsNone(augment_missing_capacity_question(TEXT+suffix,ENV)[1])

    def test_unsupported_and_non_logistic_not_taken_over(self):
        for text in [TEXT.replace('Logistic','牛顿冷却'),TEXT+'求阈值时间。',TEXT+'参数估计。',TEXT+'时变环境。',TEXT+'两个种群。',TEXT.replace('连续','离散')]:
            self.assertIsNone(augment_missing_capacity_question(text,ENV)[1])
        for status in ['ready','unsupported']:
            env={**ENV,'status':status};self.assertIsNone(augment_missing_capacity_question(TEXT,env)[1])

    def test_conflict_priority_remains_neutral(self):
        text=TEXT+'另一记录K=0个，容量为0.5个。'
        e,a=apply_parameter_policy(text,ENV)
        self.assertIn('冲突',e['questions'][0]);self.assertNotIn('正实数',e['questions'][0])

    def test_dimension_and_domain_corrections_chain_without_loss(self):
        env={**ENV,'questions':['增长率与容量单位需要一致，请提供容量单位。','请提供初始数量。']}
        e,a=apply_parameter_policy(TEXT,env)
        self.assertEqual(a['action'],'augment_missing_capacity_domain');self.assertIn('previous_validation',a)
        self.assertIn('请提供初始数量。',e['questions']);self.assertTrue(question_score(e)['passed'])

    def test_provider_audit_and_layer_classification(self):
        response={'choices':[{'finish_reason':'stop','message':{'content':json.dumps(ENV)}}]}
        with tempfile.TemporaryDirectory() as d,patch('modeling_assistant.provider.credentials',return_value=('dummy','test')),patch('urllib.request.urlopen') as request:
            request.return_value.__enter__.return_value.read.return_value=json.dumps(response).encode()
            env,meta=generate(TEXT,backend='deepseek',audit_path=Path(d)/'api.json')
            self.assertTrue(question_score(env)['passed']);self.assertEqual(meta['response'],response)
            row=classify({'outcome':'pass'},meta)
            self.assertEqual(row['pass_path'],'local_guard');self.assertFalse(row['original_pass']);self.assertFalse(row['after_format_pass'])

    def test_historical_missing_domain_replay(self):
        root=Path(__file__).resolve().parents[1]
        path=root/'outputs/remaining_regressions/20261016_220901_3d78eab4/round_1/permission_missing/generation_record.json'
        record=json.loads(path.read_text());old=record['envelope']
        self.assertFalse(question_score(old)['passed'])
        fixed,a=apply_parameter_policy(record['input'],old)
        self.assertTrue(question_score(fixed)['passed']);self.assertEqual(a['original_envelope'],old)

    def test_full_regression_includes_history_and_domain_checks(self):
        from evaluation.full_regression import cases,apply_question_checks
        items=cases()
        self.assertEqual(len(items),101)
        for id in ['remaining_permission_missing','missing_capacity_multiple','immutable_permission']:
            case=next(c for c in items if c['id']==id)
            self.assertTrue(case['capacity_domain_required'])
            with tempfile.TemporaryDirectory() as d:
                folder=Path(d);(folder/'generation_record.json').write_text(json.dumps({'envelope':ENV}))
                row={'outcome':'pass'};audit=apply_question_checks(case,row,folder)
                self.assertFalse(audit['passed']);self.assertEqual(row['outcome'],'fail')

    def test_multiple_missing_checker_rejects_lost_initial_question(self):
        from evaluation.full_regression import cases,apply_question_checks
        case=next(c for c in cases() if c['id']=='missing_capacity_multiple')
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d);env={**ENV,'questions':['请提供正实数容量K（可为小数）。']}
            (folder/'generation_record.json').write_text(json.dumps({'envelope':env}))
            self.assertFalse(apply_question_checks(case,{'outcome':'pass'},folder)['passed'])
            env['questions'].append('请提供初始数量。')
            (folder/'generation_record.json').write_text(json.dumps({'envelope':env}))
            self.assertTrue(apply_question_checks(case,{'outcome':'pass'},folder)['passed'])
