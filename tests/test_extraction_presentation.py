import copy
import json
import tempfile
import unittest
from pathlib import Path
from assistant.extraction import extract_logistic_hints
from assistant.presentation import presentation_record
from assistant.cli import save_record
from assistant.fitting import load_data,solve_fit
ROOT=Path(__file__).resolve().parents[1]

class ExtractionPresentationTests(unittest.TestCase):
    def test_complete_known_units_extract_without_conversion(self):
        text=(ROOT/'examples/robustness/logistic_units.txt').read_text();h=extract_logistic_hints(text)
        self.assertEqual(h['values']['rate'],.2);self.assertEqual(h['values']['duration'],720)
        self.assertEqual(h['rate_unit'],'1/day');self.assertEqual(h['duration_unit'],'hour')
        self.assertTrue(all(q in text for q in h['source_quotes'].values()))

    def test_missing_ambiguous_and_unsupported_not_complete(self):
        text=(ROOT/'examples/robustness/logistic_units.txt').read_text()
        self.assertIsNone(extract_logistic_hints(text.replace('容量恒定1000个','容量未提供')))
        self.assertIsNone(extract_logistic_hints(text+'另一增长率0.3每天。'))
        self.assertIsNone(extract_logistic_hints(text+'每天干预捕捞。'))

    def test_invalid_value_not_corrected(self):
        text=(ROOT/'examples/robustness/logistic_units.txt').read_text().replace('1000个','0个')
        self.assertEqual(extract_logistic_hints(text)['values']['equilibrium'],0)

    def test_system_claim_hidden_without_mutating_source(self):
        model=json.loads((ROOT/'examples/fitting/curve_model.json').read_text())
        model['assumptions']=['系统输出不包含拟合系数','观测相互独立','按CSV的train/test划分，不使用test选阶']
        data=load_data(ROOT/'examples/fitting/curve.csv')
        record={'created_at':'test','backend':'test','generation':{},'envelope':{'status':'ready','questions':[],'model':model},'stages':[{'model':model,'label':'fit','result':solve_fit(model,data)}],'dataset':data}
        before=copy.deepcopy(record);shown,audit=presentation_record(record)
        self.assertEqual(record,before);self.assertNotIn('系统输出不包含拟合系数',shown['envelope']['model']['assumptions'])
        self.assertIn('按CSV的train/test划分，不使用test选阶',shown['envelope']['model']['assumptions'])
        with tempfile.TemporaryDirectory() as d:
            folder=save_record(record,d);report=(folder/'report.md').read_text()
            self.assertNotIn('系统输出不包含拟合系数',report)
            self.assertIn('计算并保存拟合系数',report);self.assertIn('参数：',report)
            saved=json.loads((folder/'run.json').read_text());self.assertIn('系统输出不包含拟合系数',saved['envelope']['model']['assumptions'])
            self.assertTrue(json.loads((folder/'presentation_audit.json').read_text())['suppressed_display_only'])
