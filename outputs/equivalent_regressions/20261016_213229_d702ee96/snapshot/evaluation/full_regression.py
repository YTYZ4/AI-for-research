"""One frozen full development pass, separating native, repaired and guarded passes."""
import argparse
import csv
import hashlib
import json
import platform
import uuid
from collections import Counter,defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import scipy
from modeling_assistant import __version__
from modeling_assistant.config import credentials
from modeling_assistant.fitting import load_data
from .batch import run_case,write_json
from .development import ROOT
from .variants import cases as variant_cases,variant_score
from .robustness import ONLINE,unit_score
from .unit_regression import check as source_score
from .capacity_regression import VALUES, score as capacity_score, question_score
from .clarification import parameters_locked, locked_question_score


def cases():
    result=variant_cases()
    for c in ONLINE:
        if c['id'] in ('cooling_units','logistic_units','path_units'):
            result.append(dict(c,kind='units',base_id={'cooling_units':'DYN01','logistic_units':'DYN02','path_units':'NET01'}[c['id']]))
    for name,n,k in VALUES:
        result.append(dict(id='capacity_'+name,base_id='DYN02',kind='boundary',family='dynamics',
                           problem=f'examples/capacity_boundaries/{name}.txt',initial=n,capacity=k,
                           expected_envelopes=['needs_clarification'] if k is None or k<=0 else ['ready'],
                           question_keywords=['K','容量']))
    return result


def apply_question_checks(case,row,folder):
    """Keep the initial evaluator result, then layer explicit clarification rules."""
    file=folder/'generation_record.json'
    if not file.exists():return {'applied':False,'reason':'no_generation_record'}
    envelope=json.loads(file.read_text())['envelope']
    if envelope['status']=='ready':return {'applied':False,'reason':'ready_scored_numerically'}
    text='；'.join(envelope['questions'])
    checks={'expected_status':envelope['status'] in case.get('expected_envelopes',['ready']),
            'nonempty_question':bool(text.strip()),
            'relevant_topic':not case.get('question_keywords') or any(k in text for k in case['question_keywords'])}
    capacity_question=(case['id'] in ('DYN02_missing','DYN02_error') or
                       case['kind']=='boundary' and case.get('expected_envelopes')==['needs_clarification'])
    locked=parameters_locked((ROOT/case['problem']).read_text())
    if locked:checks['no_replacement_suggestion']=locked_question_score(envelope)['passed']
    elif capacity_question:checks.update(question_score(envelope)['checks'])
    audit={'applied':True,'passed':all(checks.values()),'checks':checks,'text':text,
           'scope':'状态/主题初筛；显式禁止改值时检查修改建议，否则Logistic容量检查正实数限制。不是完整语义证明。'}
    write_json(folder/'question_evaluation.json',audit)
    if not audit['passed'] and row['outcome']=='pass':
        row.update(outcome='fail',failure_category='clarification_semantics',detail=json.dumps(audit,ensure_ascii=False))
    return audit


def score(case,record,path):
    if case['kind']=='boundary':return capacity_score(case,record,path)
    if case['kind']=='units':
        return source_score(case,record,path) if case['family']=='dynamics' else unit_score(case,record,path)
    result=variant_score(case,record,path)
    if case['family']=='dynamics':
        control=dict(case,id='cooling_control' if case['base_id']=='DYN01' else 'logistic_control')
        source=source_score(control,record,path)
        return {'passed':result['passed'] and source['passed'],'original_problem':result,'source_parameters':source}
    return result


def classify(row,metadata):
    audit=metadata.get('format_repair',{})
    repaired=audit.get('action')=='applied';guard=bool(metadata.get('local_validation'))
    native_schema=audit.get('raw_schema_valid')
    source_repaired=bool(metadata.get('source_quote_repair'))
    passed=row['outcome']=='pass'
    path='failed'
    if passed:
        path='local_guard' if guard else 'local_source_repair' if source_repaired else 'format_repair' if repaired else 'native' if native_schema is True else 'unclassified'
    return dict(raw_schema_valid=native_schema,format_action=audit.get('action','not_recorded'),
                local_guard_used=guard,source_quote_repaired=source_repaired,original_pass=passed and path=='native',
                after_format_pass=passed and path in ('native','format_repair'),
                final_pass=passed,pass_path=path)


