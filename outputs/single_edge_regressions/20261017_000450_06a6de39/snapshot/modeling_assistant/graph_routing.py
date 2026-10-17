"""Conservative evidence-based request selection, never a solvability decision."""
import re

NAMED=r'最小费用流|最小成本流|多商品流|最大流|最短路径|最短路|\bmax[ _-]?flow\b|\bshortest[ _-]?path\b'
FAMILIES=r'Logistic|冷却|微分|拟合|回归|生产计划|运输分配|多项式'
STRUCTURE=r'有向网络|无向网络|节点|顶点|弧|管网|管道|道路网络'
FLOW_GOAL=r'(?:流量|输送量|吞吐量|通流量).{0,10}(?:最大|最多|尽可能大)|(?:最大化|尽可能多).{0,8}(?:流量|输送|吞吐)'
COST_GOAL=r'(?:成本|费用|运费|开销).{0,10}(?:最小|最低|尽可能低)|(?:最小化|最低).{0,8}(?:成本|费用|运费)'
PATH_GOAL=r'(?:路线|路径|路程|距离).{0,10}(?:最短|最小)|(?:最短|最小).{0,8}(?:路线|路径|路程|距离)'

def graph_route_evidence(text):
    def matches(pattern):
        return [{'quote':m[0],'start':m.start(),'end':m.end()} for m in re.finditer(pattern,text,re.I)]
    named=matches(NAMED);structure=matches(STRUCTURE)
    goals=matches(FLOW_GOAL)+matches(COST_GOAL)+matches(PATH_GOAL)
    families=matches(FAMILIES)
    candidate=bool(named or structure and goals)
    return {'version':'graph_route_evidence_v1','selected':candidate and not families,
            'reason':'other_family_present' if families else 'named_graph_task' if named else 'graph_structure_and_goal' if candidate else 'insufficient_graph_evidence',
            'named_tasks':named,'structure':structure,'objectives':goals,'other_families':families,
            'scope':'选择请求契约，不判断支持范围；否定/背景目标交模型结合全文判断，混合题型保留完整Schema'}
