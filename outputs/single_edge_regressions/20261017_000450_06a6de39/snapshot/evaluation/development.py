"""Fixed eight-case development protocol; evaluators never enter model prompts."""
import json
from pathlib import Path
from . import dynamics, fitting, graphs, transport

ROOT=Path(__file__).resolve().parents[1]
CASES=[
 dict(id='OPT01',family='optimization',problem='examples/production/problem_freeform.txt',reference=None),
 dict(id='OPT02',family='optimization',problem='examples/transport/problem.txt',reference='examples/transport/reference_model.json'),
 dict(id='FIT01',family='fitting',problem='examples/fitting/calibration.txt',data='examples/fitting/calibration.csv',reference='examples/fitting/calibration_model.json'),
 dict(id='FIT02',family='fitting',problem='examples/fitting/curve.txt',data='examples/fitting/curve.csv',reference='examples/fitting/curve_model.json'),
 dict(id='DYN01',family='dynamics',problem='examples/dynamics/cooling.txt',reference='examples/dynamics/cooling_model.json',case='cooling'),
 dict(id='DYN02',family='dynamics',problem='examples/dynamics/logistic.txt',reference='examples/dynamics/logistic_model.json',case='logistic'),
 dict(id='NET01',family='graph',problem='examples/graphs/shortest_path.txt',reference='examples/graphs/shortest_path_model.json',case='shortest_path'),
 dict(id='NET02',family='graph',problem='examples/graphs/max_flow.txt',reference='examples/graphs/max_flow_model.json',case='max_flow'),
]


def reference(case):
    if case['id']=='OPT01':
        from modeling_assistant.parser import parse_template
        return parse_template((ROOT/'examples/production/problem.txt').read_text())['model']
    return json.loads((ROOT/case['reference']).read_text())


def optimization_score(case, record):
    m=record['envelope']['model'];r=record['stages'][0]['result'];expected=reference(case)
    # These two fixtures have distinct objective coefficients. Matching coefficients
    # is only an alignment proposal; ALL domains and constraints are checked next.
    actual_by_cost={t['coefficient']:t['variable'] for t in m['objective']['terms']}
    expected_by_cost={t['coefficient']:t['variable'] for t in expected['objective']['terms']}
    if set(actual_by_cost)!=set(expected_by_cost) or len(actual_by_cost)!=len(m['variables']):
        return {'passed':False,'reason':'目标系数无法唯一对齐原题变量；需要人工审查，不按数值答案判通过'}
    mapping={actual_by_cost[c]:expected_by_cost[c] for c in expected_by_cost}
    def domains(model,rename):
        return sorted((rename[v['name']],v['kind'],v['lower'],v['upper']) for v in model['variables'])
    def constraints(model,rename):
        return sorted((c['sense'],c['rhs'],tuple(sorted((rename[t['variable']],t['coefficient']) for t in c['terms']))) for c in model['constraints'])
    identity={v['name']:v['name'] for v in expected['variables']}
    structure=(m['objective']['sense']==expected['objective']['sense'] and domains(m,mapping)==domains(expected,identity) and constraints(m,mapping)==constraints(expected,identity))
    plan={mapping[k]:v for k,v in r['values'].items()}
    if case['id']=='OPT02':numeric=transport.evaluate_plan(plan,r['objective'])
    else:
        a,b=plan['A'],plan['B'];best=max(40*x+30*y for x in range(51) for y in range(41) if 2*x+y<=100 and x+2*y<=80)
        checks={'integer_nonnegative':a>=0 and b>=0 and abs(a-round(a))<1e-6 and abs(b-round(b))<1e-6,
                'resources':2*a+b<=100+1e-6 and a+2*b<=80+1e-6,
                'optimal':abs(40*a+30*b-best)<1e-6,'claimed_objective':abs(r['objective']-(40*a+30*b))<1e-6}
        numeric={'passed':all(checks.values()),'checks':checks,'enumerated_optimum':best}
    return {'passed':structure and numeric['passed'],'structural_match':structure,'variable_alignment':mapping,'numeric':numeric,
            'scope':'严格结构匹配；等价重写可能需人工复核。单位与自然语言假设另行人工审核。'}


def score(case,record,run_path):
    m=record['envelope']['model'];r=record['stages'][0]['result']
    if case['family']=='optimization':return optimization_score(case,record)
    if case['family']=='fitting':
        numeric=fitting.evaluate_run(ROOT/case['data'],run_path)
        protocol=m['task_type']=='polynomial_fit' and m['degree']==(1 if case['id']=='FIT01' else None) and r['selection']==('fixed' if case['id']=='FIT01' else 'train_only_5fold_cv')
        return {'passed':numeric['passed'] and protocol,'protocol_match':protocol,'numeric':numeric}
    if case['family']=='dynamics':return dynamics.evaluate_run(record,case['case'])
    return graphs.evaluate_run(record,case['case'])
