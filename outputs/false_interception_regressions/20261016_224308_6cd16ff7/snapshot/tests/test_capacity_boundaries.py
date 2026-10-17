import json
import unittest
from pathlib import Path
from modeling_assistant.model import validate_model, ModelClarificationError
from modeling_assistant.dynamics import solve_dynamics
from modeling_assistant.extraction import extract_logistic_hints, logistic_domain
from evaluation.capacity_regression import VALUES, score, question_score

ROOT=Path(__file__).resolve().parents[1]

class CapacityBoundaryTests(unittest.TestCase):
    def model(self,n,k):
        m=json.loads((ROOT/'examples/dynamics/logistic_model.json').read_text())
        m.update(initial=n,equilibrium=k)
        return m

    def test_positive_real_and_initial_boundaries(self):
        for name,n,k in VALUES:
            if k is None or k<=0:continue
            with self.subTest(name=name):
                m=self.model(n,k);validate_model(m)
                result=solve_dynamics(m)
                record={'envelope':{'model':m},'stages':[{'result':result}]}
                self.assertTrue(result['verification']['passed'])
                self.assertTrue(score({'initial':n,'capacity':k},record,None)['passed'])

    def test_nonpositive_capacity_and_negative_initial(self):
        for n,k in ((100,0),(100,-.5),(-.1,.5)):
            with self.subTest(n=n,k=k):
                with self.assertRaises(ModelClarificationError) as caught:validate_model(self.model(n,k))
                self.assertIn('正实数',str(caught.exception))
                self.assertIn('不要求整数',str(caught.exception))

    def test_extraction_preserves_fractions_and_invalid_values(self):
        for name,n,k in VALUES:
            hints=extract_logistic_hints((ROOT/f'examples/capacity_boundaries/{name}.txt').read_text())
            if k is None:self.assertIsNone(hints)
            else:
                self.assertEqual(hints['values']['initial'],n)
                self.assertEqual(hints['values']['equilibrium'],k)

    def test_question_scoring_detects_previous_failure(self):
        def envelope(q):return {'status':'needs_clarification','questions':[q]}
        self.assertFalse(question_score(envelope('请提供正整数环境容量K'))['passed'])
        self.assertFalse(question_score(envelope('请提供正实数环境容量K，但必须取整'))['passed'])
        self.assertTrue(question_score(envelope('请提供正实数环境容量K（可为小数，不要求整数）'))['passed'])
        self.assertTrue(question_score(envelope('请提供正数容量，可为小数'))['passed'])

    def test_numerical_score_rejects_rounded_capacity(self):
        m=self.model(100,1000)
        record={'envelope':{'model':m},'stages':[{'result':solve_dynamics(m)}]}
        self.assertFalse(score({'initial':100,'capacity':1000.5},record,None)['passed'])

    def test_domain_distinguishes_equilibrium_decline_and_invalid(self):
        for n,k,valid,trend in ((1.5,.5,True,'decreasing'),(.5001,.5,True,'decreasing'),
                               (.5,.5,True,'constant'),(0,.5,True,'constant'),
                               (.1,.5,True,'increasing'),(1,0,False,None),(-1,.5,False,None)):
            with self.subTest(n=n,k=k):
                result=logistic_domain(dict(initial=n,equilibrium=k,rate=.2,duration=30))
                self.assertEqual(result['valid'],valid)
                self.assertEqual(result['expected_trend'],trend)
        for field,value in (('rate',0),('duration',-1),('equilibrium',float('inf'))):
            values=dict(initial=1.5,equilibrium=.5,rate=.2,duration=30)
            values[field]=value
            self.assertFalse(logistic_domain(values)['valid'])

    def test_conflicting_synonyms_do_not_supply_complete_hints(self):
        text=(ROOT/'examples/capacity_boundaries/above_symbols.txt').read_text()
        self.assertIsNone(extract_logistic_hints(text+'起始数量为2个。'))
        self.assertIsNone(extract_logistic_hints(text+'环境承载量固定1个。'))
        self.assertIsNone(extract_logistic_hints(text+'每天捕捞。'))

    def test_above_capacity_never_clamped_and_declines(self):
        for n in (1.5,.5001):
            m=self.model(n,.5);result=solve_dynamics(m)
            self.assertEqual(result['trajectory'][0]['value'],n)
            self.assertGreater(result['final_value'],.5)
            self.assertLess(result['final_value'],n)
            wrong=self.model(.5,.5)
            record={'envelope':{'model':wrong},'stages':[{'result':solve_dynamics(wrong)}]}
            self.assertFalse(score({'initial':n,'capacity':.5},record,None)['passed'])
