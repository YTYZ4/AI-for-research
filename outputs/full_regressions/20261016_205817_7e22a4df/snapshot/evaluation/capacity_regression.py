"""Continuous Logistic boundaries and paraphrases, three independent calls each."""
import hashlib
import json
import math
import re
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo
from modeling_assistant import __version__
from modeling_assistant.config import credentials
from .batch import run_case, write_json
from .development import ROOT

VALUES = [('zero',100,0),('negative',100,-.5),('missing',100,None),
          ('fraction',100,1000.5),('small',.1,.5),('zero_initial',0,.5),('above_capacity',1.5,.5),('above_paraphrase',1.5,.5),('above_symbols',1.5,.5),
          ('above_reordered',1.5,.5),('equal_capacity',.5,.5),('near_above',.5001,.5)]


def question_score(envelope):
    text='；'.join(envelope['questions'])
    # Require explicit real-valued domain; allow explicitly negated integer limits.
    stripped=re.sub(r'(?:不要求|不必是|无需为|不需要是|不限于|不限定为|不必为|不需要为|无需是|不要求为)(?:正)?整数','',text)
    checks={'clarification':envelope['status']=='needs_clarification',
            'capacity':bool(re.search(r'容量|K',text)),
            'positive_real':bool(re.search(r'正实数|正数',text)),
            'fraction_allowed':bool(re.search(r'小数|正实数',text)),
            'no_integer_requirement':not bool(re.search(r'整数|integer|取整',stripped,re.I))}
    return {'passed':all(checks.values()),'checks':checks,'text':text}


def score(case,record,path):
    m=record['envelope']['model'];n,k=case['initial'],case['capacity']
    checks={'original_parameters':m['system']=='logistic' and m['initial']==n and m['equilibrium']==k and m['rate']==.2 and m['duration']==30 and m['time_unit']=='day' and m['rate_unit']=='1/day'}
    rows=record['stages'][0]['result']['trajectory']
    errors=[abs(r['value']-(0 if n==0 else k/(1+(k/n-1)*math.exp(-.2*r['time'])))) for r in rows]
    checks['trajectory']=len(rows)==101 and rows[0]['time']==0 and rows[-1]['time']==30 and all(math.isfinite(e) and e<1e-5 for e in errors)
    return {'passed':all(checks.values()),'checks':checks,'max_error':max(errors)}


def main():
    from .full_regression import classify
    key,model=credentials(None,'deepseek')
    if not key:raise ValueError('请先配置DeepSeek')
    cases=[dict(id=name,family='dynamics',problem=f'examples/capacity_boundaries/{name}.txt',initial=n,capacity=k,
                expected_envelopes=['needs_clarification'] if k is None or k<=0 else ['ready'],question_keywords=['K','容量']) for name,n,k in VALUES]
    directory=ROOT/'outputs/capacity_regressions'/(datetime.now(ZoneInfo('Asia/Shanghai')).strftime('%Y%m%d_%H%M%S')+'_'+uuid.uuid4().hex[:8]);directory.mkdir(parents=True)
    paths=[p for group in ('modeling_assistant','evaluation','tests') for p in (ROOT/group).glob('*.py')]+list((ROOT/'examples/capacity_boundaries').glob('*.txt'))
    hashes={}
    for path in paths:
        rel=path.relative_to(ROOT);data=path.read_bytes();hashes[str(rel)]=hashlib.sha256(data).hexdigest()
        dest=directory/'snapshot'/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
    write_json(directory/'manifest.json',dict(version=__version__,model=model,cases=cases,protocol="capacity_boundaries_v2",repeats=3,max_calls=len(cases)*3,retries=0,hashes=hashes))
    print(directory,flush=True);rows=[]
    for repeat in range(1,4):
        rd=directory/f'round_{repeat}';rd.mkdir()
        for case in cases:
            row=run_case(case,rd,'deepseek',model,score_fn=score)
            folder=rd/case['id'];generation=folder/'generation_record.json'
            if case['expected_envelopes']==['needs_clarification'] and generation.exists():
                audit=question_score(json.loads(generation.read_text())['envelope']);write_json(folder/'question_evaluation.json',audit)
                if not audit['passed']:row.update(outcome='fail',failure_category='clarification_semantics',detail=json.dumps(audit,ensure_ascii=False))
            metadata=json.loads((folder/'api.json').read_text()) if (folder/'api.json').exists() else {}
            row.update(repeat=repeat,**classify(row,metadata))
            if row['run_path']:row['run_path']=f'round_{repeat}/'+row['run_path']
            rows.append(row);write_json(directory/'results.json',rows)
            print(repeat,case['id'],row['pass_path'],row['failure_category'],flush=True)
    stability={c['id']:sum(r['final_pass'] for r in rows if r['id']==c['id']) for c in cases}
    write_json(directory/'stability.json',stability)
    lines=['# 正实数容量边界重复评测','',f"原始通过{sum(r['original_pass'] for r in rows)}/{len(cases)*3}；格式修复后累计{sum(r['after_format_pass'] for r in rows)}/{len(cases)*3}；含护栏最终{sum(r['final_pass'] for r in rows)}/{len(cases)*3}。",f"已知tokens {sum(r['total_tokens'] or 0 for r in rows)}；usage未知{sum(r['total_tokens'] is None for r in rows)}。",'','| 场景 | 通过次数 |','|---|---:|']
    lines += [f'| {name} | {count}/3 |' for name,count in stability.items()]
    lines += ['','每场景3次独立请求，无重试，固定开发边界；不能证明长期稳定或保留题泛化。追问文字规则另行人工复核，原始响应保留；未覆盖的措辞可能误判。']
    (directory/'summary.md').write_text('\n'.join(lines)+'\n')
    return 0 if all(r['final_pass'] for r in rows) else 1

if __name__=='__main__':raise SystemExit(main())
