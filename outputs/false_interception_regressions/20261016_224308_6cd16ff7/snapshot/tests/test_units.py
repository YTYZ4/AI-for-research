import copy
import unittest
from modeling_assistant.units import normalize_dynamics
from modeling_assistant.model import validate_model,ModelClarificationError

class UnitTests(unittest.TestCase):
    def source(self):
        return dict(task_type='dynamics_input',name='source',system='logistic',initial=100,rate=.2,equilibrium=1000,duration=720,duration_unit='hour',rate_unit='1/day',state_unit='个',assumptions=[],source_quotes=dict(initial='初始100个',equilibrium='容量1000个',rate='每天0.2',duration='720小时'))

    def test_day_hour_keeps_rate_and_source(self):
        source=self.source();before=copy.deepcopy(source)
        m,a=normalize_dynamics(source,'初始100个，容量1000个，每天0.2，模拟720小时')
        self.assertEqual(m['rate'],.2);self.assertEqual(m['duration'],30)
        self.assertEqual(source,before);self.assertTrue(a['source_quotes_checked'])

    def test_min_hour_and_reverse(self):
        s=self.source();s.update(rate=.1,rate_unit='1/min',duration=.5,duration_unit='hour')
        self.assertEqual(normalize_dynamics(s)[0]['duration'],30)
        s.update(rate=6,rate_unit='1/hour',duration=30,duration_unit='min')
        self.assertEqual(normalize_dynamics(s)[0]['duration'],.5)

    def test_altered_rate_and_unit_rejected_against_original(self):
        text='初始100个，容量1000个，每天0.2，模拟720小时'
        for change in ('number','unit','quote'):
            s=self.source()
            if change=='number':s['rate']=.2/24
            if change=='unit':s['duration_unit']='day'
            if change=='quote':s['source_quotes']['duration']='30天'
            with self.assertRaises(ModelClarificationError):normalize_dynamics(s,text)

    def test_cross_year_not_assumed(self):
        s=self.source();s['duration_unit']='year'
        with self.assertRaises(ModelClarificationError):normalize_dynamics(s)

    def test_source_validation_uses_converted_horizon(self):
        s=self.source();s['duration']=7200
        validate_model(s)  # rate*duration_source=1440, but normalized product=60.
        s['equilibrium']=0
        with self.assertRaises(ModelClarificationError):validate_model(s)

    def test_celsius_case_is_equivalent_in_independent_oracle(self):
        import json
        from pathlib import Path
        from modeling_assistant.dynamics import solve_dynamics
        from evaluation.robustness import unit_score
        root=Path(__file__).resolve().parents[1]
        m=json.loads((root/'examples/dynamics/cooling_model.json').read_text());m['state_unit']='celsius'
        record={'envelope':{'model':m},'stages':[{'result':solve_dynamics(m)}]}
        self.assertTrue(unit_score({'id':'cooling_units','family':'dynamics'},record,None)['passed'])
