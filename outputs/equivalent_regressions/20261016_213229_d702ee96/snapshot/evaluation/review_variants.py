"""Offline re-score saved solved records; never invokes a model or overwrites raw results."""
import argparse
import json
from pathlib import Path
from .variants import variant_score,summary
from .batch import write_json


def main(argv=None):
    parser=argparse.ArgumentParser(description='离线复核变体批次，保留原结果；不调用API')
    parser.add_argument('batch',type=Path);args=parser.parse_args(argv)
    root=args.batch;out=root/'offline_review';out.mkdir(exist_ok=False)
    manifest=json.loads((root/'manifest.json').read_text());items={c['id']:c for c in manifest['cases']}
    rows=json.loads((root/'results.json').read_text());changes=[]
    for row in rows:
        if not row['run_path']:continue
        path=root/row['run_path']/'run.json';record=json.loads(path.read_text());case=items[row['id']]
        if not record['stages']:continue
        before=dict(row)
        try:
            result=variant_score(case,record,path)
            write_json(out/f"{row['id']}_round{row['repeat']}_evaluation.json",result)
            row.update(outcome='pass' if result['passed'] else 'fail',failure_category='' if result['passed'] else 'evaluation_failed',detail='' if result['passed'] else json.dumps(result,ensure_ascii=False))
        except Exception as exc:
            row.update(outcome='fail',failure_category='evaluator_error',detail=type(exc).__name__+': '+str(exc))
        if row['outcome']!=before['outcome'] or row['failure_category']!=before['failure_category']:
            changes.append(dict(id=row['id'],repeat=row['repeat'],before=before,after=dict(row),reason='离线读取已保存求解结果，修正verification=null引发的评测器空值错误'))
        row['run_path']='../'+row['run_path']
    write_json(out/'adjudications.json',changes);summary(out,rows,64)
    print(f'离线复核：{sum(r["outcome"]=="pass" for r in rows)}/64；调整{len(changes)}条；{out}')
    return 0

if __name__=='__main__':raise SystemExit(main())
