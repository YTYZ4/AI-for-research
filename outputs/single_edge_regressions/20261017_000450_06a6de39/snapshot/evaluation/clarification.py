"""Narrow semantic checks for explicit immutable-parameter instructions."""
import re


from modeling_assistant.parameter_policy import parameters_locked


def locked_question_score(envelope):
    text='；'.join(envelope['questions'])
    from .response_language import forbidden_replacement
    bad=forbidden_replacement(text)
    return {'passed':not bad and bool(text.strip()),'no_replacement_suggestion':not bad,'text':text,
            'scope':'仅检查显式禁止改参数后的常见改值建议；不是完整语义证明'}
