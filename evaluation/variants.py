"""Frozen development variants, two rounds; no adaptive prompt changes."""
import argparse
import hashlib
import json
import platform
import time
import uuid
from collections import Counter,defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from .batch import run_case,write_json
from .development import CASES,ROOT,reference,score
from assistant.config import credentials

BASE={c['id']:c for c in CASES}


def cases():
    result=[dict(c,base_id=c['id'],kind='original',expected_envelopes=['ready'],expected_status='normal') for c in CASES]
    for v in json.loads((ROOT/'examples/development_variants/manifest.json').read_text()):
        c=dict(BASE[v['base_id']]);c.pop('data',None);c.update(v);result.append(c)
    return result


def infeasible_score(case,record):
    expected=reference(BASE[case['base_id']]);m=record['envelope']['model']
    if case['base_id']=='OPT01':
        expected['constraints'].append(dict(name='order',terms=[dict(variable='A',coefficient=1)],sense='>=',rhs=60,unit='件'))
    else:
        for c in expected['constraints']:
            if c['rhs']==40:c['rhs']=30
    actual_cost={t['coefficient']:t['variable'] for t in m['objective']['terms']}
    expected_cost={t['coefficient']:t['variable'] for t in expected['objective']['terms']}
    if set(actual_cost)!=set(expected_cost) or len(actual_cost)!=len(m['variables']):return {'passed':False,'reason':'原题目标或变量无法对齐'}
    mapping={actual_cost[k]:v for k,v in expected_cost.items()}
    identity={v['name']:v['name'] for v in expected['variables']}
    def canonical(model,rename):
        out=[]
        def add(terms,sense,rhs):
            terms=sorted((rename[t['variable']],t['coefficient']) for t in terms if t['coefficient']!=0)
            scale=abs(terms[0][1]) if terms else 1
            out.append((tuple((n,round(a/scale,10)) for n,a in terms),sense,round(rhs/scale,10)))
        for c in model['constraints']:add(c['terms'],c['sense'],c['rhs'])
        for v in model['variables']:
            add([dict(variable=v['name'],coefficient=1)],'>=',v['lower'])
            # Always include nonnegativity even if a stronger bound was provided.
            if v['lower']>0:add([dict(variable=v['name'],coefficient=1)],'>=',0)
            if v['upper'] is not None:add([dict(variable=v['name'],coefficient=1)],'<=',v['upper'])
        return sorted(set(out))
    domains=sorted((mapping[v['name']],v['kind']) for v in m['variables'])==sorted((v['name'],v['kind']) for v in expected['variables'])
    checks={'conditions_preserved':canonical(m,mapping)==canonical(expected,identity),'domains':domains,
            'objective_sense':m['objective']['sense']==expected['objective']['sense'],
            'infeasible':record['stages'][0]['result']['status']=='infeasible'}
    return {'passed':all(checks.values()),'checks':checks,'independent_reason':'A至少60件需至少120小时，超过100小时' if case['base_id']=='OPT01' else '总供给60吨小于硬需求70吨'}


def variant_score(case,record,path):
    if case.get('expected_status')=='infeasible':return infeasible_score(case,record)
    return score(BASE[case['base_id']],record,path)


