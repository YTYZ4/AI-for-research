import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from assistant.graph_quotes import repair_graph_quotes,extract_global_edges
from assistant.graph_units import normalize_graph
from assistant.capacity_conflict import apply_parameter_policy
from assistant.parameter_policy import permission_to_ask
from assistant.provider import generate
from evaluation.full import classify,check_quote_repair

ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/'outputs/full_regressions/20261016_215628_fad2b50a'
TEXT='封闭种群连续Logistic模型，初始1.5个，环境容量恒定0个，增长率0.2每天，模拟0到30天，求轨迹和最终数量。'
PERMISSION='可以修改参数，但请先询问，不要自行替换数值。'
REJECT={'status':'unsupported','questions':['K=0不能求解。'],'model':None}


def graph_fixture():
    text='单向管道只有：B→T上限9，A→T上限6，A→B上限4，S→B上限5，S→A上限10，单位均为立方米/小时。'
    pairs=[('B','T',9),('A','T',6),('A','B',4),('S','B',5),('S','A',10)]
    model=dict(task_type='graph_input',name='flow',problem='max_flow',nodes=['S','A','B','T'],source='S',target='T',unit='立方米/小时',assumptions=[],edges=[dict(source=u,target=v,weight=w,unit='立方米/小时',source_quote=f'{u}→{v}上限{w}，单位均为立方米/小时',unit_quote='单位均为立方米/小时') for u,v,w in pairs])
    return text,model


