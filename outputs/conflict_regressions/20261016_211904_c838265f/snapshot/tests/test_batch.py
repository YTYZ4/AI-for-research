import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from evaluation.batch import run_case, summarize
from evaluation.development import CASES, reference, optimization_score
from modeling_assistant.solver import solve

class BatchTests(unittest.TestCase):
    def test_optimization_rejects_missing_constraint_even_with_correct_answer(self):
        for case in CASES[:2]:
            model=reference(case);result=solve(model)
            record={'envelope':{'model':model},'stages':[{'result':result}]}
            self.assertTrue(optimization_score(case,record)['passed'])
            model['constraints'].pop()
            self.assertFalse(optimization_score(case,record)['passed'])

    def test_clarification_is_not_pass(self):
        with tempfile.TemporaryDirectory() as d:
            with patch('evaluation.batch.generate',return_value=({'status':'needs_clarification','model':None,'questions':['missing']},{'backend':'deepseek'})):
                row=run_case(CASES[0],Path(d),'deepseek','test')
            self.assertEqual(row['failure_category'],'needs_clarification')
            self.assertIsNone(row['total_tokens'])

    def test_failure_does_not_prevent_next_case(self):
        with tempfile.TemporaryDirectory() as d:
            with patch('evaluation.batch.generate',side_effect=ValueError('invalid response')):
                first=run_case(CASES[0],Path(d),'deepseek','test')
            second=run_case(CASES[1],Path(d),'reference',None)
            self.assertEqual(first['failure_category'],'generation_error');self.assertEqual(second['outcome'],'pass')
            summarize(Path(d),[first,second],'test')
            self.assertTrue((Path(d)/'results.csv').exists())

    def test_evaluator_error_is_separate(self):
        with tempfile.TemporaryDirectory() as d:
            with patch('evaluation.batch.score',side_effect=RuntimeError('checker bug')):
                row=run_case(CASES[0],Path(d),'reference',None)
            self.assertEqual(row['failure_category'],'evaluator_error')

    def test_raw_usage_survives_schema_error(self):
        def fail(*args,**kwargs):
            kwargs['audit_path'].write_text(json.dumps({'usage':{'total_tokens':123},'response_model':'test','response':{'bad':'schema'}}))
            raise ValueError('schema invalid')
        with tempfile.TemporaryDirectory() as d:
            with patch('evaluation.batch.generate',side_effect=fail):
                row=run_case(CASES[0],Path(d),'deepseek','test')
            self.assertEqual(row['total_tokens'],123)
            self.assertTrue((Path(d)/'OPT01/api.json').exists())

    def test_provider_preserves_non_json_response(self):
        import io
        from modeling_assistant.provider import generate
        with tempfile.TemporaryDirectory() as d:
            audit=Path(d)/'api.json'
            with patch('modeling_assistant.provider.credentials',return_value=('secret','test')), patch('urllib.request.urlopen') as request:
                request.return_value.__enter__.return_value=io.BytesIO(b'not json')
                with self.assertRaises(ValueError):generate('question',backend='deepseek',audit_path=audit)
            saved=json.loads(audit.read_text())
            self.assertEqual(saved['response_text'],'not json')
            self.assertNotIn('secret',audit.read_text())
