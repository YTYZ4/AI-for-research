"""Independent original-problem oracle for DYN01/DYN02 development fixtures."""
import math


def evaluate_run(record, case):
    if case not in ('cooling','logistic'):
        raise ValueError('仅支持两个固定开发题')
    expected = dict(system='newton_cooling',initial=90,rate=.1,equilibrium=20,duration=30,time_unit='min',rate_unit='1/min') if case=='cooling' else dict(system='logistic',initial=100,rate=.2,equilibrium=1000,duration=30,time_unit='day',rate_unit='1/day')
    model=record['envelope']['model'];result=record['stages'][0]['result']
    checks={'original_parameters':all(model.get(k)==v for k,v in expected.items())}
    trajectory=result['trajectory']
    checks['grid']=len(trajectory)==101 and all(abs(row['time']-.3*i)<1e-10 for i,row in enumerate(trajectory))
    errors=[]
    for row in trajectory:
        t=row['time']
        target=20+70*math.exp(-.1*t) if case=='cooling' else 1000/(1+9*math.exp(-.2*t))
        errors.append(abs(row['value']-target))
    checks['original_problem_trajectory']=bool(errors) and all(math.isfinite(e) and e<1e-5 for e in errors)
    checks['final_consistency']=bool(trajectory) and abs(result['final_value']-trajectory[-1]['value'])<1e-10
    return {'passed':all(checks.values()),'checks':checks,'absolute_tolerance':1e-5,'max_error':max(errors) if errors else None,
            'scope':'原题固定参数和解析解独立复算；不评价其他动态问题或自然语言改写成功率'}
