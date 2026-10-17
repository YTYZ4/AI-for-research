import json
import math
import tempfile
import unittest
from pathlib import Path
from assistant.dynamics import solve_dynamics
from assistant.model import validate_model
from assistant.cli import main
ROOT=Path(__file__).resolve().parents[1]

class DynamicsTests(unittest.TestCase):
    def model(self,name='cooling'):
        return json.loads((ROOT/'examples/dynamics'/f'{name}_model.json').read_text())

    def test_cooling_analytic(self):
        r=solve_dynamics(self.model())
        self.assertTrue(r['verification']['passed'])
        self.assertAlmostEqual(r['final_value'],20+70*math.exp(-3),places=6)

    def test_logistic_analytic(self):
        r=solve_dynamics(self.model('logistic'))
        self.assertTrue(r['verification']['passed'])
        self.assertAlmostEqual(r['final_value'],1000/(1+9*math.exp(-6)),places=5)

    def test_equilibria_zero_and_above_capacity(self):
        for initial in (0,1000,1500):
            m=self.model('logistic');m['initial']=initial
            r=solve_dynamics(m)
            self.assertTrue(r['verification']['passed'])
            if initial in (0,1000):self.assertAlmostEqual(r['final_value'],initial)
            else:self.assertGreater(r['final_value'],1000)

    def test_heating_negative_temperature(self):
        m=self.model();m['initial']=-10
        r=solve_dynamics(m)
        self.assertTrue(r['verification']['passed'])
        self.assertGreater(r['final_value'],-10)

    def test_invalid_parameters(self):
        for key,value in [('rate',0),('initial',float('nan')),('duration',-1),('rate_unit','1/hour')]:
            m=self.model();m[key]=value
            with self.assertRaises(ValueError):validate_model(m)
        for key,value in [('initial',-1),('equilibrium',0)]:
            m=self.model('logistic');m[key]=value
            with self.assertRaises(ValueError):validate_model(m)

    def test_time_unit_conversion(self):
        m=self.model();before=solve_dynamics(m)
        m.update(duration=.5,rate=6,time_unit='hour',rate_unit='1/hour')
        after=solve_dynamics(m)
        self.assertAlmostEqual(before['final_value'],after['final_value'],places=6)

    def test_cli_and_prepare(self):
        for prepare in ([],['--prepare-only']):
            with tempfile.TemporaryDirectory() as d:
                self.assertEqual(main(['--model-file',str(ROOT/'examples/dynamics/cooling_model.json'),'--output',d]+prepare),0)
                folder=next(Path(d).iterdir())
                self.assertTrue((folder/'report.md').exists())
                self.assertEqual((folder/'trajectory.csv').exists(),not bool(prepare))

    def test_independent_oracle_rejects_wrong_problem(self):
        from evaluation.dynamics import evaluate_run
        m=self.model();record={'envelope':{'model':m},'stages':[{'result':solve_dynamics(m)}]}
        self.assertTrue(evaluate_run(record,'cooling')['passed'])
        m['rate']=.2
        record['stages'][0]['result']=solve_dynamics(m)
        self.assertFalse(evaluate_run(record,'cooling')['passed'])
