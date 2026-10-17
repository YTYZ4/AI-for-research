import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from modeling_assistant.provider import generate
from modeling_assistant.cli import main
ROOT=Path(__file__).resolve().parents[1]

class ParameterFeedbackTests(unittest.TestCase):
    def response(self,capacity):
        m=json.loads((ROOT/'examples/dynamics/logistic_model.json').read_text());m['equilibrium']=capacity
        if capacity==1000:
            m.update(task_type='dynamics_input',duration_unit=m.pop('time_unit'),source_quotes={'initial':'初值100','equilibrium':'容量应为1000个','rate':'速率0.2每天','duration':'时长30天'})
        return {'model':'test','usage':{'total_tokens':100},'choices':[{'finish_reason':'stop','message':{'content':json.dumps({'status':'ready','questions':[],'model':m})}}]}

    def test_guard_preserves_raw_and_asks(self):
        with tempfile.TemporaryDirectory() as d,patch('modeling_assistant.provider.credentials',return_value=('secret','test')),patch('urllib.request.urlopen') as request:
            request.return_value.__enter__.return_value=io.BytesIO(json.dumps(self.response(0)).encode())
            envelope,meta=generate('K=0',backend='deepseek',audit_path=Path(d)/'api.json')
            self.assertEqual(envelope['status'],'needs_clarification');self.assertIsNone(envelope['model'])
            self.assertFalse(meta['local_validation']['model_executed'])
            self.assertEqual(json.loads(meta['response']['choices'][0]['message']['content'])['model']['equilibrium'],0)
            self.assertEqual(json.loads((Path(d)/'api.json').read_text())['local_validation'],meta['local_validation'])

    def test_interactive_corrected_value_runs_without_auto_substitution(self):
        with tempfile.TemporaryDirectory() as d,patch('modeling_assistant.provider.credentials',return_value=('secret','test')),patch('urllib.request.urlopen') as request,patch('builtins.input',side_effect=['Logistic K=0，初值100，速率0.2每天，时长30天','','容量应为1000个']):
            responses=[io.BytesIO(json.dumps(self.response(0)).encode()),io.BytesIO(json.dumps(self.response(1000)).encode())]
            request.return_value.__enter__.side_effect=responses
            self.assertEqual(main(['--interactive','--backend','deepseek','--output',d]),0)
            records=[json.loads(p.read_text()) for p in Path(d).glob('*/run.json')]
            self.assertEqual(sum(bool(r['stages']) for r in records),1)
            self.assertEqual(next(r for r in records if r['stages'])['envelope']['model']['equilibrium'],1000)

    def test_bad_csv_never_calls_model(self):
        with tempfile.TemporaryDirectory() as d,patch('modeling_assistant.cli.generate') as network:
            p=Path(d)/'bad.csv';p.write_text('x,y,split\n1,,train\n')
            self.assertEqual(main(['--backend','deepseek','--text','拟合','--data',str(p),'--output',d]),2)
            network.assert_not_called()

    def test_data_quality_fixtures(self):
        from modeling_assistant.fitting import load_data
        for name in ('missing_y','nan','bad_split','train_only','constant_x','wrong_header'):
            with self.subTest(name=name),self.assertRaises(ValueError):load_data(ROOT/'examples/robustness'/f'{name}.csv')
        self.assertEqual(load_data(ROOT/'examples/robustness/valid.csv')['counts'],{'train':45,'test':15})

    def test_unit_oracle_rejects_unconverted_rate(self):
        from evaluation.robustness import unit_score
        from modeling_assistant.dynamics import solve_dynamics
        m=json.loads((ROOT/'examples/dynamics/cooling_model.json').read_text())
        m.update(time_unit='hour',rate_unit='1/hour',duration=.5,rate=6)
        record={'envelope':{'model':m},'stages':[{'result':solve_dynamics(m)}]}
        case={'id':'cooling_units','family':'dynamics'}
        self.assertTrue(unit_score(case,record,None)['passed'])
        m['rate']=.1;record['stages'][0]['result']=solve_dynamics(m)
        self.assertFalse(unit_score(case,record,None)['passed'])