def summarize(directory,rows,local,total):
    write_json(directory/'results.json',rows)
    fields=['id','base_id','kind','question_semantics_passed','raw_schema_valid','format_action','local_guard_used','source_quote_repaired','original_pass','after_format_pass','final_pass','pass_path','failure_category','detail','total_tokens','elapsed_seconds','run_path']
    with (directory/'results.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows({k:r.get(k) for k in fields} for r in rows)
    counts=Counter(r['pass_path'] for r in rows);groups=defaultdict(list)
    for r in rows:groups[r['kind']].append(r)
    lines=['# 当前版本完整开发回归','',f"完成{len(rows)}/{total}；原始通过{sum(r['original_pass'] for r in rows)}；格式修复后累计通过{sum(r['after_format_pass'] for r in rows)}；含护栏最终通过{sum(r['final_pass'] for r in rows)}。",f"路径计数：{dict(counts)}。",f"原schema通过{sum(r['raw_schema_valid'] is True for r in rows)}；schema未知{sum(r['raw_schema_valid'] is None for r in rows)}。",f"已知tokens {sum(r['total_tokens'] for r in rows if r['total_tokens'] is not None)}；usage未知{sum(r['total_tokens'] is None for r in rows)}。",f"本地CSV检查{sum(r['passed'] for r in local)}/{len(local)}，API调用0，单独统计。",'',
           '原始通过=无需格式修复或本地纠错追问，且原题评分通过；正常单位转换与数值求解属于正常流程，不计修复。格式修复后累计通过=原始通过+仅靠允许的格式删除恢复的通过。含本地处理最终通过还包含原文引用修复及本地拦截处理。schema通过本身不代表题意正确。', '',
           '| 类型 | 数量 | 原始通过 | 格式修复后累计 | 含护栏最终 |','|---|---:|---:|---:|---:|']
    for kind,rs in groups.items():lines.append(f"| {kind} | {len(rs)} | {sum(r['original_pass'] for r in rs)} | {sum(r['after_format_pass'] for r in rs)} | {sum(r['final_pass'] for r in rs)} |")
    lines+=['','## 失败与本地接管','']
    for r in rows:
        if r['pass_path']!='native':lines.append(f"- {r['id']}：{r['pass_path']}，{r['failure_category']}；{r['detail']}")
    lines+=['',f'固定{total}个在线场景，每题1次，不重试、不在中途调参。24变体、3个单位场景与12个边界场景不算新基础题。仅为单轮开发回归，不用于稳定率或保留题泛化结论。关键词追问与严格结构评分仍需定性复核；任何后续审查单独保存，不覆盖本统计。']
    (directory/'summary.md').write_text('\n'.join(lines)+'\n')


def main(argv=None):
    p=argparse.ArgumentParser(description='当前版本47个在线场景各1次+7个本地CSV检查；无重试')
    p.add_argument('--output',type=Path,default=ROOT/'outputs/full_regressions');args=p.parse_args(argv)
    key,model=credentials(None,'deepseek')
    if not key:p.error('请先配置DeepSeek')
    items=cases();directory=args.output/(datetime.now(ZoneInfo('Asia/Shanghai')).strftime('%Y%m%d_%H%M%S')+'_'+uuid.uuid4().hex[:8]);directory.mkdir(parents=True)
    paths={Path('task_cards/full_regression_protocol_v2.md'),Path('examples/development_variants/manifest.json'),Path('examples/production/problem.txt'),Path('requirements-assistant-lock.txt')}
    for c in items:
        for key in ('problem','data','reference'):
            if c.get(key):paths.add(Path(c[key]))
    for group in ('evaluation','modeling_assistant','tests'):
        paths.update(f.relative_to(ROOT) for f in (ROOT/group).glob('*.py'))
    paths.update(f.relative_to(ROOT) for f in (ROOT/'examples/robustness').glob('*.csv'))
    hashes={}
    for rel in sorted(paths):
        data=(ROOT/rel).read_bytes();hashes[str(rel)]=hashlib.sha256(data).hexdigest();dest=directory/'snapshot'/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
    write_json(directory/'manifest.json',dict(protocol='full_development_single_pass_v2',version=__version__,cases=items,max_calls=len(items),repeats=1,retries=0,model=model,hashes=hashes,python=platform.python_version(),scipy=scipy.__version__))
    local=[]
    for name in ('missing_y','nan','bad_split','train_only','constant_x','wrong_header','valid'):
        try:load_data(ROOT/'examples/robustness'/f'{name}.csv');accepted=True;detail='accepted'
        except ValueError as exc:accepted=False;detail=str(exc)
        local.append(dict(id=name,passed=accepted==(name=='valid'),accepted=accepted,detail=detail,api_calls=0))
    write_json(directory/'data_quality.json',local)
    print('完整回归：'+str(directory),flush=True);rows=[]
    for c in items:
        row=run_case(c,directory,'deepseek',model,score_fn=score)
        audit=apply_question_checks(c,row,directory/c['id'])
        row['question_semantics_passed']=audit.get('passed')
        api=directory/c['id']/'api.json';metadata=json.loads(api.read_text()) if api.exists() else {}
        row.update(kind=c['kind'],base_id=c['base_id'],**classify(row,metadata));rows.append(row)
        write_json(directory/c['id']/'classified_result.json',row);summarize(directory,rows,local,len(items))
        print(c['id'],row['pass_path'],row['failure_category'],flush=True)
    return 0 if all(r['final_pass'] for r in rows) and all(r['passed'] for r in local) else 1

if __name__=='__main__':raise SystemExit(main())
