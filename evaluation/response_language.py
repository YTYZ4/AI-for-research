"""Independent lexical oracles for fixed response cases; no runtime policy imports."""
import re
from decimal import Decimal
from assistant.numeric_text import NUM


def forbidden_replacement(text):
    # Separate implementation, validated against manually labeled positive/negative pairs.
    action=r'改|替换|替代|提供|绝对值|调整'
    if re.search(r'不能不|不得不|不是不能|并非不|不是不|不必不|不要不',text) and re.search(action,text):return True
    pieces=re.split(r'[，,。；;!?！？\n]|但是|但|然而|不过|同时|而且|并且|然后|却|(?:或|并|也|再)(?=请|建议|可以|可将|允许)|(?:并|也|再)(?=改为|取绝对值)',text)
    for piece in pieces:
        neg=re.search(r'不得|不要|禁止|不允许|不能|不会|不应|不建议|无法|不请求|不要求|不索要|无需|无须|不必|不需要|不(?=修改|改动|替换|更改|调整|提供|索要|取绝对值|改为)|(?:不是|并非)(?=建议|要求|请求)',piece)
        if neg:
            tail=piece[neg.end():]
            act=re.search(r'修改|改动|替换|替代|更改|调整|取绝对值|改为|修正|提供|索要',tail)
            if act:
                remainder=tail[act.end():]
                remainder=re.sub(r'或(?:改为|改成|取绝对值)', '或受否定动作', remainder)
                if re.search(r'(?<!不)(?:请提供|请修改|建议|可以|可将|是否|改为|改成|取绝对值)',remainder):return True
                piece=piece[:neg.start()]
        if re.search(r'请.{0,20}(?:提供|修改|更改|调整|纠正)|是否.{0,25}(?:改|笔误|绝对值)|建议|可以|可将|改为|改成|修正为|替换为|取绝对值|(?:提供|索要).{0,12}(?:新|替代|正实数|正数|容量|K)|(?:调整|修改|替换).{0,10}(?:参数|容量|K)',piece):return True
    return False


def conflict_checks(text,values,status):
    capacity_text=re.sub(r'(?:初值|初始|增长率|时长|N0|\br\b)\s*(?:为|是|=)?\s*'+NUM,'',text)
    values_present={Decimal(str(v)) for v in values}<={Decimal(n) for n in re.findall(NUM,capacity_text)}
    denied=bool(re.search(r'(?:没有|并无|不存在|并非|不是|无).{0,2}(?:冲突|矛盾)|记录.{0,4}(?:相同|等价|一致)',text))
    statement=bool(re.search(r'冲突|矛盾|不一致',text))
    records=bool(re.search(r'(?:两|二|2|多)(?:条|处|份).{0,12}记录|(?:数值|值)不同的记录',text))
    topic=bool(re.search(r'容量|承载量|承载能力|\bK\b',text))
    selection=bool(re.search(r'哪(?:一)?条|哪份|核对.{0,8}记录',text))
    bad=re.search(r'正实数|正数|正值|有效.{0,4}(?:值|容量)|K\s*>\s*0|大于0|必须为正|除零|建议.{0,8}(?:采用|取|改)|默认|已选|取绝对值|(?:采用|选用|使用|选择|取)\s*(?:K\s*=|较大|较小|[-+]?\d)|已(?:经)?(?:确定|选定|采用)|(?:认为|认定).{0,10}(?:准确|正确|有效)|以.{0,12}为准|按.{0,8}(?:计算|求解)',text)
    return {'all_conflict_values':values_present,'neutral':not bool(bad),
            'states_conflict':not denied and (statement or records and topic and selection),
            'requests_resolution':bool(re.search(r'确认|核对|澄清|哪|提供',text)),
            'clarification':status=='needs_clarification'}
