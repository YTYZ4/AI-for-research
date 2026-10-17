"""Targeted post-fix regression: 10 online calls plus seven local CSV cases."""
import argparse
import hashlib
import json
import math
import uuid
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from .batch import run_case,write_json
from .development import ROOT,CASES,score
from .graphs import CASES as GRAPHS
from assistant.config import credentials
from assistant.fitting import load_data

BASE={c['id']:c for c in CASES}
ONLINE=[dict(BASE['DYN02'],id='invalid_capacity',problem='examples/development_variants/DYN02_error.txt',expected_envelopes=['needs_clarification','unsupported'],question_keywords=['容量','K','0']),
        dict(BASE['DYN02'],id='valid_logistic'),
        dict(BASE['DYN01'],id='cooling_units',problem='examples/robustness/cooling_units.txt'),
        dict(BASE['DYN02'],id='logistic_units',problem='examples/robustness/logistic_units.txt'),
        dict(BASE['NET01'],id='path_units',problem='examples/robustness/path_units.txt')]


def unit_score(case,record,path):
    if case['id']=='valid_logistic':return score(BASE['DYN02'],record,path)
    m=record['envelope']['model'];r=record['stages'][0]['result']
    if case['family']=='dynamics':
        cooling=case['id']=='cooling_units'
        # Convert model time to the original problem's minutes or days.
        conversion={'s':1/60,'min':1,'hour':60,'day':1440} if cooling else {'s':1/86400,'min':1/1440,'hour':1/24,'day':1}
        factor=conversion.get(m['time_unit'])
        if factor is None:return {'passed':False,'reason':'不支持的单位换算'}
        checks={'parameters':m['system']==('newton_cooling' if cooling else 'logistic') and m['initial']==(90 if cooling else 100) and m['equilibrium']==(20 if cooling else 1000),
                'rate':math.isclose(m['rate']/factor,.1 if cooling else .2,rel_tol=1e-10),
                'duration':math.isclose(m['duration']*factor,30,rel_tol=1e-10),
                'rate_unit':m['rate_unit']=='1/'+m['time_unit'],
                'state_unit':m['state_unit'].strip().casefold() in (['摄氏度','℃','°c','celsius','degc'] if cooling else ['个','个体'])}
        trajectory=r['trajectory'];errors=[]
        for row in trajectory:
            t=row['time']*factor
            target=20+70*math.exp(-.1*t) if cooling else 1000/(1+9*math.exp(-.2*t))
            errors.append(abs(row['value']-target))
        checks['trajectory']=len(errors)==101 and all(math.isfinite(e) and e<1e-5 for e in errors)
        checks['endpoints']=bool(trajectory) and abs(trajectory[0]['time'])<1e-10 and math.isclose(trajectory[-1]['time']*factor,30)
        return {'passed':all(checks.values()),'checks':checks,'max_error':max(errors)}
    factor={'km':1,'千米':1,'公里':1,'kilometer':1,'kilometers':1,'m':.001,'米':.001,'meter':.001,'meters':.001}.get(m['unit'])
    if factor is None:return {'passed':False,'reason':'距离单位无法转换'}
    expected=GRAPHS['shortest_path'];actual={(e['source'],e['target']):e['weight']*factor for e in m['edges']}
    checks={'original_edges':actual==expected,'source_target':m['source']=='S' and m['target']=='T','path':r['path']==['S','B','A','C','T'],'distance':math.isclose(r['value']*factor,8)}
    return {'passed':all(checks.values()),'checks':checks}


def main(argv=None):
    p=argparse.ArgumentParser(description='修复定向回归：7个本地数据用例+5场景各2次DeepSeek调用')
    p.add_argument('--output',type=Path,default=ROOT/'outputs/robustness_batches');args=p.parse_args(argv)
    key,name=credentials(None,'deepseek')
    if not key:p.error('请先配置DeepSeek')
    directory=args.output/(datetime.now(ZoneInfo('Asia/Shanghai')).strftime('%Y%m%d_%H%M%S')+'_'+uuid.uuid4().hex[:8]);directory.mkdir(parents=True)
    paths=set()
    for group in ('assistant','evaluation','tests'):
        paths.update(f.relative_to(ROOT) for f in (ROOT/group).glob('*.py'))
    paths.update(f.relative_to(ROOT) for f in (ROOT/'examples/robustness').glob('*'))
    paths.update(Path(c['problem']) for c in ONLINE);hashes={}
    for rel in paths:
        data=(ROOT/rel).read_bytes();hashes[str(rel)]=hashlib.sha256(data).hexdigest();dest=directory/'snapshot'/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
    write_json(directory/'manifest.json',dict(protocol='targeted_robustness_v1',max_calls=10,repeats=2,retries=0,cases=ONLINE,hashes=hashes,requested_model=name))
    local=[]
    for case in ('missing_y','nan','bad_split','train_only','constant_x','wrong_header','valid'):
        try:load_data(ROOT/'examples/robustness'/f'{case}.csv');accepted=True;detail='accepted'
        except ValueError as exc:accepted=False;detail=str(exc)
        local.append(dict(id=case,passed=accepted==(case=='valid'),accepted=accepted,detail=detail,api_calls=0))
    write_json(directory/'data_quality.json',local)
    print('定向回归：'+str(directory),flush=True);rows=[]
    for repeat in (1,2):
        rounddir=directory/f'round_{repeat}';rounddir.mkdir()
        for case in ONLINE:
            row=run_case(case,rounddir,'deepseek',name,score_fn=unit_score);row['repeat']=repeat
            if row['run_path']:row['run_path']=f'round_{repeat}/'+row['run_path']
            api=rounddir/case['id']/'api.json'
            meta=json.loads(api.read_text()) if api.exists() else {}
            row['local_guard_used']=bool(meta.get('local_validation'))
            row['raw_model_status']=None
            try:row['raw_model_status']=json.loads(meta['response']['choices'][0]['message']['content'])['status']
            except (KeyError,IndexError,ValueError,TypeError):pass
            rows.append(row);write_json(directory/'results.json',rows)
            print(repeat,case['id'],row['outcome'],'guard='+str(row['local_guard_used']),flush=True)
    total=sum(r['total_tokens'] or 0 for r in rows)
    lines=['# 修复后定向回归','',f"本地数据检查：{sum(r['passed'] for r in local)}/7；在线系统验收：{sum(r['outcome']=='pass' for r in rows)}/10；tokens {total}。",'本批为修复后定向测试，不覆盖或合并修复前64次结果。正确追问可能来自模型或本地护栏，分列如下。','','| 场景 | 次数 | 系统结果 | 原模型状态 | 本地护栏 |','|---|---:|---|---|---|']
    lines += [f"| {r['id']} | {r['repeat']} | {r['outcome']} | {r['raw_model_status']} | {r['local_guard_used']} |" for r in rows]
    lines += ['','数据质量是本地输入校验，不计LLM成功次数。两次通过不证明长期稳定。失败详情见results.json和每题API/评分证据。']
    (directory/'summary.md').write_text('\n'.join(lines)+'\n')
    return 0 if all(r['outcome']=='pass' for r in rows) and all(r['passed'] for r in local) else 1

if __name__=='__main__':raise SystemExit(main())