def summary(directory,rows,planned):
    import csv
    write_json(directory/'results.json',rows)
    fields=['id','base_id','kind','repeat','outcome','failure_category','detail','elapsed_seconds','total_tokens','response_model','run_path']
    with (directory/'results.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows({k:r.get(k) for k in fields} for r in rows)
    bykind=defaultdict(list);bycase=defaultdict(list)
    for r in rows:bykind[r['kind']].append(r);bycase[r['id']].append(r)
    stability=[]
    for id,rs in bycase.items():
        complete=len(rs)==2;states=[r['outcome'] for r in rs]
        label='pending' if not complete else 'both_pass' if all(s=='pass' for s in states) else 'both_fail' if all(s=='fail' for s in states) else 'mixed'
        stability.append(dict(id=id,classification=label,outcomes=states,failure_categories=[r['failure_category'] for r in rs]))
    write_json(directory/'stability.json',stability)
    tokens=sum(r['total_tokens'] for r in rows if r['total_tokens'] is not None)
    lines=['# 开发变体两次重复评测','',f"完成{len(rows)}/{planned}；通过{sum(r['outcome']=='pass' for r in rows)}/{len(rows)}；已知tokens {tokens}；未知usage {sum(r['total_tokens'] is None for r in rows)}。",'固定题面/规则，不重试、不修复。两次是两个独立请求；API默认采样，无独立性或长期稳定性保证。','','| 类型 | 通过 | 总数 |','|---|---:|---:|']
    for kind,rs in bykind.items():lines.append(f"| {kind} | {sum(r['outcome']=='pass' for r in rs)} | {len(rs)} |")
    lines+=['','## 两次一致性','',str(dict(Counter(s['classification'] for s in stability))), '', 'mixed表示同题一次通过一次失败；both_fail表示重复出现的缺陷，不代表稳定正确。仅比较验收结果，措辞差异或不同等价最优解不算失败。','', '## 自动判定失败','']
    for r in rows:
        if r['outcome']!='pass':lines.append(f"- {r['id']} / 第{r['repeat']}次：{r['failure_category']}；{r['detail']}")
    lines+=['','预期追问只按状态和关键词初筛，仍须审查问题是否相关且未擅自补值。结构评分可能拒绝等价重写；评分器异常单列，不算模型错误。全部属于开发题变体，不计新增基础题或保留测试。']
    (directory/'summary.md').write_text('\n'.join(lines)+'\n')


def main(argv=None):
    p=argparse.ArgumentParser(description='8原题+24变体，各2次，最多64次API调用；无重试')
    p.add_argument('--backend',choices=['deepseek','openai'],default='deepseek');p.add_argument('--llm-model')
    p.add_argument('--output',type=Path,default=ROOT/'outputs/variant_batches');args=p.parse_args(argv)
    key,name=credentials(args.llm_model,args.backend)
    if not key:p.error('请先配置API')
    items=cases();directory=args.output/(datetime.now(ZoneInfo('Asia/Shanghai')).strftime('%Y%m%d_%H%M%S')+'_'+uuid.uuid4().hex[:8]);directory.mkdir(parents=True)
    paths={'examples/development_variants/manifest.json','examples/production/problem.txt','requirements.lock'}
    for c in items:
        for k in ('problem','data','reference'):
            if c.get(k):paths.add(c[k])
    paths.update(str(f.relative_to(ROOT)) for group in ('evaluation','assistant','tests') for f in (ROOT/group).glob('*.py'))
    hashes={}
    for namepath in sorted(paths):
        data=(ROOT/namepath).read_bytes();hashes[namepath]=hashlib.sha256(data).hexdigest();dest=directory/'snapshot'/namepath;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
    write_json(directory/'manifest.json',dict(protocol='development_variants_v1',cases=items,repeats=2,max_calls=64,retries=0,repair_rounds=0,requested_model=name,backend=args.backend,hashes=hashes,python=platform.python_version(),order='round1 all 32 then round2 all 32'))
    print('批次：'+str(directory.resolve()),flush=True);rows=[]
    for repeat in (1,2):
        rounddir=directory/f'round_{repeat}';rounddir.mkdir()
        for c in items:
            row=run_case(c,rounddir,args.backend,name,score_fn=variant_score)
            row.update(base_id=c['base_id'],kind=c['kind'],repeat=repeat)
            if row['run_path']:row['run_path']=f'round_{repeat}/'+row['run_path']
            rows.append(row);summary(directory,rows,64)
            print(f"{repeat} {c['id']}: {row['outcome']} {row['failure_category']}",flush=True)
    return 0 if all(r['outcome']=='pass' for r in rows) else 1

if __name__=='__main__':raise SystemExit(main())
