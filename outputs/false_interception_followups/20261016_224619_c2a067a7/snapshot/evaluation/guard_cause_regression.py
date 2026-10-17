"""One frozen targeted experiment: priority fixes, with all post-response guards retained."""
import argparse
import hashlib
import json
import re
import uuid
from collections import Counter
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from modeling_assistant import __version__
from modeling_assistant.config import credentials
from .batch import run_case,write_json
from .development import ROOT
from .full_regression import score as full_score,apply_question_checks,check_quote_repair,classify
from .graph_units import provenance_checks


def cases():
    return json.loads((ROOT/'examples/guard_cause_boundaries/manifest.json').read_text())


def score(case,record,path):
    if case['kind']!='guard_control':return full_score(case,record,path)
    m=record['envelope']['model'];r=record['stages'][0]['result'];source=record['generation'].get('source_model',{})
    aliases={'升/小时':{'升/小时','L/hour','L/h'},'立方米/小时':{'立方米/小时','m3/hour','m³/h','m3/h'}}
    checks=provenance_checks(record)
    checks.update(problem=m['problem']=='max_flow',nodes=set(m['nodes'])=={'S','T'},source_target=m['source']=='S' and m['target']=='T',
                  unit=m['unit'] in aliases[case['unit']],edges=m['edges']==[{'source':'S','target':'T','weight':1}],
                  original_edges=[(e['source'],e['target'],e['weight'],e['unit']) for e in source.get('edges',[])]==[('S','T',case['original_value'],'升/小时')],
                  flow=r['value']==1 and r['flows']==[{'source':'S','target':'T','capacity':1,'flow':1}])
    return {'passed':all(checks.values()),'checks':checks}


def flow_refusal_check(envelope):
    text='；'.join(envelope['questions'])
    positive=re.sub(r'(?:不得|禁止|不能|不允许|不会|不应)[^，。；？?]{0,15}(?:改|取整|舍入)[^，。；？?]*','',text)
    checks={'nonready':envelope['status'] in ('needs_clarification','unsupported'),
            'integer_limitation':'整数' in text and bool(re.search(r'换算|转换|单位',text)),
            'no_forbidden_change':not bool(re.search(r'建议.{0,15}(?:改|取整)|(?:是否|请).{0,15}(?:改.{0,8}单位|取整)|四舍五入后',positive))}
    return {'passed':all(checks.values()),'checks':checks}


