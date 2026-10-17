"""Nonnegative shortest paths and integral maximum flows with certificates."""
import csv
import heapq
from collections import deque
from .model import validate_model


def solve_graph(model):
    validate_model(model)
    nodes, source, target = model['nodes'],model['source'],model['target']
    weights={(e['source'],e['target']):e['weight'] for e in model['edges']}
    adjacency={u:[] for u in nodes}
    for u,v in weights: adjacency[u].append(v)
    if model['problem']=='shortest_path':
        distance={source:0};previous={};queue=[(0,source)]
        while queue:
            cost,u=heapq.heappop(queue)
            if cost!=distance[u]:continue
            for v in adjacency[u]:
                new=cost+weights[u,v]
                if v not in distance or new<distance[v]:
                    distance[v]=new;previous[v]=u;heapq.heappush(queue,(new,v))
        path=[]
        if target in distance:
            path=[target]
            while path[-1]!=source:path.append(previous[path[-1]])
            path.reverse()
        # Reachable-set closure certifies unreachability; distance labels certify a lower bound.
        closed=all(v in distance for u,v in weights if u in distance)
        inequalities=all(distance[v]<=distance[u]+w+1e-8 for (u,v),w in weights.items() if u in distance)
        path_cost=sum(weights[u,v] for u,v in zip(path,path[1:])) if path else None
        checks={'reachable_set_closed':closed,'distance_inequalities':inequalities,
                'path_matches_distance':not path or abs(path_cost-distance[target])<1e-8}
        return {'status':'optimal' if path else 'unreachable','value':path_cost,'path':path,
                'distances':{u:distance.get(u) for u in nodes},'reachable':sorted(distance),
                'verification':{'passed':all(checks.values()),'checks':checks}}
    capacity={(u,v):int(w) for (u,v),w in weights.items()}
    residual=dict(capacity)
    for u,v in capacity:
        residual.setdefault((v,u),0)
        if u not in adjacency[v]:adjacency[v].append(u)
    value=0
    while True:
        previous={source:None};queue=deque([source])
        while queue and target not in previous:
            u=queue.popleft()
            for v in adjacency[u]:
                if v not in previous and residual[u,v]>0:
                    previous[v]=u;queue.append(v)
        if target not in previous:break
        v=target;amount=None
        while v!=source:
            u=previous[v];amount=residual[u,v] if amount is None else min(amount,residual[u,v]);v=u
        v=target
        while v!=source:
            u=previous[v];residual[u,v]-=amount;residual[v,u]+=amount;v=u
        value+=amount
    reachable=set(previous)
    # Opposing original edges use a cancellation-equivalent nonnegative flow.
    flows=[{'source':u,'target':v,'capacity':c,'flow':max(0,c-residual[u,v])} for (u,v),c in capacity.items()]
    balance={u:0 for u in nodes}
    for e in flows:balance[e['source']]+=e['flow'];balance[e['target']]-=e['flow']
    cut=[e for e in flows if e['source'] in reachable and e['target'] not in reachable]
    cut_capacity=sum(e['capacity'] for e in cut)
    checks={'capacity_bounds':all(0<=e['flow']<=e['capacity'] for e in flows),
            'conservation':all(balance[u]==0 for u in nodes if u not in (source,target)),
            'source_target_balance':balance[source]==value and balance[target]==-value,
            'flow_equals_cut':value==cut_capacity,'cut_separates':source in reachable and target not in reachable}
    return {'status':'optimal','value':value,'flows':flows,'cut':{'source_side':sorted(reachable),
            'target_side':sorted(set(nodes)-reachable),'edges':cut,'capacity':cut_capacity},
            'verification':{'passed':all(checks.values()),'checks':checks}}


def report_graph(record):
    m=record['envelope']['model']
    lines=['# 图与网络求解报告','',m['name'],'',f"任务：{m['problem']}；起点：{m['source']}；终点：{m['target']}；单位：{m['unit']}。",'所有边按有向边解释；双向道路须在模型中列出两个方向。','假设：'+'；'.join(m['assumptions']),'','| 起点 | 终点 | 距离或容量 |','|---|---|---:|']
    lines += [f"| {e['source']} | {e['target']} | {e['weight']} |" for e in m['edges']]
    conversion = record.get('generation', {}).get('unit_conversion')
    if conversion:
        lines += ['', '## 原始边权与程序换算', '', '| 边 | 原值 | 原单位 | 因子 | 统一值 |', '|---|---:|---|---|---:|']
        lines += [f"| {e['source']} → {e['target']} | {e['original_weight']} | {e['original_unit']} | {e['factor']} | {e['normalized_weight']} |" for e in conversion['edges']]
        lines += ['', '原始引用见source_model.json，逐边换算见unit_conversion.json。引用核对不等于完整语义验证。']
    if not record['stages']:return '\n'.join(lines+['','仅生成模型，尚未求解。'])+'\n'
    r=record['stages'][0]['result'];lines += ['',f"状态：{r['status']}；结果：{r['value']} {m['unit']}。"]
    if m['problem']=='shortest_path':
        lines += ['路径：'+' → '.join(r['path']) if r['path'] else '终点不可达。', '距离标签（null为不可达）：'+str(r['distances'])]
    else:
        lines += ['最小割源侧：'+', '.join(r['cut']['source_side']),f"最小割容量：{r['cut']['capacity']}，与最大流相等。",'各边流量见 edges.csv。']
    lines += ['','验证：'+str(r['verification']),'','证据只针对生成的图；仍须对照原题核对方向、缺边、权重与单位。当前不支持负权、平行边、多商品流或成本流。']
    return '\n'.join(lines)+'\n'


def save_edges(record,directory):
    m=record['envelope']['model']
    rows=m['edges']
    if record['stages'] and m['problem']=='max_flow':rows=record['stages'][0]['result']['flows']
    fields=['source','target','capacity','flow'] if rows and 'flow' in rows[0] else ['source','target','weight']
    with (directory/'edges.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
