"""Offline scoring revision: never calls the provider or overwrites paid evidence."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path
from .batch import write_json
from .direction_explanation_regression import summarize,flow_refusal_check,unknown_unit_check
from .full_regression import apply_question_checks,check_quote_repair,classify
from .graph_explanations import direction_score,explanation_extras
from .refusal_semantics import refusal_score
from .development import ROOT

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--batch',type=Path,required=True)
    args=parser.parse_args();batch=args.batch
    out=batch/'scoring_revision_v2';out.mkdir(exist_ok=False)
    original=json.loads((batch/'manifest.json').read_text());items=original['cases']
    paths=set(original['hashes'])|{'evaluation/direction_explanation_rescore.py','task_cards/direction_explanation_scoring_v2.md'}
    hashes={}
    for rel in sorted(paths):
        data=(ROOT/rel).read_bytes();hashes[rel]=hashlib.sha256(data).hexdigest()
        dest=out/'snapshot'/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
    write_json(out/'manifest.json',dict(protocol='direction_explanation_scoring_v2',api_calls=0,
               source_batch=str(batch),source_manifest_sha256=hashlib.sha256((batch/'manifest.json').read_bytes()).hexdigest(),hashes=hashes))
    rows=[];sources={}
    for repeat in range(1,4):
        for c in items:
            old=batch/f'round_{repeat}'/c['id'];folder=out/f'round_{repeat}'/c['id'];folder.mkdir(parents=True)
            for name in ['case_result.json','api.json','generation_record.json']:
                if (old/name).exists():
                    sources[str(old/name)]=hashlib.sha256((old/name).read_bytes()).hexdigest()
            row=json.loads((old/'case_result.json').read_text())
            meta=json.loads((old/'api.json').read_text())
            if (old/'generation_record.json').exists():shutil.copyfile(old/'generation_record.json',folder/'generation_record.json')
            qa=apply_question_checks(c,row,folder);quote=check_quote_repair(c,meta,folder)
            if quote.get('passed') is False:row.update(outcome='fail',failure_category='quote_audit_failed')
            if (folder/'generation_record.json').exists():
                env=json.loads((folder/'generation_record.json').read_text())['envelope'];checks=[]
                if c['id'] in ('graph_units_fractional_flow','flow_same_fractional','flow_unknown_conversion'):
                    checks.append(('flow_refusal',unknown_unit_check(env) if c['id']=='flow_unknown_conversion' else flow_refusal_check(env)))
                if c.get('refusal_topic'):
                    checks.append(('refusal_semantics',refusal_score(env,c['refusal_topic'])))
                    checks.append(('refusal_extra_assertions',explanation_extras(env,c.get('present_fields',[]))))
                if c.get('check_direction'):checks.append(('direction_semantics',direction_score(env)))
                for name,audit in checks:
                    write_json(folder/(name+'.json'),audit)
                    if not audit['passed']:row.update(outcome='fail',failure_category=name,detail=json.dumps(audit,ensure_ascii=False))
            row.update(group=c['group'],repeat=repeat,generation_route=meta.get('request_contract',{}).get('route'),
                       question_semantics_passed=qa.get('passed'),quote_audit_passed=quote.get('passed'),**classify(row,meta))
            if row['run_path']:row['run_path']=f'round_{repeat}/'+row['run_path']
            rows.append(row)
    summarize(out,rows)
    summary=(out/'summary.md').read_text()
    (out/'summary.md').write_text('# 零新增API的评分修订重评\n\n同一48次历史付费响应，不是新调用；tokens为源批使用量，不重复计费统计。原批评分保留。\n\n'+summary)
    write_json(out/'source_integrity.json',dict(hashes=sources,passed=all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in sources.items())))
    print(out)
    print([sum(r[k] for r in rows) for k in ('original_pass','after_format_pass','final_pass')])

if __name__=='__main__':main()