def summarize(directory,rows):
    import csv
    write_json(directory/'results.json',rows)
    fields=['id','group','repeat','original_pass','after_format_pass','final_pass','pass_path','generation_route','raw_schema_valid','format_action','source_quote_repaired','local_guard_used','failure_category','detail','total_tokens','run_path']
    with (directory/'results.csv').open('w',newline='',encoding='utf-8-sig') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows({k:r.get(k) for k in fields} for r in rows)
    sums=[sum(r[k] for r in rows) for k in ('original_pass','after_format_pass','final_pass')]
    lines=['# 本地策略共因修复定向回归','',f'完成{len(rows)}/{len(cases())*3}；原始{sums[0]}；格式后累计{sums[1]}；本地后累计{sums[2]}。',f"路径计数：{dict(Counter(r['pass_path'] for r in rows))}；tokens {sum(r['total_tokens'] or 0 for r in rows)}；usage未知{sum(r['total_tokens'] is None for r in rows)}。",'','原始通过仍包含生成前本地参数提取与分流提示，排除生成后的格式修复、引用修复和本地接管。不能据此声称裸模型能力提升。护栏保留，三层计数累计不可相加。','', '| 场景 | 分组 | 次数 | 原始 | 格式后累计 | 本地后累计 |','|---|---|---:|---:|---:|---:|']
    for c in cases():
        rs=[r for r in rows if r['id']==c['id']]
        lines.append(f"| {c['id']} | {c['group']} | {len(rs)} | "+' | '.join(str(sum(r[k] for r in rs)) for k in ('original_pass','after_format_pass','final_pass'))+' |')
    lines+=['','## 非原始通过']
    lines += [f"- {r['id']} #{r['repeat']}：{r['pass_path']} {r['failure_category']} {r['detail']}" for r in rows if not r['original_pass']]
    lines+=['','19开发场景各3次，不重试、不在批次中改代码；不代表独立题族或长期稳定率，不与历史单轮101场景合并统计。旧响应离线重放单列零API。']
    (directory/'summary.md').write_text('\n'.join(lines)+'\n')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=ROOT/'outputs/guard_cause_regressions');args=parser.parse_args()
    key,model=credentials(None,'deepseek')
    if not key:raise ValueError('请先配置DeepSeek')
    items=cases();directory=args.output/(datetime.now(ZoneInfo('Asia/Shanghai')).strftime('%Y%m%d_%H%M%S')+'_'+uuid.uuid4().hex[:8]);directory.mkdir(parents=True)
    paths={Path('task_cards/guard_cause_regression_protocol_v1.md'),Path('requirements-assistant-lock.txt')}
    for group in ('modeling_assistant','evaluation','tests'):paths.update(p.relative_to(ROOT) for p in (ROOT/group).glob('*.py'))
    paths.update(p.relative_to(ROOT) for p in (ROOT/'examples').rglob('*') if p.is_file())
    prior=Path('outputs/full_regressions/20261016_221715_01b77856')
    for c in items:
        if c['group']=='historical_guard':paths.update([prior/c['id']/'api.json',prior/c['id']/'generation_record.json'])
    paths.update([Path('outputs/full_regressions/20261016_215628_fad2b50a/NET02_paraphrase/api.json'),Path('outputs/full_regressions/20261016_215628_fad2b50a/immutable_permission/generation_record.json'),Path('outputs/remaining_regressions/20261016_220901_3d78eab4/round_1/permission_missing/generation_record.json')])
    hashes={}
    for rel in sorted(paths):
        data=(ROOT/rel).read_bytes();hashes[str(rel)]=hashlib.sha256(data).hexdigest();dest=directory/'snapshot'/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
    write_json(directory/'manifest.json',dict(version=__version__,protocol='guard_causes_v1',model=model,cases=items,repeats=3,max_calls=len(items)*3,retries=0,hashes=hashes))
    print(directory,flush=True);rows=[]
    for repeat in range(1,4):
        rd=directory/f'round_{repeat}';rd.mkdir()
        for c in items:
            row=run_case(c,rd,'deepseek',model,score_fn=score);folder=rd/c['id']
            qa=apply_question_checks(c,row,folder)
            api=folder/'api.json';meta=json.loads(api.read_text()) if api.exists() else {}
            quote=check_quote_repair(c,meta,folder)
            if quote.get('passed') is False:row.update(outcome='fail',failure_category='quote_audit_failed')
            if c['id']=='graph_units_fractional_flow' and (folder/'generation_record.json').exists():
                fa=flow_refusal_check(json.loads((folder/'generation_record.json').read_text())['envelope']);write_json(folder/'flow_refusal_evaluation.json',fa)
                if not fa['passed']:row.update(outcome='fail',failure_category='flow_refusal_semantics',detail=json.dumps(fa,ensure_ascii=False))
            row.update(group=c['group'],repeat=repeat,generation_route=meta.get('generation_policy_context',{}).get('route'),question_semantics_passed=qa.get('passed'),quote_audit_passed=quote.get('passed'),**classify(row,meta))
            if row['run_path']:row['run_path']=f'round_{repeat}/'+row['run_path']
            rows.append(row);summarize(directory,rows)
            print(repeat,c['id'],row['pass_path'],row['failure_category'],flush=True)
    return 0 if all(r['final_pass'] for r in rows) else 1

if __name__=='__main__':raise SystemExit(main())
