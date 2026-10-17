"""No file I/O, reference model, error label, or evaluator dependencies."""
import re
from assistant.model import validate_model, MODEL_SCHEMA
from jsonschema import Draft202012Validator
from assistant.solver import verify

def check(problem,model,public_result):
    issues=[]
    try:
        Draft202012Validator(MODEL_SCHEMA).validate(model)
        validate_model(model)
    except Exception as exc:
        return {'issues':[{'code':'invalid_model','detail':str(exc)}],'scope':'模型结构/数值合法性'}
    match=re.search(r'产量均为非负整数',problem)
    if match:
        for v in model['variables']:
            if v['kind']!='integer' or v['lower']<0:
                issues.append({'code':'source_domain','variable':v['name'],
                               'quote':match[0],'detail':'候选变量域与原文明示的全局产量域不一致'})
    if public_result.get('values') is not None:
        audit=verify(model,public_result['values'],public_result.get('objective'))
        issues.extend({'code':'candidate_solution','detail':c} for c in audit['checks'] if not c['passed'])
    return {'issues':issues,'scope':'仅结构、显式全局整数域及候选模型自身验证；未发现问题不证明原题建模正确'}
