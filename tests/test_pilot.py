import ast
import copy
import json
import unittest
from pathlib import Path
from unittest.mock import patch
from lab.production.checker import check
from lab.production.experiment import public_solve,request,MAX_TOKENS,changes
from lab.production.judge import score

ASSETS=Path('lab/production/assets')
class ProductionFeedbackPilotTests(unittest.TestCase):
    def setUp(self):
        self.drafts=json.loads((ASSETS/'drafts.json').read_text())
        self.reference=json.loads((ASSETS/'reference.json').read_text())
        self.problem=(ASSETS/'problem.txt').read_text()

    def test_detection_limits_without_reference_or_file_access(self):
        outcomes={}
        for name,model in self.drafts.items():
            public=public_solve(model)
            with patch('builtins.open',side_effect=AssertionError('checker cannot open files')),patch.object(Path,'read_text',side_effect=AssertionError('checker cannot read references')):
                outcomes[name]=bool(check(self.problem,model,public)['issues'])
        self.assertEqual(outcomes,dict(V1=False,V2=False,V3=True,V4=False))
        tree=ast.parse(Path('lab/production/checker.py').read_text())
        imports=[n.module for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)]
        self.assertFalse(any('evaluation' in n or 'judge' in n for n in imports))

    def test_shared_inputs_and_equal_budget_feedback_only_difference(self):
        model=self.drafts['V3'];pub=public_solve(model);diag=check(self.problem,model,pub)
        a=request(self.problem,model,pub,'self_check',diag,'test')
        b=request(self.problem,model,pub,'program_feedback',diag,'test')
        pa=json.loads(a['messages'][1]['content']);pb=json.loads(b['messages'][1]['content'])
        self.assertEqual(pb.pop('program_checks'),diag);self.assertEqual(pa,pb)
        self.assertEqual(a['messages'][0],b['messages'][0])
        self.assertEqual(a['max_tokens'],b['max_tokens']);self.assertEqual(a['max_tokens'],MAX_TOKENS)
        self.assertNotIn('verification',pub)

    def test_judge_separates_correct_answer_from_correct_model(self):
        grades={k:score(m,public_solve(m),self.reference) for k,m in self.drafts.items()}
        self.assertTrue(grades['V1']['passed'])
        self.assertFalse(any(grades[k]['passed'] for k in ['V2','V3','V4']))
        self.assertTrue(grades['V3']['answer_matches_problem'])
        self.assertFalse(grades['V3']['model_matches_problem'])
        self.assertTrue(all(g['candidate_self_valid'] for g in grades.values()))

    def test_judge_accepts_reordering_scaling_but_not_bad_coefficient(self):
        m=copy.deepcopy(self.reference);m['constraints'].reverse()
        for c in m['constraints']:
            c['rhs']*=2
            for t in c['terms']:t['coefficient']*=2
        self.assertTrue(score(m,public_solve(m),self.reference)['passed'])
        m['constraints'][0]['terms'][0]['coefficient']+=1
        self.assertFalse(score(m,public_solve(m),self.reference)['passed'])

    def test_checker_does_not_change_draft_or_invent_semantic_detection(self):
        m=self.drafts['V2'];before=copy.deepcopy(m)
        check(self.problem,m,public_solve(m))
        self.assertEqual(m,before)
        continuous=self.drafts['V3']
        self.assertEqual(check(self.problem.replace('非负整数','非负实数'),continuous,public_solve(continuous))['issues'],[])

    def test_invalid_output_is_failure_and_change_log_preserves_values(self):
        self.assertFalse(score({'bad':'output'},public_solve({'bad':'output'}),self.reference)['passed'])
        diff=changes(self.drafts['V1'],self.drafts['V4'])
        self.assertEqual(len(diff),1)
        self.assertEqual((diff[0]['before'],diff[0]['after']),(2,1))
