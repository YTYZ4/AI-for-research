import copy
import itertools
import json
import random
import tempfile
import unittest
from pathlib import Path
from modeling_assistant.graphs import solve_graph
from modeling_assistant.model import validate_model
from modeling_assistant.cli import main
ROOT=Path(__file__).resolve().parents[1]

class GraphTests(unittest.TestCase):
    def model(self,problem='shortest_path'):
        return json.loads((ROOT/'examples/graphs'/f'{problem}_model.json').read_text())

    def test_reference_path(self):
        r=solve_graph(self.model())
        self.assertEqual(r['path'],['S','B','A','C','T']);self.assertEqual(r['value'],8)
        self.assertTrue(r['verification']['passed'])

    def test_reference_flow(self):
        r=solve_graph(self.model('max_flow'))
        self.assertEqual(r['value'],15);self.assertEqual(r['cut']['capacity'],15)
        self.assertTrue(r['verification']['passed'])

    def test_unreachable_and_empty(self):
        for problem in ('shortest_path','max_flow'):
            m=self.model(problem);m['edges']=[];r=solve_graph(m)
            self.assertEqual(r['status'],'unreachable' if problem=='shortest_path' else 'optimal')
            self.assertTrue(r['verification']['passed'])

    def test_zero_weight_cycle(self):
        m=self.model();m['edges'] += [dict(source='A',target='B',weight=0)]
        m['edges'][2]['weight']=0
        self.assertEqual(solve_graph(m)['value'],7)

    def test_invalid_models(self):
        for change in ('duplicate','negative','unknown','fraction','nan'):
            m=self.model('max_flow')
            if change=='duplicate':m['edges'].append(copy.deepcopy(m['edges'][0]))
            if change=='negative':m['edges'][0]['weight']=-1
            if change=='unknown':m['edges'][0]['source']='X'
            if change=='fraction':m['edges'][0]['weight']=.5
            if change=='nan':m['edges'][0]['weight']=float('nan')
            with self.assertRaises(ValueError):validate_model(m)

    def test_random_flows_against_exhaustive_cuts(self):
        rng=random.Random(17)
        for _ in range(30):
            m=self.model('max_flow');m['nodes']=['S','A','B','C','T']
            m['edges']=[dict(source=u,target=v,weight=rng.randrange(8)) for u,v in itertools.permutations(m['nodes'],2) if rng.random()<.4]
            cuts=[]
            for membership in itertools.product((False,True),repeat=3):
                side={'S'}|{n for n,b in zip(['A','B','C'],membership) if b}
                cuts.append(sum(e['weight'] for e in m['edges'] if e['source'] in side and e['target'] not in side))
            r=solve_graph(m)
            self.assertEqual(r['value'],min(cuts));self.assertTrue(r['verification']['passed'])

    def test_cli_export_and_prepare(self):
        for prepare in ([],['--prepare-only']):
            with tempfile.TemporaryDirectory() as d:
                self.assertEqual(main(['--model-file',str(ROOT/'examples/graphs/max_flow_model.json'),'--output',d]+prepare),0)
                folder=next(Path(d).iterdir());self.assertTrue((folder/'edges.csv').exists());self.assertTrue((folder/'report.md').exists())

    def test_independent_original_problem_oracle(self):
        from evaluation.graphs import evaluate_run
        for case in ('shortest_path','max_flow'):
            m=self.model(case);r=solve_graph(m)
            record={'envelope':{'model':m},'stages':[{'result':r}]}
            self.assertTrue(evaluate_run(record,case)['passed'])
            m['edges'][0]['weight']+=1
            self.assertFalse(evaluate_run(record,case)['passed'])

    def test_shortest_path_against_enumeration(self):
        rng=random.Random(19)
        for _ in range(30):
            m=self.model();m['edges']=[dict(source=u,target=v,weight=rng.randrange(8)) for u,v in itertools.permutations(m['nodes'],2) if rng.random()<.3]
            candidates=[]
            def visit(node,seen,cost):
                if node=='T':candidates.append(cost);return
                for e in m['edges']:
                    if e['source']==node and e['target'] not in seen:visit(e['target'],seen|{e['target']},cost+e['weight'])
            visit('S',{'S'},0)
            r=solve_graph(m)
            self.assertEqual(r['value'],min(candidates) if candidates else None)
            self.assertTrue(r['verification']['passed'])

    def test_explicit_isolated_target(self):
        m=self.model();m.update(nodes=['S','A','T'],edges=[dict(source='S',target='A',weight=2)])
        r=solve_graph(m)
        self.assertEqual(r['status'],'unreachable')
        self.assertEqual(r['reachable'],['A','S'])
        self.assertIsNone(r['distances']['T'])
