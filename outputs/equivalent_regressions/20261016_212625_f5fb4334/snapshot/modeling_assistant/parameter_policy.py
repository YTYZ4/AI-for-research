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


def enforce_parameter_lock(text,envelope):
    if not parameters_locked(text):return envelope,None
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
