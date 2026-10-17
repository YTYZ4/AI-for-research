import unittest
from pathlib import Path
from modeling_assistant.graph_completeness import single_edge_evidence
from evaluation.graph_explanations import explanation_extras
from evaluation.refusal_semantics import refusal_score

BASE='有向网络只有S到T容量0.001立方米/小时，节点S、T，无其他边。求最大流，以升/小时表示。'
def env(q):return dict(status='unsupported',model=None,questions=[q])

class SingleEdgeAndRefusalTests(unittest.TestCase):
    def test_exact_source_evidence(self):
        e=single_edge_evidence(BASE)
        self.assertEqual(e['raw_value'],'0.001')
        for k in ['edge_quote','nodes_quote','closure_quote']:self.assertIn(e[k],BASE)

    def test_missing_ambiguous_or_extra_edges_do_not_claim_complete(self):
        for text in [BASE.replace('无其他边',''),BASE.replace('0.001','未知'),
                     BASE.replace('节点S、T','节点S、A'),BASE.replace('有向','无向'),
                     BASE+'另一记录S到T容量2升/小时。',BASE+'如果容量改变需重算。',
                     BASE.replace('S到T','S到S'),BASE+'方向未知。']:
            self.assertIsNone(single_edge_evidence(text),text)

    def test_evidence_does_not_certify_numeric_domain(self):
        for value in ['0','-1','0.0001']:
            e=single_edge_evidence(BASE.replace('0.001',value))
            self.assertIsNotNone(e)
            self.assertNotIn('supported',e)

    def test_conditional_capability_description_is_not_change_request(self):
        q='不支持最小费用流。支持边界：若仅求单商品最大流，可处理固定容量有向图；若仅求最短路径，可处理边权图。'
        self.assertTrue(explanation_extras(env(q))['passed'])
        for q in ['若仅求最大流，请删除费用目标。','若仅求最大流，建议改为普通最大流。']:
            self.assertFalse(explanation_extras(env(q))['passed'])

    def test_split_requests_and_negated_controls(self):
        for q in ['请拆分为两个问题。','建议分别提交。','请分开提交。','请一次只提交其中一项。','不能删除目标，但请拆分任务。']:
            self.assertFalse(explanation_extras(env(q))['passed'],q)
        for q in ['不建议拆分任务，只说明不能联合求解。','不会要求分别提交。']:
            self.assertTrue(explanation_extras(env(q))['passed'],q)

    def test_joint_limit_equivalence_and_false_release(self):
        for q in ['当前单模型协议不能联合表示并求解Logistic及最大流。','当前协议无法联合表示Logistic与图任务。']:
            self.assertTrue(refusal_score(env(q),'Logistic|联合')['passed'])
        for q in ['当前可以联合表示Logistic及图任务。','Logistic和最大流两个任务。']:
            self.assertFalse(refusal_score(env(q),'Logistic|联合')['passed'])

    def test_refusal_remains_unchanged_despite_completeness_evidence(self):
        import json
        from unittest.mock import patch
        from modeling_assistant.provider import generate
        response_env=dict(status='needs_clarification',model=None,questions=['请确认是否只有一条边？'])
        response={'choices':[{'finish_reason':'stop','message':{'content':json.dumps(response_env)}}]}
        with patch('modeling_assistant.provider.credentials',return_value=('dummy','test')),patch('urllib.request.urlopen') as request:
            request.return_value.__enter__.return_value.read.return_value=json.dumps(response).encode()
            result,meta=generate(BASE,backend='deepseek')
        self.assertEqual(result,response_env)
        self.assertIn('graph_completeness_evidence',meta)
        self.assertNotIn('local_validation',meta)
        self.assertIn('本地原文图完整性证据',meta['request']['messages'][1]['content'])

    def test_historical_scoring_errors_and_split_suggestions(self):
        import json
        root=Path('outputs/routing_regressions/20261016_235822_63be8542')
        for name,repeat in [('flow_cost_priority',3),('mixed_logistic',3)]:
            a=json.loads((root/f'round_{repeat}'/name/'api.json').read_text())
            raw=json.loads(a['response']['choices'][0]['message']['content'])
            self.assertTrue(explanation_extras(raw)['passed'])
            self.assertTrue(refusal_score(raw,'费用|联合|Logistic')['passed'])
        a=json.loads((root/'round_1/mixed_production/api.json').read_text())
        raw=json.loads(a['response']['choices'][0]['message']['content'])
        self.assertFalse(explanation_extras(raw)['passed'])