class RemainingFailureTests(unittest.TestCase):
    def test_graph_repair_only_quotes(self):
        text,source=graph_fixture();before=copy.deepcopy(source)
        fixed,a=repair_graph_quotes(source,text)
        self.assertEqual(source,before);self.assertIsNotNone(a)
        m,c=normalize_graph(fixed,text);self.assertTrue(c['source_quotes_checked'])
        self.assertEqual([e['weight'] for e in m['edges']],[9,6,4,5,10])
        self.assertEqual(fixed['edges'][0]['source_quote'],'B→T上限9')
        self.assertIsNone(repair_graph_quotes(fixed,text)[1])

    def test_graph_refuses_math_or_unit_changes(self):
        for field,value in [('weight',90),('unit','升/小时'),('source','S')]:
            text,s=graph_fixture();s['edges'][0][field]=value
            self.assertIsNone(repair_graph_quotes(s,text)[1])

    def test_graph_refuses_missing_extra_duplicate_edges(self):
        for kind in ['missing','extra','duplicate']:
            text,s=graph_fixture()
            if kind=='missing':s['edges'].pop()
            elif kind=='extra':s['edges'].append(dict(s['edges'][0],source='T',target='S'))
            else:s['edges'][0]=copy.deepcopy(s['edges'][1])
            self.assertIsNone(repair_graph_quotes(s,text)[1])

    def test_graph_ambiguous_scope_not_repaired(self):
        text,s=graph_fixture()
        for modified in [text+'另一个网络。',text+'单位为升/小时。',text.replace('单向','双向'),text.replace('上限9','上限9升/小时'),text+'更正S到A为11。',text.replace('单位均为','S到A的单位为')]:
            self.assertIsNone(repair_graph_quotes(s,modified)[1])

    def test_global_unit_wording(self):
        text,s=graph_fixture()
        for declaration in ['单位均为','单位都为','单位统一为','单位为']:
            t=text.replace('单位均为',declaration);fixed,a=repair_graph_quotes(s,t)
            self.assertIsNotNone(a);normalize_graph(fixed,t)

    def test_permission_reject_becomes_question(self):
        result,a=apply_parameter_policy(TEXT+PERMISSION,REJECT)
        self.assertEqual(result['status'],'needs_clarification');self.assertIsNone(result['model'])
        self.assertEqual(a['original_envelope'],REJECT);self.assertIn('正实数',result['questions'][0])
        self.assertFalse(classify({'outcome':'pass'},{'format_repair':{'raw_schema_valid':True},'local_validation':a})['original_pass'])

    def test_permission_paraphrases(self):
        for phrase in [PERMISSION,'允许调整容量，但需先征求我的同意。','可以更改K，但请先问我。']:
            self.assertTrue(permission_to_ask(phrase))
            self.assertEqual(apply_parameter_policy(TEXT+phrase,REJECT)[0]['status'],'needs_clarification')

    def test_permission_negative_and_scoped_controls(self):
        for phrase in ['不允许修改参数，请先询问。','如果可以修改参数，请先询问。','可以修改增长率，但请先询问。','可以修改参数，但容量不得改动，先询问。','可以修改参数。','并非允许修改参数，请先询问。','可以修改参数，不必先询问。','可以修改参数，无需先确认。']:
            self.assertFalse(permission_to_ask(phrase))

    def test_valid_missing_or_unsupported_inputs_not_taken_over(self):
        for text in [TEXT.replace('恒定0个','恒定0.5个'),TEXT.replace('环境容量恒定0个，',''),TEXT.replace('求轨迹和最终数量','求到达阈值时间'),TEXT.replace('初始1.5个','初始-1个')]:
            self.assertIsNone(apply_parameter_policy(text+PERMISSION,REJECT)[1])

    def test_conflict_precedes_permission(self):
        e,a=apply_parameter_policy(TEXT+'另记录K=0.5个。'+PERMISSION,REJECT)
        self.assertIn('冲突',e['questions'][0]);self.assertNotIn('正实数',e['questions'][0])

    def test_correct_question_not_counted_as_guard(self):
        e={'status':'needs_clarification','model':None,'questions':['K=0无效，请确认并提供正实数环境容量K（可为小数）。']}
        self.assertEqual(apply_parameter_policy(TEXT+PERMISSION,e),(e,None))

    def test_historical_graph_response_replay_and_audit(self):
        text=(ROOT/'examples/development_variants/NET02_paraphrase.txt').read_text()
        meta=json.loads((OLD/'NET02_paraphrase/api.json').read_text());response=meta['response']
        with tempfile.TemporaryDirectory() as d,patch('assistant.provider.credentials',return_value=('dummy','test')),patch('urllib.request.urlopen') as request:
            request.return_value.__enter__.return_value.read.return_value=json.dumps(response).encode()
            e,metadata=generate(text,backend='deepseek')
            self.assertEqual(e['status'],'ready');self.assertEqual(classify({'outcome':'pass'},metadata)['pass_path'],'local_source_repair')
            case={'problem':'examples/development_variants/NET02_paraphrase.txt'}
            self.assertTrue(check_quote_repair(case,metadata,Path(d))['passed'])
            metadata['source_model']['edges'][0]['weight']=90
            self.assertFalse(check_quote_repair(case,metadata,Path(d))['passed'])

    def test_historical_permission_replay(self):
        text=(ROOT/'examples/immutable/permission.txt').read_text()
        old=json.loads((OLD/'immutable_permission/generation_record.json').read_text())['envelope']
        e,a=apply_parameter_policy(text,old)
        self.assertEqual(e['status'],'needs_clarification');self.assertEqual(a['original_envelope'],old)

    def test_quote_audit_rejects_fake_change_list(self):
        from evaluation.graph_units import graph_quote_audit
        text,s=graph_fixture();fixed,a=repair_graph_quotes(s,text)
        meta={'source_quote_repair':a,'source_model':fixed,'response':{'choices':[{'message':{'content':json.dumps({'model':s})}}]}}
        self.assertTrue(graph_quote_audit(meta,text)['passed'])
        a['changes']=[]
        self.assertFalse(graph_quote_audit(meta,text)['passed'])

    def test_targeted_evaluator_rejects_wrong_permission_status(self):
        from evaluation.remaining import check_response
        with tempfile.TemporaryDirectory() as d:
            case={'check':'permission','expected_envelopes':['needs_clarification']}
            self.assertFalse(check_response(case,REJECT,Path(d))['passed'])
            good={'status':'needs_clarification','questions':['请确认并提供正实数容量K，可为小数。'],'model':None}
            self.assertTrue(check_response(case,good,Path(d))['passed'])
