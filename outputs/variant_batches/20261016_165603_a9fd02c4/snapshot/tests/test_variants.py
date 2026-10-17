import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from evaluation.variants import cases,infeasible_score,BASE,summary
from evaluation.development import reference
from evaluation.batch import run_case
from modeling_assistant.solver import solve

class VariantTests(unittest.TestCase):
    def test_fixed_coverage(self):
        items=cases();self.assertEqual(len(items),32)
        self.assertEqual(len({c['id'] for c in items}),32)
        self.assertEqual(sum(c['kind']=='missing' and 'data' in c for c in items),0)
    def test_expected_question_and_unexpected_ready(self):
        case=next(c for c in cases() if c['id']=='OPT01_missing')
        for env,expected in [({'status':'needs_clarification','questions':['原料上限？'],'model':None},'pass'),({'status':'needs_clarification','questions':['天气？'],'model':None},'fail'),({'status':'ready','questions':[],'model':reference(BASE['OPT01'])},'fail')]:
            with tempfile.TemporaryDirectory() as d,patch('evaluation.batch.generate',return_value=(env,{})):
                self.assertEqual(run_case(case,Path(d),'deepseek','test')['outcome'],expected)
    def test_infeasible_conditions_must_be_preserved(self):
        case=next(c for c in cases() if c['id']=='OPT01_error');m=reference(BASE['OPT01']);m['variables'][0]['lower']=60
        record={'envelope':{'model':m},'stages':[{'result':solve(m)}]}
        self.assertTrue(infeasible_score(case,record)['passed'])
        m['variables'][0]['lower']=61
        self.assertFalse(infeasible_score(case,record)['passed'])
    def test_mixed_and_consistent_failure_separate(self):
        import json
        with tempfile.TemporaryDirectory() as d:
            rows=[dict(id='a',kind='error',outcome=o,failure_category='x',detail='',repeat=i,total_tokens=None) for i,o in enumerate(['pass','fail'])]
            summary(Path(d),rows,2)
            self.assertEqual(json.loads((Path(d)/'stability.json').read_text())[0]['classification'],'mixed')
