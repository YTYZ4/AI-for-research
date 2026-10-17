"""Local least squares with immutable explicit split and train-only selection."""
import csv
import hashlib
import io
import numpy as np
from .model import validate_model


def load_data(path):
    raw = path.read_bytes()
    if len(raw) > 2_000_000:
        raise ValueError('拟合 CSV 最大 2 MB')
    reader = csv.DictReader(io.StringIO(raw.decode('utf-8-sig')))
    if reader.fieldnames != ['x', 'y', 'split']:
        raise ValueError('CSV 表头必须为 x,y,split')
    rows = []
    for row_number, row in enumerate(reader, start=2):
        try:
            x, y = float(row['x']), float(row['y'])
            split = row['split']
            if None in row or not np.isfinite([x, y]).all() or split not in ('train', 'test'):
                raise ValueError()
        except (ValueError, TypeError, KeyError):
            raise ValueError(f'CSV 第{row_number}行含缺失/非有限数字、列数错误或非法 split（仅 train/test）；请修正原数据后重试') from None
        rows.append({'x': x, 'y': y, 'split': split})
    counts = {s: sum(r['split'] == s for r in rows) for s in ('train', 'test')}
    if counts['train'] < 10 or counts['test'] < 2 or len(rows) > 10000:
        raise ValueError('需要至少10条训练、2条留出数据；最多10000条')
    if len({r['x'] for r in rows if r['split']=='train'}) < 2:
        raise ValueError('训练数据的 x 全部相同，无法辨识当前支持的带截距多项式；请补充不同 x 的训练观测')
    return {'sha256': hashlib.sha256(raw).hexdigest(), 'source': str(path.resolve()),
            'counts': counts, 'rows': rows}


def data_context(data):
    # Deliberately expose neither training values nor held-out labels to the LLM.
    return '\n附件数据说明：已由本地校验 CSV，列为 x,y,split；训练行数 %d，留出行数 %d。数据仅在本地拟合，按题意指定阶数或自动选阶。' % (data['counts']['train'], data['counts']['test'])


def fit_polynomial(x, y, degree):
    center, scale = float(np.mean(x)), float(np.std(x))
    if scale == 0 or len(np.unique(x)) < degree + 1:
        raise ValueError('训练数据的不同 x 数量不足，无法辨识该阶多项式')
    design = np.polynomial.polynomial.polyvander((x-center)/scale, degree)
    coef, _, rank, _ = np.linalg.lstsq(design, y, rcond=None)
    if rank != degree + 1 or not np.isfinite(coef).all():
        raise ValueError('拟合矩阵秩不足或数值不稳定')
    return {'center': center, 'scale': scale, 'coefficients': coef.tolist()}


def predict(fit, x):
    values = np.polynomial.polynomial.polyval((np.asarray(x)-fit['center'])/fit['scale'], fit['coefficients'])
    if not np.isfinite(values).all():
        raise ValueError('预测出现非有限数值')
    return values


def metrics(y, predicted):
    error = y-predicted
    result = {'rmse': float(np.sqrt(np.mean(error**2))), 'mae': float(np.mean(np.abs(error)))}
    if not all(np.isfinite(v) for v in result.values()):
        raise ValueError('误差溢出，请检查数据量级')
    return result


def solve_fit(model, data):
    validate_model(model)
    train = [r for r in data['rows'] if r['split'] == 'train']
    x, y = np.array([r['x'] for r in train]), np.array([r['y'] for r in train])
    scores = []
    degree = model['degree']
    if degree is None:
        folds = np.array_split(np.random.default_rng(20261016).permutation(len(x)), 5)
        for candidate in range(1, 6):
            errors = []
            try:
                for validation in folds:
                    keep = np.ones(len(x), dtype=bool)
                    keep[validation] = False
                    fit = fit_polynomial(x[keep], y[keep], candidate)
                    errors.extend((predict(fit, x[validation])-y[validation]).tolist())
                score = metrics(np.array(errors), np.zeros(len(errors)))['rmse']
                scores.append({'degree': candidate, 'cv_rmse': score})
            except ValueError as exc:
                scores.append({'degree': candidate, 'cv_rmse': None, 'reason': str(exc)})
        valid = [s for s in scores if s['cv_rmse'] is not None]
        if not valid:
            raise ValueError('所有候选阶数均无法在训练折上拟合')
        best = min(s['cv_rmse'] for s in valid)
        degree = min(s['degree'] for s in valid if s['cv_rmse'] <= best + 1e-10)
    fit = fit_polynomial(x, y, degree)
    predictions, scores_by_split = [], {}
    for split in ('train', 'test'):
        rows = [r for r in data['rows'] if r['split'] == split]
        yp = predict(fit, [r['x'] for r in rows])
        scores_by_split[split] = metrics(np.array([r['y'] for r in rows]), yp)
        predictions.extend(dict(r, predicted=float(p), residual=float(r['y']-p)) for r, p in zip(rows, yp))
    warnings = []
    if scores_by_split['test']['rmse'] > 2 * max(scores_by_split['train']['rmse'], 1e-10):
        warnings.append('留出 RMSE 超过训练 RMSE 两倍，存在泛化差距；该阈值仅作提示，不能单独证明过拟合。')
    if any(r['x'] < min(x) or r['x'] > max(x) for r in data['rows'] if r['split'] == 'test'):
        warnings.append('部分留出点超出训练 x 范围，属于外推。')
    return {'status': 'fitted', 'degree': degree, 'fit': fit, 'metrics': scores_by_split,
            'selection': 'fixed' if model['degree'] is not None else 'train_only_5fold_cv',
            'seed': 20261016, 'cv_scores': scores, 'warnings': warnings, 'predictions': predictions}


def report_fit(record):
    model = record['envelope']['model']
    lines = ['# 拟合与留出验证报告', '', model['name'], '',
             '模型：y = Σ c[k] z^k，z = (x - center) / scale；使用普通最小二乘。',
             '单位：x 为 '+model['x_unit']+'；y 为 '+model['y_unit']+'。',
             '假设：'+'；'.join(model['assumptions']), '',
             'CSV 快照保存在 run.json 的 dataset；原文件 SHA256：'+record['dataset']['sha256'],
             '留出集仅计算最终误差；自动选阶只使用训练集五折交叉验证。样例属于开发任务，不代表跨题型泛化评测。', '']
    if not record['stages']:
        return '\n'.join(lines+['仅生成模型，尚未拟合。'])+'\n'
    result = record['stages'][0]['result']
    lines += [f"阶数：{result['degree']}；选阶方式：{result['selection']}。", f"参数：{result['fit']}", '',
              '| 数据 | RMSE | MAE |', '|---|---:|---:|']
    for split, m in result['metrics'].items():
        lines.append(f"| {split} | {m['rmse']:.8g} | {m['mae']:.8g} |")
    lines += ['', '训练内候选比较：'+str(result['cv_scores']), '', *result['warnings'], '',
              '逐点预测和残差见 predictions.csv。数据划分及其独立性须由数据提供者确认；当前不支持时间序列或分组交叉验证。']
    return '\n'.join(lines)+'\n'


def save_predictions(record, directory):
    if not record['stages']:
        return
    with (directory/'predictions.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['x', 'y', 'split', 'predicted', 'residual'])
        writer.writeheader()
        writer.writerows(record['stages'][0]['result']['predictions'])
