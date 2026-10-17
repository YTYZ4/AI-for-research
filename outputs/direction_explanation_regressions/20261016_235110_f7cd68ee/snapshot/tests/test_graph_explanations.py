import json
import unittest
from pathlib import Path
from evaluation.graph_explanations import direction_score,explanation_extras

def env(q,status='needs_clarification',model=None):
    return dict(status=status,questions=[q],model=model)

class GraphExplanationTests(unittest.TestCase):
    def test_direction_synonyms(self):
        for q in ['需要明确S与T之间从哪个节点指向哪个节点。','请确认这条边是S到T、T到S还是双向？','请提供边的流向。','边是单向还是双向？','请确认方向。']:
            self.assertTrue(direction_score(env(q))['passed'],q)

    def test_false_release_direction(self):
        for e in [env('方向未知。'),env('请提供容量。'),env('请确认方向。','unsupported'),
                  env('请确认方向，默认S到T。'),env('请确认方向，假设双向。'),
                  env('方向已明确，无需确认。'),env('请确认方向。',model={}),
                  env('请确认方向，暂按S到T求解。')]:
            self.assertFalse(direction_score(e)['passed'],e)

    def test_historical_direction_labels(self):
        old=Path('outputs/refusal_contract_regressions/20261016_225944_e764b376')
        for n,expected in [(1,True),(2,False),(3,True)]:
            a=json.loads((old/f'round_{n}/flow_missing_direction/api.json').read_text())
            raw=json.loads(a['response']['choices'][0]['message']['content'])
            self.assertEqual(direction_score(raw)['passed'],expected)

    def test_explanation_suggestions_and_denials(self):
        for q in ['不支持最小费用流，若只要求最大流，请去掉费用要求。',
                  '请改为静态最大流。','建议忽略成本。','不能改为普通最大流，但请移除费用目标。',
                  '若需要支持的任务，可改为仅求最大流。']:
            self.assertFalse(explanation_extras(env(q))['passed'],q)
        for q in ['不支持最小费用流，仅支持普通最大流。','不能忽略费用后直接求解。',
                  '不会修改任务，当前不支持多商品流。']:
            self.assertTrue(explanation_extras(env(q))['passed'],q)

    def test_false_missing_claims_use_fixed_case_evidence(self):
        q='多商品流超出支持范围，未提供具体节点、边、容量和商品需求。'
        self.assertFalse(explanation_extras(env(q),['节点','容量'])['passed'])
        self.assertTrue(explanation_extras(env('不支持多商品流；已提供节点和容量。'),['节点','容量'])['passed'])
        # A genuinely unspecified demand is not treated as supplied evidence.
        self.assertTrue(explanation_extras(env('未提供商品需求。'),['节点','容量'])['passed'])

    def test_historical_extra_assertion_detected(self):
        p=Path('outputs/refusal_contract_regressions/20261016_225944_e764b376/round_3/multi_commodity/api.json')
        raw=json.loads(json.loads(p.read_text())['response']['choices'][0]['message']['content'])
        self.assertFalse(explanation_extras(raw,['节点','容量'])['passed'])
