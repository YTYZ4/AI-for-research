"""Fixed descriptions of system behavior; model assumptions are not UI promises."""
import copy
import re

# Suppress only display of obvious system/output claims; never delete source data.
SYSTEM_CLAIM=re.compile(r'求解器|程序|--data|schema|API|source_quotes|(?:系统|软件|工具).{0,12}(?:输出|保存|计算|生成|换算|展示)|(?:报告|文件).{0,8}(?:保存|生成|展示)|(?:保存|生成).{0,8}(?:报告|文件)|输出.{0,8}(?:系数|文件)|本地.{0,8}(?:计算|换算|求解)' ,re.I)


def presentation_record(record):
    shown=copy.deepcopy(record);hidden=[]
    for location,model in [('envelope',shown['envelope'].get('model'))]+[(f'stage_{i+1}',s['model']) for i,s in enumerate(shown['stages'])]:
        if not model:continue
        kept=[]
        for a in model.get('assumptions',[]):
            if SYSTEM_CLAIM.search(a):hidden.append({'location':location,'text':a,'reason':'包含系统行为或实现描述，移到原始记录，不作为报告假设展示'})
            else:kept.append(a)
        model['assumptions']=kept
    return shown,{'policy':'fixed_system_descriptions_v2','suppressed_display_only':hidden,'source_modified':False}


def system_description(record):
    model=record['envelope'].get('model')
    if model is None:
        if record['envelope']['status']=='unsupported':return '系统未执行求解。给定问题超出当前支持范围；原题条件保持不变，原因见上方说明。'
        return '系统尚未求解，需要补充题目实际缺失或待澄清的条件。'
    kind=model.get('task_type');done=bool(record['stages'])
    if kind=='polynomial_fit':
        return ('系统使用本地普通最小二乘计算并保存拟合系数；结果报告展示系数、训练/留出误差，predictions.csv保存逐点预测和残差。' if done else '本次仅生成拟合规格，尚未计算系数。求解后，系统会保存并在报告中展示系数、误差和逐点预测。')
    if kind=='dynamics':return '系统在本地完成已支持的时间单位换算、数值积分与解析解对照；仅生成模式不会执行积分。原始参数和换算记录按实际运行情况保存。'
    if kind=='graph':return '系统在本地计算路径或流量，并输出适用的距离标签或最小割验证；仅生成模式不求解。'
    return '系统在本地求解线性/整数模型并复核约束与目标；仅生成模式不求解。原题含义仍需对照模型审核。'
