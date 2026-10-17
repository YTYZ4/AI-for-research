"""Independent fixed graph-unit fixtures; never call runtime conversion to score."""
from fractions import Fraction
from .robustness import unit_score


def provenance_checks(record):
    gen=record.get('generation',{});source=gen.get('source_model',{});audit=gen.get('unit_conversion',{})
    edges=source.get('edges',[]);converted=record['envelope']['model']['edges']
    raw={}
    try:raw=__import__('json').loads(gen['response']['choices'][0]['message']['content'])['model']
    except (KeyError,ValueError,IndexError,TypeError):pass
    checks={'source_preserved':source==raw and source.get('task_type')=='graph_input',
            'quotes_checked':audit.get('source_quotes_checked') is True,
            'edge_count':len(edges)==len(converted)==len(audit.get('edges',[])),
            'quotes_verbatim':all(e['source_quote'] in record['input'] and e['unit_quote'] in record['input'] for e in edges)}
    checks['audit_matches']=checks['edge_count'] and all(
        a['original_weight']==e['weight'] and a['original_unit']==e['unit'] and
        a['source']==e['source']==c['source'] and a['target']==e['target']==c['target'] and
        a['source_quote']==e['source_quote'] and a['unit_quote']==e['unit_quote'] and
        a['normalized_unit']==record['envelope']['model']['unit'] and a['normalized_weight']==c['weight'] and
        float(Fraction(str(e['weight']))*Fraction(a['factor']))==c['weight']
        for e,c,a in zip(edges,converted,audit.get('edges',[])))
    return checks


def score_path_units(case,record,path):
    numeric=unit_score(case,record,path);checks=provenance_checks(record)
    expected={('S','A'):(4000,'米'),('S','B'):(2,'千米'),('B','A'):(1000,'米'),('A','C'):(2,'千米'),('B','C'):(5000,'米'),('C','T'):(3,'千米'),('A','T'):(7,'千米')}
    checks['original_values_units']={(e['source'],e['target']):(e['weight'],e['unit']) for e in record['generation'].get('source_model',{}).get('edges',[])}==expected
    return {'passed':numeric['passed'] and all(checks.values()),'numeric':numeric,'provenance':checks}


def score_boundary(case,record,path):
    checks=provenance_checks(record);m=record['envelope']['model'];r=record['stages'][0]['result']
    raw=record['generation'].get('source_model',{}).get('edges',[])
    expected={(a,b):(w,u) for a,b,w,u in case['source_edges']}
    checks['original_values_units']={(e['source'],e['target']):(e['weight'],e['unit']) for e in raw}==expected
    aliases={'m':{'m','米'},'km':{'km','千米','公里'},'立方米/小时':{'立方米/小时','m3/hour','m³/h','m3/h'}}
    checks['unit']=m['unit'] in aliases[case['unit']]
    checks['edges']={(e['source'],e['target']):e['weight'] for e in m['edges']}=={(e[0],e[1]):w for e,w in zip(case['source_edges'],case['weights'])}
    checks['problem']=m['problem']==case['graph_problem'] and m['source']=='S' and m['target']=='T' and set(m['nodes'])=={'S','A','T'}
    checks['value']=r['value']==case['value']
    if case['graph_problem']=='shortest_path':checks['path']=r['path']==['S','A','T']
    else:
        flows={(e['source'],e['target']):e['flow'] for e in r['flows']}
        checks['flows']=flows=={('S','A'):6,('A','T'):6,('S','T'):5}
    return {'passed':all(checks.values()),'checks':checks}
