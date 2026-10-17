"""Narrow semantic checks for explicit immutable-parameter instructions."""
import re


from modeling_assistant.parameter_policy import parameters_locked


def locked_question_score(envelope):
    text='；'.join(envelope['questions'])
    # Remove explicit prohibitions before looking for affirmative suggestions.
    allowed=re.sub(r'(?:不得|禁止|不允许|不能|不会|不应|不建议|无法)[^，。；？?]{0,25}?(?:修改|改动|替换|取绝对值|改为|修正)[^，。；？?]*','',text)
    bad=bool(re.search(r'请.{0,20}(?:提供|修改|更改|调整|纠正)|是否.{0,25}(?:改|笔误|绝对值)|(?:建议|可以|可将|改为|修正为|替换为|取绝对值)',allowed))
    return {'passed':not bad and bool(text.strip()),'no_replacement_suggestion':not bad,'text':text,
            'scope':'仅检查显式禁止改参数后的常见改值建议；不是完整语义证明'}
