"""Conservative stop policy for explicitly immutable, invalid Logistic inputs."""
import re
from .extraction import extract_logistic_hints


def parameters_locked(text):
    # Explicit permission or contradictory permissions disable automatic takeover.
    # The model still sees the full text and may ask for clarification.
    if re.search(r'(?<!不)(?:可以|允许|可按需|无需禁止|并非禁止|不是禁止)[^，。；\n]{0,10}(?:修改|改动|调整|替换|纠正)',text):
        return False
    patterns=(
        r'(?:不得|禁止|不允许|不能|不要|不准|不可)[^，。；\n]{0,12}(?:改动|修改|调整|替换|更改)[^，。；\n]{0,8}(?:参数|数值|阶数|容量)',
        r'(?:不得|禁止|不允许|不能|不要|不准|不可)[^，。；\n]{0,10}(?:取绝对值|修改为其他数值)',
        r'(?:所有|全部)?(?:参数|数值)[^，。；\n]{0,5}(?:必须|应当)?(?:保持原样|保持原值|原封不动|不得变动)',
        r'保持原值[^，。；\n]{0,6}(?:不能|不得|禁止|不允许)(?:调整|修改|改动)',
    )
    return any(re.search(pattern,text) for pattern in patterns)


def has_replacement_suggestion(text):
    allowed=re.sub(r'(?:不得|禁止|不允许|不能|不会|不应|不建议|无法)[^，。；？?]{0,25}?(?:修改|改动|替换|取绝对值|改为|修正)[^，。；？?]*','',text)
    return bool(re.search(r'请.{0,20}(?:提供|修改|更改|调整|纠正)|是否.{0,25}(?:改|笔误|绝对值)|(?:建议|可以|可将|改为|修正为|替换为|取绝对值)',allowed))


def enforce_parameter_lock(text,envelope):
    if not parameters_locked(text):return envelope,None
    if envelope['status']=='unsupported' and has_replacement_suggestion('；'.join(envelope['questions'])):
        clauses=[c.strip() for q in envelope['questions'] for c in re.split(r'[。；！？?]',q) if c.strip()]
        kept=[c for c in clauses if not has_replacement_suggestion(c)]
        result={**envelope,'questions':kept+['原题条件保持不变，当前不执行求解，也不要求修改参数。']}
        return result,{'action':'sanitize_unsupported','reason':'拒绝求解后的改参数建议违反原题限制',
                       'original_status':'unsupported','original_envelope':envelope,'model_executed':False}
    hints=extract_logistic_hints(text)
    if not hints or hints['parameter_domain']['valid']:return envelope,None
    values=hints['values'];reasons=[]
    if values['initial']<0:reasons.append(f"初值{values['initial']}小于0")
    if values['equilibrium']<=0:reasons.append(f"环境容量K={values['equilibrium']}不满足K>0")
    if values['rate']<=0:reasons.append(f"增长率{values['rate']}不满足r>0")
    if values['duration']<=0:reasons.append(f"模拟时长{values['duration']}不为正")
    if not reasons:return envelope,None
    # A correct unsupported response is already sufficient; do not count a guard.
    if envelope['status']=='unsupported':return envelope,None
    stopped={'status':'unsupported','questions':['；'.join(reasons)+'。原题明确禁止改动参数；保持原值时超出当前连续Logistic模型支持范围，停止求解。'],'model':None}
    audit={'action':'unsupported','original_status':envelope['status'],'original_envelope':envelope,
           'model_executed':False,'reason':'原文禁止改值且本地原参数域检查失败','evidence':hints}
    return stopped,audit


def permission_to_ask(text):
    """Explicit global/capacity permission plus prior confirmation, not permission to act."""
    if re.search(r'如果|若|假如|除非|不(?:可以|允许)|禁止|不得|不能|不可|不准|保持原值|保持原样|不是|并非',text):
        return False
    if re.search(r'(?:不必|无需|不需要|不用|不要)\s*先(?:询问|问我|确认|征求)',text):return False
    permission=re.search(r'(?:可以|允许)\s*(?:修改|改动|调整|更改)\s*(?:参数|数值|环境容量|容量|K)',text)
    first=re.search(r'先(?:询问|问我|确认|征求)|经我确认|确认后|同意后',text)
    return bool(permission and first)


def enforce_permission_question(text,envelope):
    if not permission_to_ask(text):return envelope,None
    hints=extract_logistic_hints(text)
    if not hints:return envelope,None
    v=hints['values']
    # Only a single invalid K with otherwise valid explicit constant parameters.
    if not (v['equilibrium']<=0 and v['initial']>=0 and v['rate']>0 and v['duration']>0):return envelope,None
    q='；'.join(envelope['questions'])
    correct=(envelope['status']=='needs_clarification' and envelope.get('model') is None
             and bool(re.search(r'容量|\bK\b',q)) and bool(re.search(r'正实数|正数',q))
             and bool(re.search(r'请|是否|能否',q)) and bool(re.search(r'确认|提供|允许|同意',q))
             and not re.search(r'正整数|默认|已(?:经)?(?:改|调整|设)|建议.{0,8}\d|取绝对值',q))
    if correct:return envelope,None
    result={'status':'needs_clarification','model':None,'questions':[
        f"原题环境容量K={v['equilibrium']}不满足当前连续Logistic模型的K>0要求。你允许修改参数但要求先询问：请先确认是否调整环境容量K，并提供你确认的正实数容量（可为小数）。在确认前保留原值，不执行求解。"]}
    return result,{'action':'needs_clarification','reason':'明确允许改值但须先询问，非法容量必须等待用户确认',
                   'original_status':envelope['status'],'original_envelope':envelope,'model_executed':False,'evidence':hints}
