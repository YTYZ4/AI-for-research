"""Run exactly one attempt per fixed development case, preserving failures."""
import argparse
import csv
import hashlib
import json
import platform
import time
import uuid
from collections import Counter
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import scipy
from modeling_assistant import __version__
from modeling_assistant.cli import save_record
from modeling_assistant.config import credentials
from modeling_assistant.provider import generate
from modeling_assistant.fitting import load_data, data_context, solve_fit
from modeling_assistant.dynamics import solve_dynamics
from modeling_assistant.graphs import solve_graph
from modeling_assistant.solver import solve
from .development import CASES, ROOT, reference, score


def write_json(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')


def summarize(directory,rows,mode):
    write_json(directory/'results.json',rows)
    fields=['id','family','outcome','failure_category','detail','elapsed_seconds','total_tokens','requested_model','response_model','run_path']
    with (directory/'results.csv').open('w',newline='',encoding='utf-8-sig') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows({k:r.get(k) for k in fields} for r in rows)
    passed=sum(r['outcome']=='pass' for r in rows)
    failures=Counter(r['failure_category'] for r in rows if r['outcome']!='pass')
    known=sum(r['total_tokens'] for r in rows if r['total_tokens'] is not None)
    unknown=sum(r['total_tokens'] is None for r in rows)
    lines=['# 八题开发基线评测','',f'模式：{mode}；已完成 {len(rows)}/8；自动检查通过 {passed}/{len(rows)}。',
           f'已知总tokens：{known}；usage未知：{unknown}例；未知不计作0，金额以账单为准。',
           '每题一次，不自动重试或修复。固定开发题，不代表保留题泛化、稳定成功率或对照实验效果。',
           '自动通过涵盖数值与部分结构检查；中文含义、单位和假设仍需人工审核。离线模式不计为LLM实验。','',
           '| 题号 | 类别 | 结果 | 失败分类 | tokens | 秒 |','|---|---|---|---|---:|---:|']
    for r in rows:lines.append(f"| {r['id']} | {r['family']} | {r['outcome']} | {r['failure_category']} | {r['total_tokens']} | {r['elapsed_seconds']:.3f} |")
    lines+=['','## 失败分析','',str(dict(failures)) if failures else '当前没有自动检查失败。仍需审查语义与评测覆盖边界。']
    for r in rows:
        if r['outcome']!='pass':lines += ['',f"- {r['id']}：{r['detail']}；证据见 {r['id']}/case_result.json 和 api.json（若有响应）。"]
    lines += ['','## 文件说明','','manifest.json 固定协议、模型名和输入/代码哈希；snapshot/ 保存本轮输入与代码。每题目录先保存原始API响应（不含密钥），再保存求解与评分。results.csv 可用于统计；不依据退出码或optimal状态直接判成功。',
              '失败分类：generation_error（网络/HTTP/响应解析或模型格式）、needs_clarification、unsupported、solver_error、verification_failed、evaluation_failed（原题评分不通过）、evaluator_error（评分器异常）。评分器异常不算模型答错，需单独修复并保留原记录。']
    (directory/'summary.md').write_text('\n'.join(lines)+'\n')


def run_case(case,directory,backend,model_name):
    folder=directory/case['id'];folder.mkdir()
    started=time.perf_counter();stage='generation';metadata={};record=None
    row=dict(id=case['id'],family=case['family'],outcome='fail',failure_category='',detail='',total_tokens=None,requested_model=model_name,response_model=None,run_path=None)
    try:
        text=(ROOT/case['problem']).read_text();dataset=load_data(ROOT/case['data']) if case.get('data') else None
        original=text
        if dataset:text+=data_context(dataset)
        if backend=='reference':
            envelope={'status':'ready','questions':[],'model':reference(case)};metadata={'backend':'reference','llm_used':False}
        else:envelope,metadata=generate(text,model_name,backend=backend,audit_path=folder/'api.json')
        record=dict(created_at=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),version=__version__,python=platform.python_version(),scipy=scipy.__version__,backend=backend,input=text,original_input=original,generation=metadata,envelope=envelope,stages=[],clarification_history=[],dataset=dataset)
        # Persist paid generation even when the following numerical stage fails.
        write_json(folder/'generation_record.json',record)
        if envelope['status']!='ready':
            row.update(failure_category=envelope['status'],detail='；'.join(envelope['questions']))
            row['run_path']=str(save_record(record,folder).relative_to(directory))
        else:
            stage='solver';m=envelope['model'];kind=m.get('task_type')
            if kind=='polynomial_fit':
                if dataset is None:raise ValueError('返回拟合模型但本题无数据附件')
                result=solve_fit(m,dataset)
            elif kind=='dynamics':result=solve_dynamics(m)
            elif kind=='graph':result=solve_graph(m)
            else:result=solve(m)
            record['stages']=[dict(label='批量基线',model=m,result=result)]
            run_folder=save_record(record,folder);row['run_path']=str(run_folder.relative_to(directory))
            if result['status'] not in ('optimal','fitted','simulated'):
                row.update(failure_category='solver_error',detail='期望可解开发题，实际状态：'+result['status'])
            elif result.get('verification',{}).get('passed') is False:
                row.update(failure_category='verification_failed',detail='运行时验证失败')
            else:
                stage='evaluation'
                expected_type={'optimization':None,'fitting':'polynomial_fit','dynamics':'dynamics','graph':'graph'}[case['family']]
                evaluation=score(case,record,run_folder/'run.json') if kind==expected_type else {'passed':False,'reason':'返回任务类型与原题不符'}
                write_json(folder/'evaluation.json',evaluation)
                if evaluation['passed']:row.update(outcome='pass')
                else:row.update(failure_category='evaluation_failed',detail=json.dumps(evaluation,ensure_ascii=False))
    except Exception as exc:
        row.update(failure_category={'generation':'generation_error','solver':'solver_error','evaluation':'evaluator_error'}[stage],detail=type(exc).__name__+': '+str(exc))
    finally:
        if (folder/'api.json').exists():metadata=json.loads((folder/'api.json').read_text())
        usage=metadata.get('usage') or {}
        row.update(total_tokens=usage.get('total_tokens') if backend!='reference' else 0,response_model=metadata.get('response_model'),elapsed_seconds=time.perf_counter()-started)
        write_json(folder/'case_result.json',row)
    return row


