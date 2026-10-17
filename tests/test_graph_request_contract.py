import copy
import json
import unittest
from pathlib import Path
from unittest.mock import patch
from jsonschema import Draft202012Validator
from assistant.request_contract import request_contract
from assistant.provider import generate,INSTRUCTIONS
from assistant.model import ENVELOPE_SCHEMA
from evaluation.full import classify

class GraphRequestContractTests(unittest.TestCase):
    def call(self,text,env):
        response={'choices':[{'finish_reason':'stop','message':{'content':json.dumps(env)}}]}
        with patch('assistant.provider.credentials',return_value=('dummy','test')),patch('urllib.request.urlopen') as req:
            req.return_value.__enter__.return_value.read.return_value=json.dumps(response).encode()
            return generate(text,backend='deepseek')

    def fixture(self,value=1000,unit='升/小时',target='立方米/小时'):
        quote=f'S到T容量{value}{unit}'
        text=f'有向网络只有{quote}，节点S、T，无其他边。输出{target}。求最大流。'
        env={'status':'ready','questions':[],'model':dict(task_type='graph_input',name='flow',problem='max_flow',nodes=['S','T'],source='S',target='T',unit=target,assumptions=[],edges=[dict(source='S',target='T',weight=value,unit=unit,source_quote=quote,unit_quote=quote)])}
        return text,env

    def test_only_source_schema_sent_and_general_not_mutated(self):
        before=copy.deepcopy(ENVELOPE_SCHEMA)
        text,env=self.fixture()
        prompt,schema,meta=request_contract(text,INSTRUCTIONS)
        self.assertEqual(meta['route'],'graph_source_only')
        self.assertEqual(len(schema['properties']['model']['anyOf']),2)
        self.assertNotIn('Logistic',prompt)
        self.assertTrue(Draft202012Validator(schema).is_valid(env))
        old=copy.deepcopy(env);old['model']['task_type']='graph'
        self.assertFalse(Draft202012Validator(schema).is_valid(old))
        self.assertEqual(before,ENVELOPE_SCHEMA)

    def test_mixed_and_nongraph_fallback(self):
        for text in ['Logistic增长','拟合最大流与温度关系','生产计划和最短路径联合求解','请优化运输分配']:
            self.assertEqual(request_contract(text,INSTRUCTIONS)[2]['route'],'general')

    def test_valid_conversions_preserve_source_and_native_class(self):
        for value,unit,target,w in [(1000,'升/小时','立方米/小时',1),(.001,'立方米/小时','升/小时',1),(1,'升/小时','升/小时',1),(60,'升/分钟','升/秒',1),(0,'升/小时','立方米/小时',0)]:
            text,env=self.fixture(value,unit,target);result,meta=self.call(text,env)
            self.assertEqual(result['model']['edges'][0]['weight'],w)
            self.assertEqual(meta['source_model'],env['model'])
            self.assertEqual(meta['request_contract']['route'],'graph_source_only')
            self.assertTrue(classify({'outcome':'pass'},meta)['original_pass'])

    def test_nonintegral_unknown_and_incompatible_still_guarded(self):
        for value,unit,target in [(1,'升/小时','立方米/小时'),(.5,'升/小时','升/小时'),(1,'桶/小时','立方米/小时'),(1,'米','升/小时')]:
            text,env=self.fixture(value,unit,target);result,meta=self.call(text,env)
            self.assertNotEqual(result['status'],'ready')
            self.assertIn('local_validation',meta)
            self.assertFalse(classify({'outcome':'pass'},meta)['original_pass'])

    def test_corrupt_quotes_cannot_execute(self):
        text,env=self.fixture()
        for field,value in [('source_quote','S到T容量2000升/小时'),('unit','立方米/小时')]:
            bad=copy.deepcopy(env);bad['model']['edges'][0][field]=value
            result,meta=self.call(text,bad)
            self.assertNotEqual(result['status'],'ready')

    def test_refusals_are_preserved_not_promoted(self):
        old=Path('outputs/false_interception_followups/20261016_224619_c2a067a7')
        for repeat,name in [(1,'flow_integer_conversion'),(1,'flow_reverse_conversion'),(2,'flow_reverse_conversion'),(3,'flow_reverse_conversion')]:
            rec=json.loads((old/f'round_{repeat}'/name/'generation_record.json').read_text())
            env=json.loads(rec['generation']['response']['choices'][0]['message']['content'])
            result,meta=self.call(rec['input'],env)
            self.assertEqual(result,env);self.assertNotIn('local_validation',meta)

    def test_invalid_numeric_and_parallel_edges_do_not_reach_ready(self):
        for variant in ['negative','parallel','overflow']:
            text,env=self.fixture()
            if variant=='negative':env['model']['edges'][0]['weight']=-1
            elif variant=='parallel':env['model']['edges']*=2
            else:env['model']['edges'][0]['weight']=1e15
            try:
                result,meta=self.call(text,env)
            except ValueError:
                continue
            self.assertNotEqual(result['status'],'ready')

    def test_missing_and_out_of_scope_answers_stay_nonready(self):
        for text,status in [('有向网络S到T容量未知，求最大流','needs_clarification'),
                            ('求最小费用最大流','unsupported')]:
            env={'status':status,'questions':['缺容量或超出支持范围，未求解。'],'model':None}
            result,meta=self.call(text,env)
            self.assertEqual(result,env)
