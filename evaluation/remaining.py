"""Frozen targeted regression for graph quotes and permission-before-change."""
import argparse
import hashlib
import json
import re
import uuid
from collections import Counter
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from assistant import __version__
from assistant.config import credentials
from .batch import run_case,write_json
from .development import ROOT
from .full import classify,check_quote_repair,apply_question_checks
from .graph_units import provenance_checks,score_path_units,score_boundary
from .graphs import evaluate_run
from .capacity import score as capacity_score, question_score
from .clarification import locked_question_score


def cases():
    return json.loads((ROOT/'examples/remaining_failure/manifest.json').read_text())


def score(case,record,path):
    if case['check']=='valid':return capacity_score(case,record,path)
    if case['check']=='path':return score_path_units(dict(case,id='path_units'),record,path)
    if case['check']=='mixed_flow':
        fixture=next(c for c in json.loads((ROOT/'examples/graph_unit/manifest.json').read_text()) if c['id']=='graph_units_flow_mixed')
        return score_boundary(fixture,record,path)
    numeric=evaluate_run(record,'max_flow');audit=provenance_checks(record)
    m=record['envelope']['model']
    unit=m['unit'] in ('立方米/小时','m3/hour','m³/h','m3/h')
    return {'passed':numeric['passed'] and unit and all(audit.values()),'numeric':numeric,'unit':unit,'provenance':audit}


def check_response(case,envelope,folder):
    kind=case['check'];q='；'.join(envelope['questions']);checks={'expected_status':envelope['status'] in case['expected_envelopes']}
    if kind in ('permission','missing'):
        checks.update(question_score(envelope)['checks'])
        if kind=='permission':
            checks['requests_user_input']=bool(re.search(r'请|是否|能否',q)) and bool(re.search(r'确认|提供|同意|允许',q))
            checks['no_automatic_replacement']=not bool(re.search(r'默认|已(?:经)?(?:改|调整|设)|取绝对值',q))
    elif kind=='locked':checks['locked']=locked_question_score(envelope)['passed']
    elif kind=='conflict':
        tempcase=dict(case,kind='conflict',question_keywords=['K','容量'])
        row={'outcome':'pass'};audit=apply_question_checks(tempcase,row,folder)
        checks['neutral_conflict']=audit.get('passed',False)
    elif kind=='unsupported':checks['explains_scope']=bool(re.search(r'阈值|到达|支持|范围',q))
    return {'passed':all(checks.values()),'checks':checks,'scope':'预先固定的部分语义检查，仍需定性复核'}


def summarize(directory,rows,total):
    import csv
    write_json(directory/'results.json',rows)
    fields=['id','repeat','original_pass','after_format_pass','final_pass','pass_path','raw_schema_valid','format_action','source_quote_repaired','local_guard_used','false_guard','failure_category','detail','total_tokens','run_path']
    with (directory/'results.csv').open('w',newline='',encoding='utf-8-sig') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows({k:r.get(k) for k in fields} for r in rows)
    counts=[sum(r[k] for r in rows) for k in ('original_pass','after_format_pass','final_pass')]
    lines=['# 图引用与修改许可定向回归','',f'完成{len(rows)}/{total}；原始{counts[0]}；格式后累计{counts[1]}；本地后累计{counts[2]}。',f"路径计数：{dict(Counter(r['pass_path'] for r in rows))}。",f"tokens {sum(r['total_tokens'] or 0 for r in rows)}；usage未知{sum(r['total_tokens'] is None for r in rows)}；对照误接管{sum(r['false_guard'] for r in rows)}。",'', '| 场景 | 完成次数 | 原始 | 格式后累计 | 本地后累计 |','|---|---:|---:|---:|---:|']
    for case in cases():
        rs=[r for r in rows if r['id']==case['id']]
        lines.append('| '+case['id']+' | '+str(len(rs))+' | '+' | '.join(str(sum(r[k] for r in rs)) for k in ('original_pass','after_format_pass','final_pass'))+' |')
    lines+=['','每场景3次、无重试、批次中不改代码；开发变体不代表独立题族或稳定率。正常换算不算修复；引用修复计local_source_repair；响应接管计local_guard；三层为累计口径，不可相加。','', '## 非原始通过记录']
    lines += [f"- {r['id']} #{r['repeat']}：{r['pass_path']} {r['failure_category']} {r['detail']}" for r in rows if not r['original_pass']]
    (directory/'summary.md').write_text('\n'.join(lines)+'\n')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=ROOT/'outputs/remaining_regressions');args=parser.parse_args()
    key,model=credentials(None,'deepseek')
    if not key:raise ValueError('请先配置DeepSeek')
    items=cases();directory=args.output/(datetime.now(ZoneInfo('Asia/Shanghai')).strftime('%Y%m%d_%H%M%S')+'_'+uuid.uuid4().hex[:8]);directory.mkdir(parents=True)
    paths={Path('protocols/remaining_v1.md'),Path('examples/remaining_failure/manifest.json'),Path('examples/graph_unit/manifest.json'),Path('requirements.lock')}
    paths.update(Path(c['problem']) for c in items)
    for group in ('evaluation','assistant','tests'):paths.update(p.relative_to(ROOT) for p in (ROOT/group).glob('*.py'))
    # Offline history replay tests reference these immutable evidence files.
    old=Path('outputs/full_regressions/20261016_215628_fad2b50a')
    paths.update([old/'NET02_paraphrase/api.json',old/'immutable_permission/generation_record.json'])
    hashes={}
    for rel in sorted(paths):
        data=(ROOT/rel).read_bytes();hashes[str(rel)]=hashlib.sha256(data).hexdigest();dest=directory/'snapshot'/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
    write_json(directory/'manifest.json',dict(version=__version__,protocol='remaining_failures_v1',model=model,cases=items,repeats=3,retries=0,max_calls=len(items)*3,hashes=hashes))
    print(directory,flush=True);rows=[]
    for repeat in range(1,4):
        rd=directory/f'round_{repeat}';rd.mkdir()
        for case in items:
            row=run_case(case,rd,'deepseek',model,score_fn=score);folder=rd/case['id']
            api=folder/'api.json';metadata=json.loads(api.read_text()) if api.exists() else {}
            quote=check_quote_repair(case,metadata,folder)
            if quote.get('passed') is False:row.update(outcome='fail',failure_category='quote_audit_failed')
            gen=folder/'generation_record.json'
            if gen.exists():
                audit=check_response(case,json.loads(gen.read_text())['envelope'],folder);write_json(folder/'response_evaluation.json',audit)
                if not audit['passed']:row.update(outcome='fail',failure_category='response_semantics',detail=json.dumps(audit,ensure_ascii=False))
            permission_guard=metadata.get('local_validation',{}).get('reason')=='明确允许改值但须先询问，非法容量必须等待用户确认'
            false_guard=permission_guard and case['check']!='permission'
            if false_guard:row.update(outcome='fail',failure_category='false_permission_guard')
            row.update(repeat=repeat,false_guard=false_guard,quote_audit_passed=quote.get('passed'),**classify(row,metadata))
            if row['run_path']:row['run_path']=f'round_{repeat}/'+row['run_path']
            rows.append(row);summarize(directory,rows,len(items)*3)
            print(repeat,case['id'],row['pass_path'],row['failure_category'],flush=True)
    return 0 if all(r['final_pass'] for r in rows) else 1

if __name__=='__main__':raise SystemExit(main())
