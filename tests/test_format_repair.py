import copy
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from assistant.format_repair import validate_with_repair
from assistant.provider import generate,parse_deepseek_response
from assistant.model import ModelClarificationError
ROOT=Path(__file__).resolve().parents[1]
HIST=ROOT/'outputs/unit_regressions/20261016_201428_3b74d7fb/round_3/cooling_units/api.json'

class FormatRepairTests(unittest.TestCase):
    def envelope(self):
        model=json.loads((ROOT/'examples/dynamics/logistic_model.json').read_text())
        return dict(status='ready',questions=[],model=model,model_type='dynamics')

    def test_duplicate_only_preserves_input_and_math(self):
        e=self.envelope();before=copy.deepcopy(e);audit={};fixed=validate_with_repair(e,audit)
        self.assertEqual(e,before);self.assertEqual(fixed['model'],before['model'])
        self.assertNotIn('model_type',fixed);self.assertEqual(audit['changes'],[dict(operation='remove',path='/model_type',old_value='dynamics')])
        self.assertNotEqual(audit['original_sha256'],audit['repaired_sha256'])

    def test_unknown_or_conflicting_fields_not_discarded(self):
        for scenario in ('conflict','unknown_top','unknown_model','missing','type'):
            e=self.envelope()
            if scenario=='conflict':e['model_type']='graph'
            if scenario=='unknown_top':e['new_constraint']='K>=2000'
            if scenario=='unknown_model':e['model']['extra_rate']=10
            if scenario=='missing':del e['model']['rate']
            if scenario=='type':e['model']['rate']='.2'
            a={}
            with self.assertRaises(ValueError):validate_with_repair(e,a)
            self.assertEqual(a['action'],'rejected')

    def test_format_repair_does_not_fix_invalid_parameters(self):
        e=self.envelope();e['model']['equilibrium']=0;a={}
        with self.assertRaises(ModelClarificationError):validate_with_repair(e,a)
        self.assertFalse(a['semantic_validation_passed'])
        self.assertEqual(a['repaired_envelope']['model']['equilibrium'],0)

    def test_truncated_response_never_repaired(self):
        response={'choices':[{'finish_reason':'length','message':{'content':json.dumps(self.envelope())}}]}
        a={}
        with self.assertRaises(ValueError):parse_deepseek_response(response,a)
        self.assertEqual(a,{})

    def test_audit_preserved_on_rejected_response(self):
        e=self.envelope();e['model_type']='graph'
        response={'choices':[{'finish_reason':'stop','message':{'content':json.dumps(e)}}]}
        with tempfile.TemporaryDirectory() as d,patch('assistant.provider.credentials',return_value=('secret','test')),patch('urllib.request.urlopen') as request:
            request.return_value.__enter__.return_value=io.BytesIO(json.dumps(response).encode())
            path=Path(d)/'api.json'
            with self.assertRaises(ValueError):generate('test',backend='deepseek',audit_path=path)
            audit=json.loads(path.read_text());self.assertEqual(audit['response'],response)
            self.assertEqual(audit['format_repair']['action'],'rejected');self.assertNotIn('secret',path.read_text())

    def test_generate_repairs_then_normalizes_without_touching_raw(self):
        source=dict(task_type='dynamics_input',name='cold',system='newton_cooling',initial=90,rate=.1,equilibrium=20,duration=.5,duration_unit='hour',rate_unit='1/min',state_unit='摄氏度',assumptions=[],source_quotes=dict(initial='初始90摄氏度',equilibrium='环境20摄氏度',rate='0.1每分钟',duration='0.5小时'))
        envelope=dict(status='ready',questions=[],model=source,model_type='dynamics_input')
        response={'model':'test','choices':[{'finish_reason':'stop','message':{'content':json.dumps(envelope)}}]}
        original=copy.deepcopy(response)
        with tempfile.TemporaryDirectory() as d,patch('assistant.provider.credentials',return_value=('secret','test')),patch('urllib.request.urlopen') as request:
            request.return_value.__enter__.return_value=io.BytesIO(json.dumps(response).encode())
            result,meta=generate('初始90摄氏度，环境20摄氏度，0.1每分钟，0.5小时',backend='deepseek',audit_path=Path(d)/'api.json')
            self.assertEqual(result['model']['duration'],30)
            self.assertEqual(meta['response'],original)
            self.assertEqual(meta['source_model']['duration'],.5)
            self.assertEqual(meta['format_repair']['repaired_envelope']['model'],source)
            self.assertTrue(meta['format_repair']['semantic_validation_passed'])
