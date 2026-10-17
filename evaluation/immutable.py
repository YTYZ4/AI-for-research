"""Immutable-parameter paraphrases and takeover negative controls, 3 repeats."""
import argparse
import json
import hashlib
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo
from assistant import __version__
from assistant.config import credentials
from .development import ROOT
from .batch import run_case, write_json
from .capacity import score, question_score
from .clarification import locked_question_score
from .full import classify


def cases():
    return json.loads((ROOT/'examples/immutable/manifest.json').read_text())


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--case',nargs='+',choices=[c['id'] for c in cases()]);args=parser.parse_args()
    key,model=credentials(None,'deepseek')
    if not key:raise ValueError('请先配置DeepSeek')
    items=[c for c in cases() if not args.case or c['id'] in args.case];total=len(items)*3
    directory=ROOT/'outputs/immutable_regressions'/(datetime.now(ZoneInfo('Asia/Shanghai')).strftime('%Y%m%d_%H%M%S')+'_'+uuid.uuid4().hex[:8]);directory.mkdir(parents=True)
    files=[f for group in ('assistant','evaluation','tests') for f in (ROOT/group).glob('*.py')]+list((ROOT/'examples/immutable').glob('*'))
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
            takeover=guard.get('reason')=='原文禁止改值且本地原参数域检查失败'
            false_stop=takeover and not case['guard_allowed']
            gen=folder/'generation_record.json';audit={'false_interception':false_stop}
            if gen.exists():
                e=json.loads(gen.read_text())['envelope']
                if case['guard_allowed']:
                    audit.update(locked_question_score(e))
                elif case['id']=='permission':audit.update(question_score(e))
            if false_stop or audit.get('passed') is False:
                row.update(outcome='fail',failure_category='policy_semantics',detail=json.dumps(audit,ensure_ascii=False))
            write_json(folder/'policy_evaluation.json',audit)
            row.update(repeat=repeat,parameter_takeover=takeover,false_interception=false_stop,**classify(row,meta))
            if row['run_path']:row['run_path']=f'round_{repeat}/'+row['run_path']
            rows.append(row);write_json(directory/'results.json',rows)
            print(repeat,case['id'],row['pass_path'],'false_stop='+str(false_stop),flush=True)
    stability={c['id']:sum(r['final_pass'] for r in rows if r['id']==c['id']) for c in items}
    write_json(directory/'stability.json',stability)
    lines=['# 禁止改值同义表达与误拦截重复评测','',f"原始通过{sum(r['original_pass'] for r in rows)}/{total}；格式修复后累计{sum(r['after_format_pass'] for r in rows)}/{total}；含本地处理最终{sum(r['final_pass'] for r in rows)}/{total}。",f"禁止改值策略误拦截{sum(r['false_interception'] for r in rows)}；策略接管{sum(r['parameter_takeover'] for r in rows)}。",f"tokens {sum(r['total_tokens'] or 0 for r in rows)}；usage未知{sum(r['total_tokens'] is None for r in rows)}。",'', '| 场景 | 通过次数 |','|---|---:|']
    lines += [f'| {name} | {n}/3 |' for name,n in stability.items()]
    lines += ['','原始通过不含格式修复或本地接管。有效输入不必要追问仍判失败，不能与本地误拦截混淆。每场景3次开发测试不证明长期稳定；原始回答和失败不重试覆盖。']
    (directory/'summary.md').write_text('\n'.join(lines)+'\n')
    return 0 if all(r['final_pass'] for r in rows) else 1

if __name__=='__main__':raise SystemExit(main())
