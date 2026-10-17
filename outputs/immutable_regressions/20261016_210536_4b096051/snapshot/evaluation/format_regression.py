"""Replay the historical format failure offline, then run twelve fresh requests."""
import copy
import hashlib
import json
import platform
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo
import scipy
from .development import ROOT
from .batch import write_json
from .unit_regression import main as online_main, check, ITEMS
from modeling_assistant.provider import parse_deepseek_response
from modeling_assistant.units import normalize_dynamics
from modeling_assistant.dynamics import solve_dynamics
from modeling_assistant.cli import save_record
from modeling_assistant import __version__


def replay():
    source=ROOT/'outputs/unit_regressions/20261016_201428_3b74d7fb/round_3/cooling_units/api.json'
    original=json.loads(source.read_text());audit={}
    root=ROOT/'outputs/format_replays'/(datetime.now(ZoneInfo('Asia/Shanghai')).strftime('%Y%m%d_%H%M%S')+'_'+uuid.uuid4().hex[:8]);root.mkdir(parents=True)
    write_json(root/'original_api.json',original)
    try:parse_deepseek_response(original['response']);strict_failed=False
    except ValueError:strict_failed=True
    envelope=parse_deepseek_response(original['response'],audit)
    text=original['request']['messages'][-1]['content']
    source_model=copy.deepcopy(envelope['model']);model,conversion=normalize_dynamics(source_model,text)
    metadata=dict(backend='offline_replay',llm_used=False,response=original['response'],format_repair=audit,source_model=source_model,unit_conversion=conversion)
    record=dict(created_at=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),version=__version__,python=platform.python_version(),scipy=scipy.__version__,backend='offline_replay',input=text,original_input=text,generation=metadata,envelope=dict(status='ready',questions=[],model=model),stages=[dict(label='历史响应离线修复重放',model=model,result=solve_dynamics(model))],clarification_history=[],dataset=None)
    directory=save_record(record,root)
    evaluation=check(next(c for c in ITEMS if c['id']=='cooling_units'),record,directory/'run.json')
    evidence=dict(original_path=str(source),original_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),strict_parser_failed=strict_failed,format_repair=audit,evaluation=evaluation,api_calls=0,new_tokens=0,run_path=str(directory))
    write_json(root/'replay_evaluation.json',evidence)
    passed=strict_failed and audit['action']=='applied' and evaluation['passed']
    print(f'历史离线重放：{passed}；{root}',flush=True)
    if not passed:raise ValueError('历史格式失败未正确修复，不启动付费回归')
    return root


def main():
    replay()
    return online_main(['--output',str(ROOT/'outputs/format_regressions'),'--audit-format'])

if __name__=='__main__':raise SystemExit(main())
