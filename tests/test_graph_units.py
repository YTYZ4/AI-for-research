import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from assistant.graph_units import normalize_graph
from assistant.graphs import solve_graph
from assistant.model import validate_model, ModelClarificationError
from assistant.provider import generate
from evaluation.full import classify


def source(weight=4000, unit='米', target='km'):
    quote=f'S到T {weight}{unit}'
    return dict(task_type='graph_input', name='test', problem='shortest_path', nodes=['S','T'],
                source='S', target='T', unit=target, assumptions=[],
                edges=[dict(source='S', target='T', weight=weight, unit=unit, source_quote=quote, unit_quote=quote)])


class GraphUnitTests(unittest.TestCase):
    def test_mixed_path_retains_source(self):
        s=source();s['nodes']=['S','A','T'];s['edges'][0].update(target='A',source_quote='S到A 4000米',unit_quote='S到A 4000米')
        s['edges'].append(dict(source='A',target='T',weight=2,unit='千米',source_quote='A到T 2千米',unit_quote='A到T 2千米'))
        before=copy.deepcopy(s);m,a=normalize_graph(s,'S到A 4000米，A到T 2千米')
        self.assertEqual(s,before);self.assertEqual(solve_graph(m)['value'],6)
        self.assertEqual(a['edges'][0]['factor'],'1/1000')

    def test_reverse_decimal_and_scientific(self):
        for value,unit,target,expected in [(0.5,'km','m',500),(5e-1,'米','cm',50),(250,'毫米','m',.25),(0,'cm','km',0)]:
            with self.subTest(unit=unit):self.assertEqual(normalize_graph(source(value,unit,target))[0]['edges'][0]['weight'],expected)
        s=source(.5);s['edges'][0].update(source_quote='S到T 5e-1米',unit_quote='S到T 5e-1米')
        self.assertEqual(normalize_graph(s,'S到T 5e-1米')[0]['edges'][0]['weight'],.0005)

    def test_unknown_same_unit_passes_but_mixed_rejected(self):
        self.assertEqual(normalize_graph(source(3,'元','元'))[0]['edges'][0]['weight'],3)
        for unit,target in [('英里','km'),('米','小时'),('米','m3/hour'),('','km')]:
            with self.subTest(unit=unit),self.assertRaises(ModelClarificationError):normalize_graph(source(3,unit,target))

    def test_value_unit_quote_and_endpoint_tampering(self):
        for field,value in [('weight',4),('unit','千米'),('source_quote','S到T 4千米'),('source','A')]:
            s=source();s['edges'][0][field]=value
            with self.subTest(field=field),self.assertRaises((ValueError,ModelClarificationError)):normalize_graph(s,'S到T 4000米')

    def test_unit_substrings_do_not_match(self):
        for actual,wrong in [('千米','米'),('km','m'),('毫米','米'),('mm','m'),('m/s','m')]:
            s=source(4,wrong,wrong);s['edges'][0].update(source_quote=f'S到T 4{actual}',unit_quote=f'S到T 4{actual}')
            with self.subTest(actual=actual),self.assertRaises(ModelClarificationError):normalize_graph(s,f'S到T 4{actual}')

    def test_global_unit_quote(self):
        s=source(10,'立方米/小时','m3/hour');s['problem']='max_flow'
        s['edges'][0].update(source_quote='S到T容量10',unit_quote='容量单位统一为立方米/小时')
        m,_=normalize_graph(s,'容量单位统一为立方米/小时：S到T容量10。')
        self.assertEqual(solve_graph(m)['value'],10)

    def test_flow_conversion_exact_and_fractional_rejected(self):
        for value,unit,target,expected in [(1000,'升/小时','立方米/小时',1),(1,'立方米/秒','升/小时',3600000),(60,'升/分钟','升/秒',1)]:
            s=source(value,unit,target);s['problem']='max_flow'
            self.assertEqual(solve_graph(normalize_graph(s)[0])['value'],expected)
        s=source(1,'升/小时','立方米/小时');s['problem']='max_flow'
        with self.assertRaises(ModelClarificationError):normalize_graph(s)

    def test_invalid_and_large_weights(self):
        for value in [-1,float('nan'),float('inf'),True]:
            with self.subTest(value=value),self.assertRaises(ValueError):validate_model(source(value))
        with self.assertRaises(ModelClarificationError):normalize_graph(source(1e9,'km','m'))
        self.assertEqual(normalize_graph(source(1e9,'m','m'))[0]['edges'][0]['weight'],1e9)

    def test_empty_disconnected_and_duplicate_edges(self):
        s=source();s['edges']=[]
        self.assertEqual(solve_graph(normalize_graph(s)[0])['status'],'unreachable')
        s['problem']='max_flow';self.assertEqual(solve_graph(normalize_graph(s)[0])['value'],0)
        s=source();s['edges']*=2
        with self.assertRaises(ValueError):normalize_graph(s)

    def test_online_conversion_and_layer_counts(self):
        for redundant in [False,True]:
            env=dict(status='ready',questions=[],model=source())
            if redundant:env['model_type']='graph_input'
            response={'choices':[{'finish_reason':'stop','message':{'content':json.dumps(env)}}]}
            with tempfile.TemporaryDirectory() as d,patch('assistant.provider.credentials',return_value=('dummy','test')),patch('urllib.request.urlopen') as request:
                request.return_value.__enter__.return_value.read.return_value=json.dumps(response).encode()
                result,meta=generate('S到T 4000米',backend='deepseek',audit_path=Path(d)/'api.json')
                self.assertEqual(result['model']['edges'][0]['weight'],4)
                self.assertEqual(meta['source_model'],env['model'])
                layer=classify({'outcome':'pass'},meta)
                self.assertEqual(layer['original_pass'],not redundant)
                self.assertTrue(layer['after_format_pass'])
                self.assertNotIn('local_validation',meta)

    def test_online_old_graph_cannot_bypass_provenance(self):
        old=normalize_graph(source())[0];response={'choices':[{'finish_reason':'stop','message':{'content':json.dumps(dict(status='ready',questions=[],model=old))}}]}
        with patch('assistant.provider.credentials',return_value=('dummy','test')),patch('urllib.request.urlopen') as request:
            request.return_value.__enter__.return_value.read.return_value=json.dumps(response).encode()
            env,meta=generate('S到T 4000米',backend='deepseek')
            self.assertEqual(env['status'],'needs_clarification');self.assertIn('local_validation',meta)

    def test_independent_oracle_catches_tampering(self):
        from evaluation.graph_units import provenance_checks
        s=source();m,a=normalize_graph(s,'S到T 4000米')
        record={'input':'S到T 4000米','envelope':{'model':m},'generation':{'source_model':s,'unit_conversion':a,'response':{'choices':[{'message':{'content':json.dumps({'model':s})}}]}}}
        self.assertTrue(all(provenance_checks(record).values()))
        record['generation']['unit_conversion']['edges'][0]['factor']='1'
        self.assertFalse(provenance_checks(record)['audit_matches'])
