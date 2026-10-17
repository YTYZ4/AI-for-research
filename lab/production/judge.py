"""Offline only: reference access prohibited from generation/checker path."""
from fractions import Fraction as F
from assistant.model import validate_model, MODEL_SCHEMA
from jsonschema import Draft202012Validator
from assistant.solver import verify

def normalized(model):
    domains=sorted((v['name'],v['kind'],v['lower'],v['upper']) for v in model['variables'])
    def terms(ts):return tuple(F(str(next((t['coefficient'] for t in ts if t['variable']==n),0))) for n in ['A','B'])
    constraints=set()
    for c in model['constraints']:
        co=terms(c['terms']);rhs=F(str(c['rhs']))
        factor=abs(next((v for v in (*co,rhs) if v),F(1)))
        constraints.add((c['sense'],tuple(x/factor for x in co),rhs/factor))
    return domains,model['objective']['sense'],terms(model['objective']['terms']),constraints

def score(model,result,reference):
    try:
        Draft202012Validator(MODEL_SCHEMA).validate(model)
        validate_model(model)
    except Exception as exc:return {'passed':False,'executable':False,'reason':str(exc),'review_required':False}
    executable=result.get('status')=='optimal'
    self_valid=bool(executable and verify(model,result['values'],result['objective'])['passed'])
    names={v['name'] for v in model['variables']}
    structure=names=={'A','B'} and normalized(model)==normalized(reference)
    # Independent enumeration from this frozen problem, never used for feedback.
    best=max(40*a+30*b for a in range(51) for b in range(41) if 2*a+b<=100 and a+2*b<=80)
    numeric=False
    if executable and names=={'A','B'}:
        a,b=result['values']['A'],result['values']['B']
        numeric=(a>=0 and b>=0 and abs(a-round(a))<1e-6 and abs(b-round(b))<1e-6
                 and 2*a+b<=100+1e-6 and a+2*b<=80+1e-6
                 and abs(40*a+30*b-best)<1e-6 and abs(result['objective']-best)<1e-6)
    return {'passed':bool(executable and self_valid and structure and numeric),'executable':executable,
            'candidate_self_valid':self_valid,'model_matches_problem':structure,'answer_matches_problem':numeric,
            'reference_optimum':best,'review_required':bool(numeric and not structure),
            'review_note':'模型不匹配但数值正确，需核对是否为已知域错误或等价表达；自动结果不靠数值放行'}
