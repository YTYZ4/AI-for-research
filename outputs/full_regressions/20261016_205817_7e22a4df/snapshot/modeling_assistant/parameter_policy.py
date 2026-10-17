"""Conservative stop policy for explicitly immutable, invalid Logistic inputs."""
import re
from .extraction import extract_logistic_hints


def parameters_locked(text):
    return bool(re.search(r'(?:不得|禁止|不允许|不能).{0,18}(?:改动参数|修改参数|替换.{0,6}(?:数值|阶数)|取绝对值|修改负容量|修改为其他数值)',text))


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
