import copy
import json
import unittest
from pathlib import Path
from unittest.mock import patch
from jsonschema import Draft202012Validator
from modeling_assistant.request_contract import request_contract
from modeling_assistant.provider import generate,INSTRUCTIONS
from modeling_assistant.model import validate_envelope
from modeling_assistant.format_repair import validate_with_repair

class RefusalContractTests(unittest.TestCase):
    def envelope(self,status='unsupported',questions=None):
        return dict(status=status,questions=['请求最小费用流，当前只支持最短路径和普通最大流。'] if questions is None else questions,model=None)

    def test_schema_disallows_empty_and_inconsistent_states(self):
        _,schema,_=request_contract('求最小费用最大流',INSTRUCTIONS)
        check=Draft202012Validator(schema)
        for status in ['unsupported','needs_clarification']:
            for qs in [[],[''],[' \n\t'],['说明',' ']]:
                self.assertFalse(check.is_valid(self.envelope(status,qs)),(status,qs))
        self.assertTrue(check.is_valid(self.envelope()))
        self.assertTrue(check.is_valid(self.envelope('needs_clarification',['请提供边的方向。'])))
        self.assertFalse(check.is_valid(self.envelope('ready',[])))

    def test_local_validation_rejects_blanks_without_fabricating_text(self):
        for status in ['unsupported','needs_clarification']:
            for qs in [[],[''],[' \n\t'],['合法说明',' ']]:
                env=self.envelope(status,qs);before=copy.deepcopy(env);audit={}
                with self.assertRaises(ValueError):validate_with_repair(env,audit)
                self.assertEqual(env,before)
                self.assertNotEqual(audit['action'],'applied')

    def test_three_historical_empty_refusals_still_fail(self):
        old=Path('outputs/graph_contract_regressions/20261016_225320_e4401c39')
        for n in range(1,4):
            api=json.loads((old/f'round_{n}/flow_min_cost/api.json').read_text())
            env=json.loads(api['response']['choices'][0]['message']['content'])
            with self.assertRaises(ValueError):validate_envelope(env)
            self.assertEqual(env,self.envelope(questions=[]))

    def test_valid_nonready_not_promoted_and_actual_prompt_is_consistent(self):
        env=self.envelope()
        response={'choices':[{'finish_reason':'stop','message':{'content':json.dumps(env)}}]}
        with patch('modeling_assistant.provider.credentials',return_value=('dummy','test')),patch('urllib.request.urlopen') as req:
            req.return_value.__enter__.return_value.read.return_value=json.dumps(response).encode()
            result,meta=generate('有向网络，求最小费用最大流。',backend='deepseek')
        self.assertEqual(result,env)
        self.assertNotIn('local_validation',meta)
        prompt=meta['request']['messages'][0]['content']
        self.assertNotIn('完整问题必须返回 ready',prompt)
        self.assertNotIn('该资源是否有供应上限',prompt)
        self.assertTrue(meta['request_contract']['state_constraints'])

    def test_strict_api_schema_keeps_compatible_shape(self):
        _,schema,meta=request_contract('求最小费用流',INSTRUCTIONS,'openai')
        self.assertEqual(meta['route'],'graph_source_only')
        self.assertNotIn('anyOf',schema)
        self.assertFalse(meta['state_constraints'])

    def test_independent_refusal_semantics_false_release_controls(self):
        from evaluation.refusal_semantics import refusal_score
        topic=r'最小费用|费用最小|最小成本|成本最小'
        for q in ['当前只支持最短路径和普通最大流，不支持最小费用流。',
                  '最小费用流超出支持范围，不能忽略费用后直接求解。']:
            self.assertTrue(refusal_score(self.envelope(questions=[q]),topic)['passed'])
        for env in [
            self.envelope(questions=[]),self.envelope(questions=[' ']),
            self.envelope(questions=['不支持。']),
            self.envelope(questions=['最小费用流。']),
            self.envelope(questions=['最小费用流无法输出，因为JSON不支持引用字段。']),
            self.envelope(questions=['不支持最小费用流，建议忽略费用。']),
            self.envelope(status='ready'),
        ]:
            self.assertFalse(refusal_score(env,topic)['passed'],env)
