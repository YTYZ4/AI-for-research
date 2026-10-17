"""Deterministic time conversion. LLM extracts; local arithmetic converts."""
import copy
import math
import re
from decimal import Decimal

SECONDS={'s':Decimal(1),'min':Decimal(60),'hour':Decimal(3600),'day':Decimal(86400)}
ALIASES={'s':['秒','second','seconds'], 'min':['分钟','分','minute','minutes'],
         'hour':['小时','时','hour','hours'], 'day':['天','日','day','days'], 'year':['年','year','years']}


def check_source_quotes(source,text):
    from .model import ModelClarificationError
    # Match numeric tokens independent of Chinese word boundaries.
    for field in ('initial','equilibrium','rate','duration'):
        quote=source['source_quotes'][field]
        if not quote.strip() or quote not in text:
            raise ModelClarificationError(f'原始参数{field}的引用未在题目中找到，请核对数值和单位。')
        from .numeric_text import NUM
        numbers=re.findall(NUM,quote)
        if not any(Decimal(n)==Decimal(str(source[field])) for n in numbers):
            raise ModelClarificationError(f'参数{field}与原题引用中的数值不一致，请确认原始数值；不会执行已改写的参数。')
    for field,unit in [('rate',source['rate_unit'][2:]),('duration',source['duration_unit'])]:
        quote=source['source_quotes'][field].lower()
        aliases=ALIASES[unit]
        ascii_unit=bool(re.search(r'(?<![a-z])'+re.escape(unit)+r'(?![a-z])',quote))
        if not ascii_unit and not any(alias in quote for alias in aliases):
            raise ModelClarificationError(f'原题{field}的单位与提取字段不符，请确认单位。')


def normalize_dynamics(source,text=None):
    from .model import validate_model, ModelClarificationError
    for key in ('initial','equilibrium','rate','duration'):
        if not math.isfinite(source[key]):raise ValueError('原始动态参数必须为有限数字')
    if text is not None:check_source_quotes(source,text)
    target=source['rate_unit'][2:]
    original=source['duration_unit']
    if target==original:factor=Decimal(1)
    elif target not in SECONDS or original not in SECONDS:
        raise ModelClarificationError('跨年单位换算需要明确一年天数；当前不会默认365天，请统一到秒、分、小时或天。')
    else:factor=SECONDS[original]/SECONDS[target]
    duration=float(Decimal(str(source['duration']))*factor)
    model={k:copy.deepcopy(v) for k,v in source.items() if k not in ('duration_unit','source_quotes')}
    model.update(task_type='dynamics',time_unit=target,duration=duration)
    # Keep the rate exactly as stated, convert ONLY the duration to its denominator.
    validate_model(model)
    audit={'method':'duration_to_original_rate_unit_v1','original_rate':source['rate'],
           'original_rate_unit':source['rate_unit'],'original_duration':source['duration'],
           'original_duration_unit':original,'factor':str(factor),'normalized_duration':duration,
           'normalized_time_unit':target,'rate_unchanged':True,'source_quotes_checked':text is not None}
    return model,audit
