import json
import unittest
from pathlib import Path
from modeling_assistant.model import validate_model, ModelClarificationError
from modeling_assistant.dynamics import solve_dynamics
from modeling_assistant.extraction import extract_logistic_hints
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
