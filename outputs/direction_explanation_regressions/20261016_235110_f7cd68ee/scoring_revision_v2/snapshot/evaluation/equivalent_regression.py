"""Capacity conflict priority and negative controls, 3 repeats."""
import argparse
import json
import hashlib
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo
from modeling_assistant import __version__
from modeling_assistant.config import credentials
from .development import ROOT
from .batch import run_case, write_json
from .capacity_regression import score, question_score
from .clarification import locked_question_score
from .full_regression import classify
from modeling_assistant.dimension_policy import wrong_rate_capacity_comparison


def cases():
    return json.loads((ROOT/'examples/equivalent_boundaries/manifest.json').read_text())


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--case',nargs='+',choices=[c['id'] for c in cases()]);args=parser.parse_args()
    key,model=credentials(None,'deepseek')
    if not key:raise ValueError('请先配置DeepSeek')
    items=[c for c in cases() if not args.case or c['id'] in args.case];total=len(items)*3
    directory=ROOT/'outputs/equivalent_regressions'/(datetime.now(ZoneInfo('Asia/Shanghai')).strftime('%Y%m%d_%H%M%S')+'_'+uuid.uuid4().hex[:8]);directory.mkdir(parents=True)
    files=[f for group in ('modeling_assistant','evaluation','tests') for f in (ROOT/group).glob('*.py')]+list((ROOT/'examples/equivalent_boundaries').glob('*'))
    hashes={}
    for f in files:
        rel=f.relative_to(ROOT);data=f.read_bytes();hashes[str(rel)]=hashlib.sha256(data).hexdigest();dest=directory/'snapshot'/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
    write_json(directory/'manifest.json',dict(version=__version__,model=model,cases=items,repeats=3,max_calls=total,retries=0,hashes=hashes))
    print(directory,flush=True);rows=[]
    for repeat in range(1,4):
        rd=directory/f'round_{repeat}';rd.mkdir()
        for case in items:
            row=run_case(case,rd,'deepseek',model,score_fn=score);folder=rd/case['id']
            meta=json.loads((folder/'api.json').read_text()) if (folder/'api.json').exists() else {}
            guard=meta.get('local_validation',{})
            takeover=guard.get('reason')=='容量原文记录冲突，先澄清再校验参数域'
            false_stop=takeover and not case['conflict_values']
            gen=folder/'generation_record.json';audit={'false_interception':false_stop}
            if gen.exists():
                e=json.loads(gen.read_text())['envelope']
                if case['conflict_values']:
                    import re
                    question='；'.join(e['questions'])
                    numbers={float(n) for n in re.findall(r'[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?',question)}
                    checks={'clarification':e['status']=='needs_clarification','all_original_values':set(case['conflict_values'])<=numbers,
                            'conflict_explained':bool(re.search(r'冲突|矛盾|不一致',question)),
                            'asks_resolution':bool(re.search(r'确认|核对|澄清|哪|提供',question)),
                            'no_preselected_value':not bool(re.search(r'建议.{0,8}(?:采用|取|改)|默认|已选|取绝对值|正实数|正数|正值|有效.{0,4}(?:值|容量)|K\s*>\s*0|大于0|必须为正|除零',question)),
                            'no_execution':not json.loads(gen.read_text())['stages']}
                    audit.update(passed=all(checks.values()),checks=checks,text=question)
                elif case['id']=='same_invalid':audit.update(locked_question_score(e))
                elif case['id'] in ('missing','missing_mixed','missing_rate'):
                    audit.update(passed=not any(wrong_rate_capacity_comparison(q) for q in e['questions']))
            if false_stop or audit.get('passed') is False:
                row.update(outcome='fail',failure_category='policy_semantics',detail=json.dumps(audit,ensure_ascii=False))
            write_json(folder/'policy_evaluation.json',audit)
            row.update(repeat=repeat,parameter_takeover=takeover,false_interception=false_stop,**classify(row,meta))
            if row['run_path']:row['run_path']=f'round_{repeat}/'+row['run_path']
            rows.append(row);write_json(directory/'results.json',rows)
            print(repeat,case['id'],row['pass_path'],'false_stop='+str(false_stop),flush=True)
    stability={c['id']:sum(r['final_pass'] for r in rows if r['id']==c['id']) for c in items}
    write_json(directory/'stability.json',stability)
    lines=['# 容量数值等价写法重复评测','',f"原始通过{sum(r['original_pass'] for r in rows)}/{total}；格式修复后累计{sum(r['after_format_pass'] for r in rows)}/{total}；含本地处理最终{sum(r['final_pass'] for r in rows)}/{total}。",f"容量冲突策略误拦截{sum(r['false_interception'] for r in rows)}；策略接管{sum(r['parameter_takeover'] for r in rows)}。",f"tokens {sum(r['total_tokens'] or 0 for r in rows)}；usage未知{sum(r['total_tokens'] is None for r in rows)}。",'', '| 场景 | 通过次数 |','|---|---:|']
    lines += [f'| {name} | {n}/3 |' for name,n in stability.items()]
    lines += ['','原始通过不含格式修复、本地引用修复或本地接管。引用修复以source_quote_repaired另列，pass_path为local_source_repair。有效输入不必要追问仍判失败，不能与本地误拦截混淆。每场景3次开发测试不证明长期稳定；原始回答和失败不重试覆盖。']
    (directory/'summary.md').write_text('\n'.join(lines)+'\n')
    return 0 if all(r['final_pass'] for r in rows) else 1

if __name__=='__main__':raise SystemExit(main())
