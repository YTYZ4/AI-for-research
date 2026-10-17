"""Limited correction for a missing K and an already explicit inverse-time r."""
import re


def wrong_rate_capacity_comparison(question):
    if re.search(r'不要求|不需要|无需|不必|不应|不能要求',question):return False
    return (bool(re.search(r'增长率|速率',question))
            and bool(re.search(r'容量|\bK\b',question))
            and '单位' in question and bool(re.search(r'一致|相同|匹配',question)))


def fix_dimension_question(text,envelope):
    if envelope['status']!='needs_clarification' or not re.search('logistic',text,re.I):return envelope,None
    if not re.search(r'容量(?:未提供|未知|缺失)',text):return envelope,None
    if not re.search(r'增长率\s*[-+]?\d+(?:\.\d+)?\s*每(?:天|小时|分钟|秒)',text):return envelope,None
    if not any(wrong_rate_capacity_comparison(q) for q in envelope['questions']):return envelope,None
    # Keep legitimate additional questions; remove only the mistaken comparison.
    kept=[q for q in envelope['questions'] if not wrong_rate_capacity_comparison(q)]
    fixed='请提供环境容量K的原始记录及数量单位；增长率是反时间量，K是数量量，两者不要求单位一致。'
    result={**envelope,'questions':kept+[fixed]}
    return result,{'action':'needs_clarification','reason':'已知增长率与缺失容量属于不同量纲，移除错误同单位要求',
                   'original_status':envelope['status'],'original_envelope':envelope,'model_executed':False}
