"""Independent evaluator of predictions using source CSV and raw-basis polyfit.
Not imported by the runtime assistant. This checks numerical correctness, not task semantics.
"""
import csv
import json
from pathlib import Path
import numpy as np


def evaluate_run(source, run_path):
    with Path(source).open() as f:
        rows=list(csv.DictReader(f))
    run=json.loads(Path(run_path).read_text())
    result=run['stages'][0]['result']
    degree=result['degree']
    train=[r for r in rows if r['split']=='train']
    coefficients=np.polyfit([float(r['x']) for r in train],[float(r['y']) for r in train],degree)
    checks=[]
    for split in ('train','test'):
        expected=[r for r in rows if r['split']==split]
        actual=[r for r in result['predictions'] if r['split']==split]
        if len(expected)!=len(actual):
            checks.append(False);continue
        x=np.array([float(r['x']) for r in expected]);y=np.array([float(r['y']) for r in expected])
        yp=np.polyval(coefficients,x)
        checks.extend([bool(np.allclose(yp,[r['predicted'] for r in actual],atol=1e-8,rtol=0)),
                       bool(np.allclose(x,[r['x'] for r in actual],atol=0,rtol=0)),
                       bool(np.allclose(y,[r['y'] for r in actual],atol=0,rtol=0)),
                       abs(float(np.sqrt(np.mean((y-yp)**2)))-result['metrics'][split]['rmse'])<1e-8,
                       abs(float(np.mean(abs(y-yp)))-result['metrics'][split]['mae'])<1e-8])
    return {'passed':all(checks),'checks':checks,'tolerance':1e-8,
            'scope':'固定数据和所选阶数的独立数值复算；不证明阶数选择的泛化能力或题意理解正确'}
