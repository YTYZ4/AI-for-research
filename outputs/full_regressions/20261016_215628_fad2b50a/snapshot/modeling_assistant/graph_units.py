"""Auditable edge conversion; no LLM arithmetic and no inferred unit factors."""
import copy
import math
import re
from decimal import Decimal
from fractions import Fraction
from .model import ModelClarificationError
from .numeric_text import NUM

LENGTH = {'mm': ('mm','毫米'), 'cm': ('cm','厘米'),
          'm': ('m','米','meter','meters','metre','metres'),
          'km': ('km','千米','公里','kilometer','kilometers','kilometre','kilometres')}
LENGTH_SCALE = {'mm': Fraction(1,1000), 'cm': Fraction(1,100), 'm': Fraction(1), 'km': Fraction(1000)}
VOLUME = {'m3': ('m3','m³','立方米'), 'L': ('L','l','升')}
TIME = {'s': ('s','秒'), 'min': ('min','分钟'), 'hour': ('h','hour','小时'), 'day': ('day','天')}


def unit_info(unit):
    value = unit.strip()
    for name, aliases in LENGTH.items():
        if value.casefold() in [a.casefold() for a in aliases]:
            return 'length', LENGTH_SCALE[name]
    parts = value.split('/')
    if len(parts) == 2:
        for volume, aliases in VOLUME.items():
            for time, times in TIME.items():
                if parts[0].strip() in aliases and parts[1].strip() in times:
                    return 'volume/time', (Fraction(1) if volume == 'm3' else Fraction(1,1000)) / {'s':1,'min':60,'hour':3600,'day':86400}[time]
    return None


def contains_unit(quote, unit):
    # Exact original spelling, with boundaries: m must not match km or mm.
    return bool(re.search(r'(?<![A-Za-z\u4e00-\u9fff/])' + re.escape(unit) + r'(?![A-Za-z\u4e00-\u9fff³0-9/])', quote)) or unit in re.findall(r'单位(?:统一)?(?:为|是|：|:)\s*([^，。；,;]+)', quote)


def check_edge_quote(edge, text):
    quote, unit_quote = edge['source_quote'], edge['unit_quote']
    if not quote.strip() or quote not in text or not unit_quote.strip() or unit_quote not in text:
        raise ModelClarificationError('图边原值或单位引用不在原题中，请核对原始记录。')
    # Check endpoints as tokens, but do not pretend to prove arbitrary direction prose.
    for node in (edge['source'], edge['target']):
        if not re.search(r'(?<![A-Za-z0-9_])'+re.escape(node)+r'(?![A-Za-z0-9_])', quote):
            raise ModelClarificationError('图边引用缺少对应端点，请核对该边的原始记录。')
    numbers = re.findall(NUM, quote)
    if not any(Decimal(n) == Decimal(str(edge['weight'])) for n in numbers):
        raise ModelClarificationError('图边数值与原文引用不一致，请保留原题数值，不要预先换算。')
    if not contains_unit(unit_quote, edge['unit']):
        raise ModelClarificationError('图边单位与原文引用不一致，请保留原题单位写法。')


def normalize_graph(source, text=None):
    from .model import validate_model
    model = copy.deepcopy(source)
    model['task_type'] = 'graph'
    converted, audit = [], []
    target = source['unit'].strip()
    if not target:
        raise ModelClarificationError('请明确图边统一输出单位。')
    for index, edge in enumerate(source['edges']):
        value = edge['weight']
        if isinstance(value, bool) or not math.isfinite(value) or value < 0:
            raise ValueError('图边原始数值必须有限且非负')
        if text is not None:
            check_edge_quote(edge, text)
        original = edge['unit'].strip()
        left, right = unit_info(original), unit_info(target)
        if not original:
            raise ModelClarificationError('图边缺少原始单位，请核对。')
        if original == target:
            factor = Fraction(1)
        elif left is None or right is None or left[0] != right[0]:
            raise ModelClarificationError('图边单位无法确定性换算或量纲不一致，请核对单位及必要的换算依据；不会猜测因子。')
        else:
            factor = left[1] / right[1]
        exact = Fraction(str(value)) * factor
        if source['problem'] == 'max_flow' and exact.denominator != 1:
            raise ModelClarificationError('换算后容量不是整数，超出当前最大流求解器范围；保留原值，不截断或四舍五入。')
        if exact > 10**9:
            raise ModelClarificationError('换算后边权超过当前1e9上限；保留原值，停止求解。')
        weight = int(exact) if exact.denominator == 1 else float(exact)
        if exact and weight == 0:
            raise ModelClarificationError('图边换算发生数值下溢，停止求解。')
        converted.append(dict(source=edge['source'], target=edge['target'], weight=weight))
        audit.append(dict(index=index, source=edge['source'], target=edge['target'],
                          original_weight=value, original_unit=edge['unit'], factor=str(factor),
                          normalized_weight=weight, normalized_unit=target,
                          source_quote=edge['source_quote'], unit_quote=edge['unit_quote']))
    model.update(edges=converted, unit=target)
    validate_model(model)
    return model, dict(method='graph_edges_exact_fraction_v1', source_quotes_checked=text is not None,
                       target_unit=target, edges=audit)