def main(argv=None):
    parser=argparse.ArgumentParser(description='固定八个开发题，每题单次调用；无重试/修复')
    parser.add_argument('--backend',choices=['deepseek','openai','reference'],default='deepseek')
    parser.add_argument('--llm-model')
    parser.add_argument('--output',type=Path,default=ROOT/'outputs/development_batches')
    args=parser.parse_args(argv)
    model_name=args.llm_model
    if args.backend!='reference':
        key,model_name=credentials(model_name,args.backend)
        if not key:parser.error('请先配置所选服务商API')
    stamp=datetime.now(ZoneInfo('Asia/Shanghai')).strftime('%Y%m%d_%H%M%S')
    directory=args.output/(stamp+'_'+uuid.uuid4().hex[:8]);directory.mkdir(parents=True)
    files=set()
    for case in CASES:
        files.add(case['problem'])
        for field in ('data','reference'):
            if case.get(field):files.add(case[field])
    files.add('examples/production/problem.txt')
    files.update(str(p.relative_to(ROOT)) for folder in ('modeling_assistant','evaluation') for p in (ROOT/folder).glob('*.py'))
    hashes={}
    for name in sorted(files):
        content=(ROOT/name).read_bytes();hashes[name]=hashlib.sha256(content).hexdigest()
        target=directory/'snapshot'/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(content)
    write_json(directory/'manifest.json',dict(protocol='development_single_attempt_v1',backend=args.backend,requested_model=model_name,cases=CASES,max_calls=0 if args.backend=='reference' else 8,retries=0,repair_rounds=0,max_output_tokens_per_call=6000,hashes=hashes,version=__version__,python=platform.python_version(),scipy=scipy.__version__))
    print('批量记录：'+str(directory.resolve()),flush=True)
    rows=[]
    for case in CASES:
        row=run_case(case,directory,args.backend,model_name);rows.append(row);summarize(directory,rows,args.backend)
        print(f"{case['id']}: {row['outcome']} {row['failure_category']}，tokens={row['total_tokens']}",flush=True)
    return 0 if all(r['outcome']=='pass' for r in rows) else 1

if __name__=='__main__':raise SystemExit(main())
