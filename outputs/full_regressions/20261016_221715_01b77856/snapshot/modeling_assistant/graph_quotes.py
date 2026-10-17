"""Narrow quote-only repair for explicit directed edges with one global unit."""
import copy
import re
from decimal import Decimal
from .numeric_text import NUM
from .graph_units import check_edge_quote
from .model import ModelClarificationError


def extract_global_edges(text):
    # No interpretation of corrections, scoped exceptions, multiple graphs or alternatives.
    if not re.search(r'有向|单向', text) or re.search(r'双向|无向|更正|作废|除外|除了|分别为|另一|另一个|网络甲|网络乙|或|改为|仅.{0,8}单位', text):
        return None
    declarations = list(re.finditer(r'(?:^|[，。；,;：:\n])\s*(?P<quote>(?:(?:所有|全部)?(?:边|管道|容量|距离)?(?:的)?)?单位(?:统一|均|都)?(?:为|是|：|:)\s*(?P<unit>[^，。；,;\s：:]+))', text))
    if len(declarations) != 1:
        return None
    declaration=declarations[0];unit=declaration['unit']
    node=r'[A-Za-z][A-Za-z0-9_]*'
    pattern=re.compile(rf'(?<![A-Za-z0-9_])(?P<u>{node})\s*(?:→|->|到)\s*(?P<v>{node})\s*(?:容量|上限|为|长度|距离)?\s*(?:为|是|:|：|=)?\s*(?P<w>{NUM})(?P<suffix>[^，。；,;\n]*)')
    records={}
    for match in pattern.finditer(text):
        suffix=match['suffix'].strip()
        # A local unit may repeat the global unit; any exception/extra prose disables repair.
        if suffix not in ('',unit):return None
        pair=(match['u'],match['v'])
        if pair in records:return None
        records[pair]={'weight':Decimal(match['w']),'unit':unit,
                       'source_quote':match[0].strip(),'unit_quote':declaration['quote']}
    return records or None


def repair_graph_quotes(source,text):
    try:
        for edge in source['edges']:check_edge_quote(edge,text)
        return source,None
    except ModelClarificationError:pass
    records=extract_global_edges(text)
    if not records or len(records)!=len(source['edges']):return source,None
    if set(records)!={(e['source'],e['target']) for e in source['edges']}:return source,None
    if any(Decimal(str(e['weight']))!=records[e['source'],e['target']]['weight'] or e['unit']!=records[e['source'],e['target']]['unit'] for e in source['edges']):
        return source,None
    candidate=copy.deepcopy(source);changes=[]
    for i,edge in enumerate(candidate['edges']):
        extracted=records[edge['source'],edge['target']]
        for field in ('source_quote','unit_quote'):
            if edge[field]!=extracted[field]:
                changes.append({'path':f'/edges/{i}/{field}','original':edge[field],'replacement':extracted[field]})
                edge[field]=extracted[field]
        check_edge_quote(edge,text)
    if not changes:return source,None
    return candidate,{'action':'replace_graph_quotes','scope':'global_directed_edges_v1',
                      'original_model':source,'changes':changes,'values_and_units_unchanged':True,
                      'evidence':{'global_unit':next(iter(records.values()))['unit'],'edge_count':len(records)}}
