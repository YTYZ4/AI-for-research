"""Repair only provenance text when independent extraction matches every value/unit."""
import copy
from decimal import Decimal
from .extraction import extract_logistic_hints
from .units import check_source_quotes
from .model import ModelClarificationError


def repair_source_quotes(source,text):
    try:check_source_quotes(source,text);return source,None
    except ModelClarificationError:pass
    hints=extract_logistic_hints(text)
    if not hints or source.get('system')!='logistic':return source,None
    if any(Decimal(str(source[k]))!=Decimal(str(v)) for k,v in hints['values'].items()):return source,None
    if any(source[k]!=hints[k] for k in ('rate_unit','duration_unit')):return source,None
    candidate=copy.deepcopy(source);candidate['source_quotes']=hints['source_quotes']
    check_source_quotes(candidate,text)
    changes=[{'field':k,'original':source['source_quotes'][k],'replacement':v} for k,v in hints['source_quotes'].items() if source['source_quotes'][k]!=v]
    return candidate,{'action':'replace_source_quotes','original_model':source,'changes':changes,
                      'values_and_units_unchanged':True,'evidence':hints}
