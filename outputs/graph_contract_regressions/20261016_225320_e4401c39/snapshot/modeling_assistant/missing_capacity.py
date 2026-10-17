"""Add a missing domain description only for explicit missing constant Logistic K."""
import re
from .numeric_text import NUM

CAPACITY=r'(?:环境承载量|承载能力|环境容量|容量|(?<![A-Za-z])K(?![A-Za-z]))'


def missing_capacity_evidence(text):
    if not re.search(r'logistic',text,re.I):return None
    if re.search(r'时变|分段|干预|捕捞|参数估计|参数辨识|阈值|离散|差分|种群甲|种群乙|两个种群|更正|作废|以.{0,12}为准',text):return None
    # A value, expression, range or later answer must not be overwritten as missing.
    if re.search(CAPACITY+rf'\s*(?:恒定|固定)?\s*(?:为|是|=|应为)?\s*{NUM}',text,re.I):return None
    if re.search(CAPACITY+r'\s*(?:=|>|<|≥|≤|取决于|随)',text,re.I):return None
    missing=re.search(CAPACITY+r'\s*(?:尚)?(?:未提供|未给出|未给定|未说明|未知|缺失)',text,re.I)
    if not missing:missing=re.search(r'(?:尚)?(?:未提供|未给出|未给定|未说明)\s*(?:的)?'+CAPACITY,text,re.I)
    if not missing:return None
    return {'source_quote':missing[0],'scope':'题面明确缺少常参数Logistic容量，且未发现已给数值/表达式；不是完整语义理解'}


def complete_capacity_domain(question):
    return (bool(re.search(CAPACITY,question,re.I)) and bool(re.search(r'正实数|正数',question))
            and bool(re.search(r'正实数|小数',question)))


def augment_missing_capacity_question(text,envelope):
    if envelope['status']!='needs_clarification' or envelope.get('model') is not None:return envelope,None
    evidence=missing_capacity_evidence(text)
    if not evidence:return envelope,None
    related=[q for q in envelope['questions'] if re.search(CAPACITY,q,re.I)]
    # Leave explicit conflicts/incorrect restrictions to their own policies; adding a
    # sentence must not create a contradictory or apparently repaired response.
    for q in related:
        stripped=re.sub(r'(?:不要求|不必是|无需为|不需要是|不限于|不限定为|不必为|不需要为|无需是|不要求为)(?:正)?整数','',q)
        if re.search(r'冲突|矛盾|不一致|整数|取整|负数|非正|大于\s*1|至少\s*1',stripped,re.I):return envelope,None
    if any(complete_capacity_domain(q) for q in related):return envelope,None
    questions=list(envelope['questions'])
    questions.append('请补充环境容量K的原始记录及数量单位；当前连续Logistic模型要求K为正实数（可为小数），系统不会自行填入或替换数值。')
    result={**envelope,'questions':questions}
    return result,{'action':'augment_missing_capacity_domain','reason':'显式缺容量追问漏写正实数及可为小数的参数域',
                   'original_status':envelope['status'],'original_envelope':envelope,'model_executed':False,'evidence':evidence}
