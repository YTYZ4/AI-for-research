"""Bounded graph explanation oracles, using frozen case expectations, not runtime routing."""
import re

def direction_score(envelope):
    text='；'.join(envelope.get('questions',[]))
    topic=bool(re.search(r'方向|有向|无向|双向|单向|从.{0,12}(?:到|指向)|哪.{0,8}指向|流向',text))
    asks=bool(re.search(r'请|需要明确|需明确|哪|还是|是否|能否|补充|提供|确认|告知',text))
    choice=bool(re.search(r'默认|假设.{0,12}(?:方向|双向|单向|S|T)|(?:已(?:经)?(?:选定|设定|假定|采用)|先按|暂按|直接按).{0,12}(?:方向|S|T|双向|单向)|无需.{0,8}(?:确认|补充|方向)|方向已明确',text))
    checks={'clarification':envelope.get('status')=='needs_clarification',
            'no_model':envelope.get('model') is None,
            'nonblank':bool(envelope.get('questions')) and all(q.strip() for q in envelope.get('questions',[])),
            'asks_direction':topic and asks,'no_assumed_direction':not choice}
    return {'passed':all(checks.values()),'checks':checks,'text':text}


def explanation_extras(envelope,present_fields=()):
    text='；'.join(envelope.get('questions',[]))
    # Scan each clause separately: "不能改为...，请改为..." must still fail.
    changes=[];missing=[]
    for clause in re.split(r'[，。；;\n]|但是|但|不过',text):
        negative=bool(re.search(r'不得|不能|不应|不会|无需|不要|不建议|不要求',clause))
        if not negative and re.search(r'(?:请|建议|可以|可|改为|移除|去掉|删除).{0,25}(?:改为|移除|去掉|删除|忽略|放弃|仅求|只求|只要求)',clause):
            changes.append(clause)
        # Include leading request to change, without requiring a second verb.
        if not negative and re.search(r'^(?:请)?(?:改为|移除|去掉|删除|忽略|放弃).*(?:目标|费用|成本|任务|最大流|最短路径)',clause):
            changes.append(clause)
        if not negative and re.search(r'(?:请|建议|可以|可|需要).{0,12}(?:拆分|分开|分别提交|一次只提交|只提交其中|单独提交)',clause):
            changes.append(clause)
        for field in present_fields:
            if re.search(r'(?:未提供|未给出|没有给出|缺少|缺乏|缺失|尚未明确).{0,40}'+field,clause):
                missing.append({'field':field,'clause':clause})
    return {'passed':not changes and not missing,
            'checks':{'no_task_change_suggestions':not changes,'no_false_missing_claims':not missing},
            'task_change_clauses':changes,'false_missing_claims':missing}
