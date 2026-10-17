"""Conservative same-unit constant Logistic capacity conflicts."""
import re
from .extraction import NUM


def capacity_conflict(text):
    if not re.search('logistic',text,re.I):return None
    # Corrections and multiple populations need full-text interpretation.
    if re.search(r'更正|纠正为|以.{0,12}为准|作废|不是|而非|种群甲|种群乙|两个种群|分段|时变|捕捞|干预',text):return None
    pattern=rf'(?:环境承载量|承载能力|环境容量|容量|K)\s*(?:恒定|固定)?\s*(?:为|是|=|应为)?\s*(?P<value>{NUM})\s*(?P<unit>个|只)'
    matches=list(re.finditer(pattern,text,re.I))
    if len({m['unit'] for m in matches})!=1:return None
    values=list(dict.fromkeys(float(m['value']) for m in matches))
    if len(values)<2:return None
    return {'values':values,'unit':matches[0]['unit'],'source_quotes':[m[0] for m in matches],
            'scope':'同一常参数Logistic题面中同单位容量记录；不选择真实值'}


def conflict_question_ok(envelope,evidence):
    q='；'.join(envelope['questions'])
    numbers={float(n) for n in re.findall(NUM,q)}
    return (envelope['status']=='needs_clarification' and envelope.get('model') is None
            and bool(re.search(r'冲突|矛盾|不一致',q))
            and set(evidence['values'])<=numbers
            and bool(re.search(r'确认|核对|澄清|哪|提供',q))
            and not re.search(r'建议.{0,8}(?:采用|取|改)|默认|已选|取绝对值|正实数|正数|正值|有效.{0,4}(?:值|容量)|K\s*>\s*0|大于0|必须为正|除零',q))


def apply_parameter_policy(text,envelope):
    evidence=capacity_conflict(text)
    if evidence:
        if conflict_question_ok(envelope,evidence):return envelope,None
        quoted='；'.join('“'+q+'”' for q in evidence['source_quotes'])
        result={'status':'needs_clarification','questions':[f'环境容量K的原文记录相互冲突：{quoted}。请核对并确认哪条记录准确，或补充记录分别适用的条件。系统未选择任何值，也未执行求解。'],'model':None}
        return result,{'action':'needs_clarification','reason':'容量原文记录冲突，先澄清再校验参数域',
                       'original_status':envelope['status'],'original_envelope':envelope,'model_executed':False,'evidence':evidence}
    from .dimension_policy import fix_dimension_question
    corrected, audit = fix_dimension_question(text,envelope)
    if audit:return corrected,audit
    from .parameter_policy import enforce_parameter_lock
    return enforce_parameter_lock(text,envelope)
