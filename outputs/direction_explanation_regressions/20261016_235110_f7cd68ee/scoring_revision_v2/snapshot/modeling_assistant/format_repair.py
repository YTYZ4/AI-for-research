"""Single-pass, allowlisted format repair; never infer or edit math fields."""
import copy
import hashlib
import json
from jsonschema import Draft202012Validator
from .model import ENVELOPE_SCHEMA, validate_envelope


def digest(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def validate_with_repair(envelope, audit):
    validator=Draft202012Validator(ENVELOPE_SCHEMA)
    errors=list(validator.iter_errors(envelope))
    audit.update(policy='redundant_top_level_model_type_v1',raw_schema_valid=not errors,
                 action='not_needed',changes=[],original_sha256=digest(envelope))
    if not errors:
        return validate_envelope(envelope)
    audit['action']='rejected'
    audit['reason']='仅允许删除与model.task_type完全相同的顶层model_type；其他错误不自动修复'
    if not isinstance(envelope,dict) or 'model_type' not in envelope:
        return validate_envelope(envelope)
    model=envelope.get('model')
    if not isinstance(model,dict) or not isinstance(model.get('task_type'),str) or envelope['model_type']!=model['task_type']:
        audit['reason']='顶层model_type与内部任务类型不一致或缺少内部任务类型，不能确定冗余'
        return validate_envelope(envelope)
    candidate=copy.deepcopy(envelope)
    removed=candidate.pop('model_type')
    if not validator.is_valid(candidate):
        audit['reason']='删除允许的冗余字段后仍有schema错误，拒绝部分修复'
        return validate_envelope(envelope)
    audit.update(action='applied',reason='顶层字段重复表达已存在的任务类型，删除不改变模型内容',
                 changes=[{'operation':'remove','path':'/model_type','old_value':removed}],
                 repaired_sha256=digest(candidate),repaired_envelope=candidate,
                 semantic_validation_passed=False)
    result=validate_envelope(candidate)
    audit['semantic_validation_passed']=True
    return result
