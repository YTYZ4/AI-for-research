"""Fixed-task explanation checks, independent from generation and runtime routing."""
import re

def refusal_score(envelope,topic):
    text='；'.join(envelope.get('questions',[]))
    checks={
        'unsupported':envelope.get('status')=='unsupported',
        'no_model':envelope.get('model') is None,
        'nonblank_explanations':bool(envelope.get('questions')) and all(q.strip() for q in envelope.get('questions',[])),
        'identifies_requested_scope':bool(re.search(topic,text,re.I)),
        'explains_limit':bool(re.search(r'不支持|未支持|尚未|仅支持|只支持|超出|范围|限制|无法',text)),
        'no_invented_contract_limit':not bool(re.search(r'(?:Schema|schema|JSON|引用字段).{0,20}(?:不支持|缺少|无法)|不能.{0,8}换算|仅支持原.{0,3}单位',text)),
        'no_silent_downgrade':not bool(re.search(r'(?:建议|可以|已|将).{0,8}(?:忽略费用|忽略成本|改为普通最大流)',text)),
    }
    return {'passed':all(checks.values()),'checks':checks,'text':text}
