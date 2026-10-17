import copy
import json
import tempfile
import unittest
from pathlib import Path
import numpy as np
from modeling_assistant.fitting import load_data, solve_fit, fit_polynomial, predict, data_context
from modeling_assistant.cli import main
from modeling_assistant.model import validate_model

ROOT = Path(__file__).resolve().parents[1]
class FittingTests(unittest.TestCase):
    def setUp(self):
        self.data = load_data(ROOT/'examples/fitting/curve.csv')
        self.model = json.loads((ROOT/'examples/fitting/curve_model.json').read_text())

    def test_known_polynomial(self):
        x = np.arange(12.)
        fit = fit_polynomial(x, 2+3*x-.4*x*x, 2)
        np.testing.assert_allclose(predict(fit, [1.5, 4.5]), 2+3*np.array([1.5,4.5])-.4*np.array([1.5,4.5])**2, atol=1e-10)

    def test_holdout_does_not_change_fit_or_selection(self):
        before = solve_fit(self.model, self.data)
        changed = copy.deepcopy(self.data)
        for row in changed['rows']:
            if row['split'] == 'test': row['y'] += 1000
        after = solve_fit(self.model, changed)
        self.assertEqual(before['fit'], after['fit'])
        self.assertEqual(before['degree'], after['degree'])
        self.assertEqual(before['cv_scores'], after['cv_scores'])
        self.assertGreater(after['metrics']['test']['rmse'], 900)
        self.assertEqual(data_context(self.data), data_context(changed))

    def test_linear_independent_closed_form(self):
        self.model['degree'] = 1
        result = solve_fit(self.model, self.data)
        train = [r for r in self.data['rows'] if r['split']=='train']
        x=np.array([r['x'] for r in train]);y=np.array([r['y'] for r in train])
        slope=sum((x-x.mean())*(y-y.mean()))/sum((x-x.mean())**2)
        intercept=y.mean()-slope*x.mean()
        np.testing.assert_allclose(predict(result['fit'],x),slope*x+intercept,atol=1e-10)

    def test_reject_invalid_degree_and_degenerate_data(self):
        self.model['degree']=6
        with self.assertRaises(ValueError):validate_model(self.model)
        with self.assertRaises(ValueError):fit_polynomial(np.ones(12),np.arange(12),1)

    def test_bad_csv(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'bad.csv';p.write_text('x,y,split\n1,nan,train\n')
            with self.assertRaises(ValueError):load_data(p)

    def test_cli_artifacts(self):
        with tempfile.TemporaryDirectory() as d:
            status=main(['--model-file',str(ROOT/'examples/fitting/curve_model.json'),'--data',str(ROOT/'examples/fitting/curve.csv'),'--output',d])
            self.assertEqual(status,0)
            folder=next(Path(d).iterdir())
            self.assertTrue((folder/'predictions.csv').exists())
            record=json.loads((folder/'run.json').read_text())
            self.assertEqual(record['dataset']['sha256'],self.data['sha256'])
            self.assertIn('留出', (folder/'report.md').read_text())
