"""Conservative extraction hints for explicit, constant Logistic inputs.
No model-answer replacement: hints are generated before the single API request.
"""
import re
import math

from .numeric_text import NUM, exact_number
UNIT=r'小时|分钟|每天|每小时|每分钟|天|日|秒|day|hour|min|s'
MAP={'小时':'hour','分钟':'min','天':'day','日':'day','秒':'s','day':'day','hour':'hour','min':'min','s':'s'}


def extract_logistic_hints(text):
    if not re.search(r'logistic',text,re.I):return None
    # Partial hints must never be presented as a complete problem.
    condition_text=re.sub(r'无迁入迁出|没有迁入迁出','',text)
    if re.search(r'时变|分段|干预|捕捞|迁入|迁出|参数估计|阈值',condition_text):return None
    patterns={
        'initial':rf'(?:(?:初始(?:时刻|数量|种群|状态)?|起始数量|起始种群|N\(0\)|N0)(?:为|有|是|=)?\s*|种群有\s*)(?P<value>{NUM})\s*(?:个|只)',
        'equilibrium':rf'(?:环境承载量|承载能力|环境容量|容量|K)\s*(?:恒定|固定)?\s*(?:为|是|=|应为)?\s*(?P<value>{NUM})\s*(?:个|只)',
        'rate':rf'(?:内禀)?增长率\s*(?:固定|恒定|为|是|=)?\s*(?P<value>{NUM})\s*(?:每|/)(?P<unit>小时|分钟|天|日|秒|day|hour|min|s)',
        'duration':rf'(?:模拟\s*(?:0\s*(?:到|至|–|-)\s*)?|时长\s*(?:为|是|=)?\s*|0\s*(?:到|至)\s*)(?P<value>{NUM})\s*(?P<unit>小时|分钟|天|日|秒|day|hour|min|s)',
    }
    values={};quotes={};units={}
    for field,pattern in patterns.items():
        matches=list(re.finditer(pattern,text,re.I))
        distinct={(exact_number(m['value']),m.groupdict().get('unit')) for m in matches}
        if len(distinct)!=1:return None
        match=matches[0];values[field]=float(match['value']);quotes[field]=match[0]
        if 'unit' in match.groupdict():units[field]=MAP[match['unit'].lower()]
    return dict(values=values,source_quotes=quotes,parameter_domain=logistic_domain(values),rate_unit='1/'+units['rate'],duration_unit=units['duration'],
                scope='明确数量和单位的常参数Logistic提取提示；不是可求解性证明')


def logistic_domain(values):
    """A parameter-domain check, never a claim that the full text is understood."""
    n,k,r,t=(values[f] for f in ('initial','equilibrium','rate','duration'))
    valid=all(math.isfinite(v) for v in (n,k,r,t)) and n>=0 and k>0 and r>0 and t>0
    trend=None
    if valid:trend='constant' if n==0 or n==k else 'decreasing' if n>k else 'increasing'
    return {'valid':valid,'initial_above_capacity':n>k if valid else None,'expected_trend':trend,
            'scope':'只验证提取到的常参数域，不证明全文条件完整或无冲突；K是平衡值，不是初值上限'}


def extraction_context(hints):
    import json
    return ('\n本地参数提取提示（以下仅来自上方原题，不是用户补充；你仍须核对完整题意）：'+json.dumps(hints,ensure_ascii=False)+
            '\n每天、天、day均可标为day，每小时可标为1/hour；原文引用由系统直接抽取，不向用户索要schema写法或再次抄题。参数无效不等于必须追问：容量冲突先中立核对；明确禁止修改时保留原值并unsupported；允许修改但需先问时再请求确认。parameter_domain.valid为true表示这些参数本身有效；initial_above_capacity为true时按原值建立下降轨迹，不索要再次确认，不把初值改到容量以内。仍须检查原文是否另有遗漏、冲突或不支持的条件。')
