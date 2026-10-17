"""Independent original-graph oracle, separate from runtime solver."""
import itertools

CASES={
    'shortest_path':{('S','A'):4,('S','B'):2,('B','A'):1,('A','C'):2,('B','C'):5,('C','T'):3,('A','T'):7},
    'max_flow':{('S','A'):10,('S','B'):5,('A','B'):4,('A','T'):6,('B','T'):9},
}


def evaluate_run(record,case):
    edges=CASES[case];nodes={n for edge in edges for n in edge}
    m=record['envelope']['model'];r=record['stages'][0]['result']
    generated={(e['source'],e['target']):e['weight'] for e in m['edges']}
    checks={'original_graph':m['problem']==case and m['source']=='S' and m['target']=='T' and set(m['nodes'])==nodes and generated==edges and len(m['edges'])==len(edges)}
    if case=='shortest_path':
        candidates=[]
        def visit(u,seen,cost):
            if u=='T':candidates.append(cost);return
            for (a,b),w in edges.items():
                if a==u and b not in seen:visit(b,seen|{b},cost+w)
        visit('S',{'S'},0)
        path=r['path'];pairs=list(zip(path,path[1:]))
        checks['valid_path']=bool(path) and path[0]=='S' and path[-1]=='T' and all(e in edges for e in pairs)
        cost=sum(edges.get(e,float('inf')) for e in pairs)
        checks['optimal_distance']=cost==min(candidates) and r['value']==cost
    else:
        internal=sorted(nodes-{'S','T'});cut_costs=[]
        for bits in itertools.product((False,True),repeat=len(internal)):
            side={'S'}|{u for u,b in zip(internal,bits) if b}
            cut_costs.append(sum(c for (u,v),c in edges.items() if u in side and v not in side))
        flows={(e['source'],e['target']):e['flow'] for e in r['flows']}
        checks['original_capacities']=set(flows)==set(edges) and len(r['flows'])==len(edges) and all(0<=f<=edges[e] for e,f in flows.items())
        balance={u:sum(f for (a,b),f in flows.items() if a==u)-sum(f for (a,b),f in flows.items() if b==u) for u in nodes}
        checks['conservation']=all(balance[u]==0 for u in internal) and balance['S']==r['value'] and balance['T']==-r['value']
        checks['optimal_value']=r['value']==min(cut_costs)
    return {'passed':all(checks.values()),'checks':checks,'scope':'固定开发原题；独立枚举简单路径/所有源汇割，不用于其他图或成功率结论'}
