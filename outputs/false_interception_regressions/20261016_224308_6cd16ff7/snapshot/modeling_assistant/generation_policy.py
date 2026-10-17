"""Source-derived pre-generation routing hints, never a replacement response."""
import json
import re
from .extraction import extract_logistic_hints
from .capacity_conflict import capacity_records
from .parameter_policy import parameters_locked,permission_to_ask
from .missing_capacity import missing_capacity_evidence


def generation_policy_context(text):
    if not re.search('logistic',text,re.I):return None
    if re.search(r'时变|分段|干预|捕捞|参数估计|参数辨识|阈值|离散|差分|种群甲|种群乙|两个种群|更正|作废|以.{0,12}为准|如果|假如|若|否则|除非|并非|不是',text):return None
    records=capacity_records(text);hints=extract_logistic_hints(text)
    locked=parameters_locked(text)
    result={'policy':'logistic_response_priority_v1','parameters_locked':locked,
            'scope':'从原文提取的生成前分流提示；仍须核对全文，不替代模型回复、后置护栏或独立评分'}
    if records and records['relation']=='conflicting':
        result.update(route='neutral_conflict',evidence=records,
                      response_rule='needs_clarification：只列各原记录并中立核对。本轮不讨论正值域、不提出确认后的改值分支、不选择值。')
    elif hints and not hints['parameter_domain']['valid'] and locked:
        clauses=[c.strip() for c in re.split(r'[。；，\n]',text) if c.strip()]
        result.update(route='immutable_invalid',evidence=hints,restriction_quotes=[c for c in clauses if parameters_locked(c)],
                      response_rule='unsupported：保留原值，说明该参数使当前模型无效。不要请求正容量、替代数值、改值许可或新模型。')
    elif hints and not hints['parameter_domain']['valid'] and permission_to_ask(text):
        result.update(route='permission_before_change',evidence=hints,
                      response_rule='needs_clarification：先请用户确认并提供正实数容量（可为小数），不自行选值，不直接拒绝。')
    elif missing_capacity_evidence(text):
        result.update(route='missing_capacity',evidence=missing_capacity_evidence(text),
                      response_rule='needs_clarification：补充真正缺失的正实数容量K（可为小数）及数量单位；保留其他缺失条件问题。')
    elif hints and hints['parameter_domain']['valid']:
        result.update(route='valid_parameters',evidence=hints,
                      response_rule='参数域有效：不能因初值高于K、K为小数或禁止改动而追问。若任务完整且在支持范围内，ready。')
    else:return None
    return result


def render_policy_context(context):
    return '\n生成前响应分流检查（仅来自原题；优先核对是否有冲突、缺失和禁止改值，不是参考答案）：'+json.dumps(context,ensure_ascii=False)
