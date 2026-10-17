import json
import unittest
from pathlib import Path
from modeling_assistant.graph_routing import graph_route_evidence
from modeling_assistant.request_contract import request_contract
from modeling_assistant.provider import INSTRUCTIONS

class GraphRoutingTests(unittest.TestCase):
    def test_structural_goal_synonyms(self):
        for text in ['有向网络，先让流量最大，再让运输总成本最小。',
                     '节点S、T，最大化输送量，同时使运费最低。',
                     '管网中吞吐量尽可能大，开销尽可能低。',
                     '道路网络中寻找距离最短的路线。']:
            e=graph_route_evidence(text)
            self.assertTrue(e['selected'],text)
            for key in ['structure','objectives']:
                self.assertTrue(e[key])
                for span in e[key]:self.assertEqual(text[span['start']:span['end']],span['quote'])

    def test_goal_or_structure_alone_is_not_enough(self):
        for text in ['让运输总成本最小。','节点S和T的温度是多少？','流量最大、费用最低。','神经网络拟合流量曲线。','生产运输成本最低。']:
            self.assertFalse(graph_route_evidence(text)['selected'],text)

    def test_mixed_keeps_full_schema(self):
        for text in ['有向网络中流量最大，同时拟合容量曲线。',
                     '求最大流，再联合优化生产计划。',
                     '用Logistic预测需求并求成本最低的管网流量。',
                     '拟合最大流的观测结果。']:
            _,schema,meta=request_contract(text,INSTRUCTIONS)
            self.assertEqual(meta['route'],'general')
            self.assertGreater(len(schema['properties']['model']['anyOf']),2)
            self.assertEqual(meta['routing_evidence']['reason'],'other_family_present')

    def test_routing_does_not_decide_negated_objective_or_status(self):
        text='有向网络S到T容量1升/小时，不要求费用最低，只求流量最大。'
        _,schema,meta=request_contract(text,INSTRUCTIONS)
        self.assertEqual(meta['route'],'graph_source_only')
        self.assertEqual(schema['properties']['status']['enum'],['ready','needs_clarification','unsupported'])
        self.assertNotIn('response_rule',meta['routing_evidence'])

    def test_historical_cost_paraphrase_now_routes_to_source_contract(self):
        text=Path('examples/refusal_boundaries/cost_paraphrase.txt').read_text()
        _,_,meta=request_contract(text,INSTRUCTIONS)
        self.assertEqual(meta['route'],'graph_source_only')
        self.assertEqual(meta['routing_evidence']['reason'],'graph_structure_and_goal')
