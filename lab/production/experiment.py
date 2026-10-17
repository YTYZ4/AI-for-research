"""Paired pilot. No judge is called until ALL paid generation has finished."""
import copy
import hashlib
import json
import random
import time
import urllib.request
import ssl
import uuid
import platform
import scipy
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import truststore
from assistant.model import MODEL_SCHEMA
from assistant.solver import solve
from assistant.config import credentials,PROVIDERS
from .checker import check

ROOT=Path(__file__).resolve().parents[2]
SYSTEM="""核对生产计划的原题与当前候选模型，必要时修改；候选可能正确，正确时保持不变。
只返回完整模型JSON，不输出答案或解释，不生成代码。保留A、B变量标识符，允许改模型内容。不要因为给了检查结果就假定一定有错，也不要把未检出视为正确证明。
模型须符合以下Schema：
"""+json.dumps(MODEL_SCHEMA,ensure_ascii=False)
MAX_TOKENS=4000

def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+chr(10))

def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False).encode()).hexdigest()

def public_solve(model):
    try:
        r=solve(copy.deepcopy(model))
        return {k:r.get(k) for k in ['status','values','objective']}
    except Exception as exc:return {'status':'invalid_model','values':None,'objective':None,'error':str(exc)}

def request(problem,model,public,arm,diagnostic,model_name):
    payload={'problem':problem,'current_model':model,'solver_result':public,'instruction':'请核对原题，必要时修改；正确时保持。'}
    if arm=='program_feedback':payload['program_checks']=diagnostic
    return {'model':model_name,'messages':[{'role':'system','content':SYSTEM},
            {'role':'user','content':json.dumps(payload,ensure_ascii=False)}],
            'response_format':{'type':'json_object'},'max_tokens':MAX_TOKENS,
            'temperature':0,'thinking':{'type':'disabled'},'stream':False}

def call(body,key):
    req=urllib.request.Request(PROVIDERS['deepseek']['endpoint'],data=json.dumps(body).encode(),
                               headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'},method='POST')
    with urllib.request.urlopen(req,timeout=60,context=truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)) as f:
        return json.loads(f.read())

def changes(a,b,path=''):
    if type(a)!=type(b):return [{'path':path,'before':a,'after':b}]
    if isinstance(a,dict):
        return [x for k in sorted(set(a)|set(b)) for x in changes(a.get(k),b.get(k),path+'/'+k)]
    if isinstance(a,list):
        return [x for i in range(max(len(a),len(b))) for x in changes(a[i] if i<len(a) else None,b[i] if i<len(b) else None,path+'/'+str(i))]
    return [] if a==b else [{'path':path,'before':a,'after':b}]

def main():
    key,model_name=credentials(None,'deepseek')
    if not key:raise ValueError('DeepSeek未配置')
    assets=ROOT/'lab/production/assets'
    problem=(assets/'problem.txt').read_text()
    # Only neutral IDs and drafts are read before generation.
    drafts=json.loads((assets/'drafts.json').read_text())
    order=[(case,arm,rep) for case in drafts for arm in ['self_check','program_feedback'] for rep in range(1,4)]
    random.Random(1729).shuffle(order)
    out=ROOT/'outputs/research_pilots'/(datetime.now(ZoneInfo('Asia/Shanghai')).strftime('%Y%m%d_%H%M%S')+'_'+uuid.uuid4().hex[:8])
    out.mkdir(parents=True)
    paths=set()
    for group in ['assistant','lab/production']:
        paths.update(p for p in (ROOT/group).rglob('*') if p.is_file() and '__pycache__' not in str(p))
    paths.update([ROOT/'protocols/pilot_v1.md',ROOT/'requirements.lock',ROOT/'tests/test_pilot.py'])
    hashes={}
    for p in sorted(paths):
        rel=p.relative_to(ROOT);data=p.read_bytes();hashes[str(rel)]=hashlib.sha256(data).hexdigest()
        target=out/'snapshot'/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    write(out/'manifest.json',{'protocol':'production_feedback_pilot_v1','python':platform.python_version(),'scipy':scipy.__version__,'model':model_name,'max_tokens_per_call':MAX_TOKENS,'rounds':2,
          'repeats':3,'max_calls':48,'order':order,'hashes':hashes,'initial_hashes':{k:digest(v) for k,v in drafts.items()},
          'direct_corrections_enabled':False,'seed':1729})
    print(out,flush=True)
    all_runs=[]
    for case,arm,rep in order:
        folder=out/case/arm/str(rep);current=copy.deepcopy(drafts[case]);rounds=[]
        initial_public=public_solve(current);initial_check=check(problem,current,initial_public)
        for step in [1,2]:
            public=public_solve(current);diagnostic=check(problem,current,public)
            body=request(problem,current,public,arm,diagnostic,model_name)
            before=copy.deepcopy(current);started=time.perf_counter();response=None;error=None
            try:
                response=call(body,key)
                write(folder/f'round_{step}_response.json',response)
                choice=response['choices'][0]
                if choice['finish_reason']!='stop':raise ValueError('输出未正常完成')
                raw=choice['message']['content'];current=json.loads(raw)
                if not isinstance(current,dict):raise ValueError('模型不是JSON对象')
            except Exception as exc:
                error=type(exc).__name__ # No transport exception text or credentials in log.
                current={'invalid_response':response if response is not None else error}
            record={'step':step,'request':body,'response':response,'error':error,'elapsed_seconds':time.perf_counter()-started,
                    'before':before,'after':current,'changes':changes(before,current),
                    'public_before':public,'checks_before':diagnostic,'feedback_exposed':arm=='program_feedback',
                    'public_after':public_solve(current),'usage':(response or {}).get('usage'),'direct_corrections':0}
            write(folder/f'round_{step}.json',record);rounds.append(record)
        run={'case':case,'arm':arm,'repeat':rep,'initial_model':drafts[case],'initial_public':initial_public,'initial_check':initial_check,'rounds':rounds}
        write(folder/'trajectory.json',run);all_runs.append(run)
        print(case,arm,rep,'completed',flush=True)
    # Reference and label access begins here, after the last model call.
    from .judge import score
    reference=json.loads((assets/'reference.json').read_text());labels=json.loads((assets/'labels.json').read_text())
    results=[]
    for run in all_runs:
        initial=score(run['initial_model'],run['initial_public'],reference)
        grades=[score(r['after'],r['public_after'],reference) for r in run['rounds']]
        row={k:run[k] for k in ['case','arm','repeat']}
        row.update(label=labels[run['case']],initial=initial,round_scores=grades,final_pass=grades[-1]['passed'],
                   initial_detected=bool(run['initial_check']['issues']),
                   direct_corrections=0,calls=2,
                   tokens=sum((r['usage'] or {}).get('total_tokens',0) for r in run['rounds']),
                   usage_unknown=sum(r['usage'] is None for r in run['rounds']),
                   elapsed_seconds=sum(r['elapsed_seconds'] for r in run['rounds']))
        results.append(row)
    write(out/'results.json',results)
    print('FINISHED',flush=True)

if __name__=='__main__':main()
