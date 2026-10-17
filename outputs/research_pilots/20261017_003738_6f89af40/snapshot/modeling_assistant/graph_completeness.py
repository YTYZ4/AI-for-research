"""Narrow source evidence for an explicitly closed two-node, one-edge graph."""
import re
from .numeric_text import NUM

def single_edge_evidence(text):
    if not re.search(r'有向',text) or not re.search(r'无其他边|没有其他边',text):
        return None
    if re.search(r'未知|未给|不确定|可能|如果|除非|另有|还有|更正|除了|至少|方向尚未|方向不明',text):
        return None
    node=r'[A-Za-z][A-Za-z0-9_]*'
    edge=re.search(rf'只有(?P<u>{node})到(?P<v>{node})容量(?P<value>{NUM})(?P<unit>(?:立方米|升)/(?:秒|分钟|小时|天))',text)
    nodes=re.search(rf'节点(?P<a>{node})[、,，](?P<b>{node})(?=[，。；\s])',text)
    if not edge or not nodes or edge['u']==edge['v']:
        return None
    if {nodes['a'],nodes['b']}!={edge['u'],edge['v']}:
        return None
    if len(re.findall(rf'{node}(?:到|→|->){node}容量',text))!=1:
        return None
    return {'scope':'explicit_closed_two_node_single_edge_v1',
            'edge_quote':edge[0],'nodes_quote':nodes[0],
            'closure_quote':re.search(r'无其他边|没有其他边',text)[0],
            'source':edge['u'],'target':edge['v'],'raw_value':edge['value'],'raw_unit':edge['unit'],
            'meaning':'原题已明确节点及全部边；只有一条边不表示缺边。本证据不判断任务范围、单位可换算性或整数性。'}
