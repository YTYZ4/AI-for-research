"""Bounded, predefined ODE systems; no generated code is executed."""
import csv
import numpy as np
from scipy.integrate import solve_ivp
from scipy.special import expit
from .model import validate_model


def solve_dynamics(model):
    validate_model(model)
    initial, rate, equilibrium, duration = (model[k] for k in ('initial','rate','equilibrium','duration'))
    times = np.linspace(0, duration, 101)
    calls = 0
    def rhs(t, y):
        nonlocal calls
        calls += 1
        if calls > 50000:
            raise ValueError('积分超过50000次函数计算上限，请缩短时长或检查参数')
        value = -rate*(y[0]-equilibrium) if model['system']=='newton_cooling' else rate*y[0]*(1-y[0]/equilibrium)
        if not np.isfinite(value):
            raise ValueError('积分导数溢出，请检查参数量级')
        return [value]
    solution = solve_ivp(rhs, (0,duration), [initial], t_eval=times, rtol=1e-9, atol=1e-10)
    if not solution.success or len(solution.t)!=len(times) or not np.isfinite(solution.y).all():
        raise ValueError('数值积分未完成或出现非有限结果')
    numerical = solution.y[0]
    decay = np.exp(-rate*times)
    if model['system']=='newton_cooling':
        reference = equilibrium + (initial-equilibrium)*decay
    elif initial==0:
        reference = np.zeros_like(times)
    elif initial < equilibrium:
        log_odds = np.log(initial) - np.log(equilibrium) - np.log1p(-initial/equilibrium)
        reference = equilibrium * expit(log_odds + rate*times)
        reference[0] = initial
    else:
        reference = equilibrium / (decay*(equilibrium/initial) + (1-decay))
        reference[0] = initial
    if not np.isfinite(reference).all():
        raise ValueError('解析对照数值溢出')
    tolerance = 1e-7 * max(1, abs(initial), abs(equilibrium))
    lower = min(initial, equilibrium) if model['system']=='newton_cooling' or initial>0 else 0
    upper = max(initial,equilibrium)
    checks = {'initial_condition': bool(abs(numerical[0]-initial)<=tolerance),
              'analytic_agreement': bool(np.max(abs(numerical-reference))<=tolerance),
              'physical_bounds': bool(np.all(numerical>=lower-tolerance) and np.all(numerical<=upper+tolerance))}
    direction = np.sign(equilibrium-initial)
    checks['monotonic_toward_equilibrium'] = bool(np.all(direction*np.diff(numerical)>=-tolerance))
    return {'status':'simulated' if all(checks.values()) else 'verification_failed',
            'solver':'scipy.integrate.solve_ivp/RK45', 'rtol':1e-9, 'atol':1e-10,
            'function_evaluations':calls, 'final_value':float(numerical[-1]),
            'max_absolute_error':float(np.max(abs(numerical-reference))),
            'verification':{'passed':all(checks.values()),'tolerance':tolerance,'checks':checks},
            'trajectory':[{'time':float(t),'value':float(y),'analytic':float(a),'absolute_error':float(abs(y-a))} for t,y,a in zip(times,numerical,reference)]}


def report_dynamics(record):
    model = record['envelope']['model']
    equation = 'dT/dt = -k(T−T_env)' if model['system']=='newton_cooling' else 'dN/dt = rN(1−N/K)'
    lines = ['# 动态系统建模与求解报告','',model['name'],'',f'方程：{equation}；t=0 时状态为 {model["initial"]} {model["state_unit"]}。',
             f'速率：{model["rate"]} {model["rate_unit"]}；平衡参数（环境温度或容量）：{model["equilibrium"]} {model["state_unit"]}。',
             f'时间区间：[0, {model["duration"]}] {model["time_unit"]}；输出101个等距采样点。','',
             '假设：'+'；'.join(model['assumptions']),'',
             '单位检查仅核对结构化速率与时间的兼容性；需人工核对原题换算、参数、初值和方程。解析解对照验证数值积分，不证明题意建模正确。','']
    if record['stages']:
        r=record['stages'][0]['result']
        lines += [f"状态：{r['status']}；末时刻值：{r['final_value']:.10g} {model['state_unit']}。",f"解析解对照最大绝对误差：{r['max_absolute_error']:.6g}；容差：{r['verification']['tolerance']:.6g}。",'', '| 检查 | 通过 |','|---|---|']
        lines += [f"| {k} | {'是' if v else '否'} |" for k,v in r['verification']['checks'].items()]
        lines += ['', '完整轨迹见 trajectory.csv。当前为常参数初值问题，不支持参数估计、事件时间求解或任意微分方程。']
    else:
        lines += ['仅生成模型，尚未积分。']
    return '\n'.join(lines)+'\n'


def save_trajectory(record,directory):
    if not record['stages']:
        return
    with (directory/'trajectory.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=['time','value','analytic','absolute_error'])
        writer.writeheader()
        writer.writerows(record['stages'][0]['result']['trajectory'])
