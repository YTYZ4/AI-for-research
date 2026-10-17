"""Post-fix dynamic unit conversion regression: four cases, three repeats."""
import argparse
import hashlib
import json
import uuid
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from .batch import run_case,write_json
from .development import ROOT,CASES,score
from .robustness import unit_score
from assistant.config import credentials

BASE={c['id']:c for c in CASES}
ITEMS=[dict(BASE['DYN01'],id='cooling_control'),dict(BASE['DYN02'],id='logistic_control'),
       dict(BASE['DYN01'],id='cooling_units',problem='examples/robustness/cooling_units.txt'),
       dict(BASE['DYN02'],id='logistic_units',problem='examples/robustness/logistic_units.txt')]


def check(case,record,path):
    name=case['id'];gen=record['generation'];source=gen.get('source_model');conversion=gen.get('unit_conversion')
    if not source or not conversion:return {'passed':False,'reason':'缺少原题参数或程序换算记录'}
    cooling=name.startswith('cooling');mixed=name.endswith('units')
    expected=dict(initial=90 if cooling else 100,equilibrium=20 if cooling else 1000,rate=.1 if cooling else .2,
                  rate_unit='1/min' if cooling else '1/day',duration=(.5 if cooling else 720) if mixed else 30,
                  duration_unit='hour' if mixed else ('min' if cooling else 'day'))
    raw=all(source[k]==v for k,v in expected.items())
    numeric=unit_score(case,record,path) if mixed else score(BASE['DYN01' if cooling else 'DYN02'],record,path)
    return {'passed':raw and numeric['passed'] and conversion['source_quotes_checked'],'source_values_match_original':raw,'numeric':numeric,'conversion':conversion}


def main(argv=None):
    p=argparse.ArgumentParser(description='动态单位原始参数提取+本地换算：四题各三次，共12次调用')
    p.add_argument('--output',type=Path,default=ROOT/'outputs/unit_regressions')
    p.add_argument('--audit-format',action='store_true',help='额外统计原始schema与本地格式修复')
    args=p.parse_args(argv)
    key,name=credentials(None,'deepseek')
    if not key:p.error('请先配置DeepSeek')
    directory=args.output/(datetime.now(ZoneInfo('Asia/Shanghai')).strftime('%Y%m%d_%H%M%S')+'_'+uuid.uuid4().hex[:8]);directory.mkdir(parents=True)
    paths={Path(c['problem']) for c in ITEMS}
    for group in ('assistant','evaluation','tests'):
        paths.update(f.relative_to(ROOT) for f in (ROOT/group).glob('*.py'))
    hashes={}
    for rel in paths:
        data=(ROOT/rel).read_bytes();hashes[str(rel)]=hashlib.sha256(data).hexdigest();target=directory/'snapshot'/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    write_json(directory/'manifest.json',dict(protocol='format_repair_v1' if args.audit_format else 'source_units_v1',repeats=3,max_calls=12,retries=0,requested_model=name,cases=ITEMS,hashes=hashes))
    print('单位回归：'+str(directory),flush=True);rows=[]
    for repeat in (1,2,3):
        folder=directory/f'round_{repeat}';folder.mkdir()
        for c in ITEMS:
            row=run_case(c,folder,'deepseek',name,score_fn=check);row['repeat']=repeat
            if row['run_path']:row['run_path']=f'round_{repeat}/'+row['run_path']
            api_path=folder/c['id']/'api.json'
            metadata=json.loads(api_path.read_text()) if api_path.exists() else {}
            audit=metadata.get('format_repair',{})
            row.update(raw_schema_valid=audit.get('raw_schema_valid'),format_action=audit.get('action','unknown'))
            rows.append(row);write_json(directory/'results.json',rows)
            print(repeat,c['id'],row['outcome'],row['failure_category'],flush=True)
    lines=['# 原始参数与确定性单位换算回归','',f"通过{sum(r['outcome']=='pass' for r in rows)}/12；已知tokens {sum(r['total_tokens'] or 0 for r in rows)}；未知usage {sum(r['total_tokens'] is None for r in rows)}。",'每题三次，无重试；仅验证两个动态题族，不代表其他任务的单位都已自动处理。','','| 场景 | 次数 | 结果 | 失败分类 |','|---|---:|---|---|']
    lines += [f"| {r['id']} | {r['repeat']} | {r['outcome']} | {r['failure_category']} |" for r in rows]
    lines += ['','评分同时核对原题未换算参数、程序换算记录、原题解析轨迹。失败详情见results.json；source_model.json和unit_conversion.json在每次运行目录。']
    if args.audit_format:
        lines += ['', '## 格式与系统结果分开统计', '',
                  f"原始schema通过 {sum(r['raw_schema_valid'] is True for r in rows)}/{len(rows)}；本地格式修复 {sum(r['format_action']=='applied' for r in rows)} 条；拒绝修复 {sum(r['format_action']=='rejected' for r in rows)} 条。",
                  'schema通过不等于原题正确；系统通过仍要求原值提取、程序换算和独立数值评分。所有格式修复均为本地单次操作，不新增API请求。', '', '| 场景 | 次数 | 原schema通过 | 格式处理 | 系统结果 |', '|---|---:|---|---|---|']
        lines += [f"| {r['id']} | {r['repeat']} | {r['raw_schema_valid']} | {r['format_action']} | {r['outcome']} |" for r in rows]
    (directory/'summary.md').write_text('\n'.join(lines)+'\n')
    return 0 if all(r['outcome']=='pass' for r in rows) else 1

if __name__=='__main__':raise SystemExit(main())
