import copy
import unittest
from pathlib import Path
from modeling_assistant.extraction import extract_logistic_hints
from modeling_assistant.source_quotes import repair_source_quotes
from modeling_assistant.parameter_policy import enforce_parameter_lock, has_replacement_suggestion
from evaluation.full_regression import classify


class ProvenanceAndRefusalTests(unittest.TestCase):
    def source(self):
        text=Path('examples/equivalent_boundaries/leading_dot.txt').read_text()
        h=extract_logistic_hints(text)
        return text,dict(system='logistic',**h['values'],rate_unit=h['rate_unit'],duration_unit=h['duration_unit'],source_quotes=h['source_quotes'])

    def test_punctuation_repair_keeps_numbers_and_original(self):
        text,source=self.source();source['source_quotes']['equilibrium']='环境容量恒定.5个；另一记录K=0.50个'
        before=copy.deepcopy(source);fixed,audit=repair_source_quotes(source,text)
        self.assertEqual(source,before)
        self.assertEqual({k:v for k,v in fixed.items() if k!='source_quotes'},{k:v for k,v in source.items() if k!='source_quotes'})
        self.assertTrue(all(q in text for q in fixed['source_quotes'].values()))
        self.assertEqual(audit['original_model'],before)

    def test_value_unit_and_conflict_never_repaired(self):
        text,source=self.source();source['source_quotes']['equilibrium']='改写引用'
        for key,value in (('equilibrium',.6),('rate_unit','1/hour'),('duration_unit','hour'),('system','newton_cooling')):
            changed=copy.deepcopy(source);changed[key]=value
            fixed,audit=repair_source_quotes(changed,text)
            self.assertIsNone(audit);self.assertEqual(fixed,changed)
        fixed,audit=repair_source_quotes(source,text+'另一记录环境容量为0.6个。')
        self.assertIsNone(audit)

    def test_valid_quote_stays_native(self):
        text,source=self.source();fixed,audit=repair_source_quotes(source,text)
        self.assertIsNone(audit);self.assertEqual(fixed,source)

    def test_source_repair_not_counted_native_or_format_only(self):
        result=classify({'outcome':'pass'},{'source_quote_repair':{'action':'replace_source_quotes'},'format_repair':{'raw_schema_valid':True,'action':'not_needed'}})
        self.assertFalse(result['original_pass']);self.assertFalse(result['after_format_pass']);self.assertTrue(result['final_pass'])

    def test_refusal_suggestions_removed_but_reason_kept(self):
        original={'status':'unsupported','questions':['K=0导致除零。请提供正数K或允许修改参数。'],'model':None}
        fixed,audit=enforce_parameter_lock('Logistic容量0个。不得改动参数。',original)
        self.assertIn('K=0导致除零',fixed['questions'])
        self.assertFalse(has_replacement_suggestion('；'.join(fixed['questions'])))
        self.assertEqual(audit['original_envelope'],original)

    def test_correct_refusal_or_permission_not_sanitized(self):
        original={'status':'unsupported','questions':['K=0导致除零，不能修改参数。'],'model':None}
        self.assertIsNone(enforce_parameter_lock('Logistic容量0个。不得改动参数。',original)[1])
        original['questions']=['请提供正数K']
        self.assertIsNone(enforce_parameter_lock('Logistic容量0个。可以修改参数。',original)[1])
