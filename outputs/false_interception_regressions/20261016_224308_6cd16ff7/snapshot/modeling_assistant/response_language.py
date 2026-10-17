"""Bounded clause-level checks; not a general negation or semantics parser."""
import re

# Split before a new affirmative request as well as explicit contrast/conjunctions.
BOUNDARY=r'[，,。；;！？?\n]|但是|然而|不过|但|同时|而且|并且|然后|却|(?:或|并|也|再)(?=请|建议|可以|可将|允许)|(?:并|也|再)(?=改为|取绝对值)'
NEGATIVE=r'(?:不得|禁止|不允许|不能|不会|不应|不建议|无法|不请求|不要求|不索要|无需|无须|不必|不需要|不(?=修改|改动|替换|更改|调整|提供|索要|取绝对值|改为)|(?:不是|并非)(?=建议|要求|请求))'
ACTION=r'(?:修改|改动|替换|替代|更改|调整|取绝对值|改为|修正|提供|索要)'
SUGGESTION=r'请.{0,20}(?:提供|修改|更改|调整|纠正)|是否.{0,25}(?:改|笔误|绝对值)|建议|可以|可将|改为|改成|修正为|替换为|取绝对值|(?:提供|索要).{0,12}(?:新|替代|正实数|正数|容量|K)|(?:调整|修改|替换).{0,10}(?:参数|容量|K)'


def replacement_suggestion(text):
    # Double negations do not grant an exemption, even if punctuation is absent.
    if re.search(r'(?:不能不|不得不|不是不能|并非不|不是不|不必不|不要不).{0,20}'+ACTION,text):return True
    for clause in re.split(BOUNDARY,text):
        if not clause.strip():continue
        negative=re.search(NEGATIVE+r'[^，。；？?]{0,20}?'+ACTION,clause)
        if negative:
            # Do not let a negated action swallow a later affirmative speech act.
            tail=clause[negative.end():]
            tail=re.sub(r'或(?:改为|改成|取绝对值)', '或受否定动作', tail)
            if re.search(r'(?<!不)(?:请提供|请修改|建议|可以|可将|是否|改为|改成|取绝对值)',tail):return True
            # Earlier text may already contain an affirmative proposal.
            if re.search(SUGGESTION,clause[:negative.start()]):return True
            continue
        if re.search(SUGGESTION,clause):return True
    return False


def conflict_statement(text):
    if re.search(r'(?:没有|并无|不存在|并非|不是|无).{0,2}(?:冲突|矛盾)|记录.{0,4}(?:相同|等价|一致)',text):return False
    explicit=bool(re.search(r'冲突|矛盾|不一致',text))
    implicit=(bool(re.search(r'容量|承载量|承载能力|\bK\b',text))
              and bool(re.search(r'(?:两|二|2|多)条.{0,12}记录|(?:数值|值)不同的记录',text))
              and bool(re.search(r'哪(?:一)?条|哪份|核对.{0,8}记录',text)))
    return explicit or implicit


def conflict_preselection(text):
    return bool(re.search(r'建议.{0,8}(?:采用|取|改)|默认|已选|取绝对值|正实数|正数|正值|有效.{0,4}(?:值|容量)|K\s*>\s*0|大于0|必须为正|除零|(?:采用|选用|使用|选择|取)\s*(?:K\s*=|较大|较小|[-+]?\d)|已(?:经)?(?:确定|选定|采用)|(?:认为|认定).{0,10}(?:准确|正确|有效)|以.{0,12}为准|按.{0,8}(?:计算|求解)',text))
