"""Strict offline template parser, explicitly not a language model."""

import re
from copy import deepcopy

from .model import validate_model

NUMBER = r"(?:\d+(?:\.\d*)?|\.\d+)"
ID = r"[A-Za-z_][A-Za-z_0-9]*"


def parse_constraint(text, names, name="追加约束"):
    text = text.strip().rstrip("。")
    match = re.fullmatch(r"(.+?)\s*(<=|>=|=)\s*(-?" + NUMBER + r")", text)
    if not match:
        raise ValueError("约束格式应为 A + 2*B <= 40（支持 <=、>=、=）")
    lhs, sense, rhs = match.groups()
    compact = re.sub(r"\s+", "", lhs)
    pattern = re.compile(r"([+-]?)(?:(" + NUMBER + r")\*?)?(" + ID + r")")
    terms, end = [], 0
    for token in pattern.finditer(compact):
        if token.start() != end or (end and not token.group(1)):
            raise ValueError("无法解析线性表达式：" + lhs)
        sign, value, variable = token.groups()
        if variable not in names:
            raise ValueError("约束包含未知变量：" + variable)
        terms.append({"variable": variable, "coefficient": (-1 if sign == "-" else 1) * float(value or 1)})
        end = token.end()
    if end != len(compact) or not terms:
        raise ValueError("无法解析线性表达式：" + lhs)
    return {"name": name, "terms": terms, "sense": sense, "rhs": float(rhs), "unit": "按原模型单位"}


def add_constraint(model, text):
    updated = deepcopy(model)
    names = {c["name"] for c in model["constraints"]}
    i = 1
    while f"追加约束_{i}" in names:
        i += 1
    updated["constraints"].append(parse_constraint(text, [v["name"] for v in model["variables"]], f"追加约束_{i}"))
    return validate_model(updated)


def parse_template(text):
    """Parse every nonblank line; unknown content never silently disappears."""
    products, resources, extra = [], [], []
    objective = False
    for raw in text.splitlines():
        line = raw.strip().rstrip("。")
        if not line:
            continue
        if line == "目标：利润最大化":
            if objective:
                raise ValueError("目标重复")
            objective = True
            continue
        product = re.fullmatch(r"产品\s+(" + ID + r")：单位利润\s+(-?" + NUMBER + r")\s+元；产量为非负(整数|实数)", line)
        if product:
            name, profit, kind = product.groups()
            products.append((name, float(profit), kind))
            continue
        resource = re.fullmatch(r"资源\s+([^：]+)：上限\s+(" + NUMBER + r")；(.+)", line)
        if resource:
            name, limit, usages = resource.groups()
            terms = []
            for usage in usages.split("；"):
                term = re.fullmatch(r"\s*(" + ID + r")\s+每件消耗\s+(" + NUMBER + r")\s*", usage)
                if not term:
                    raise ValueError("资源消耗格式无法识别：" + usage)
                terms.append({"variable": term[1], "coefficient": float(term[2])})
            resources.append({"name": name, "terms": terms, "sense": "<=", "rhs": float(limit), "unit": name})
            continue
        if line.startswith("约束："):
            extra.append(line[len("约束："):])
            continue
        raise ValueError("离线模板无法识别此行；请使用示例格式或 openai 后端：" + line)
    questions = []
    if not objective:
        questions.append("请提供：目标：利润最大化。")
    if not products:
        questions.append("请提供产品、单位利润，以及产量为非负整数或实数。")
    if not resources:
        questions.append("请提供资源上限和每种产品的单位消耗。")
    names = [p[0] for p in products]
    for r in resources:
        if set(t["variable"] for t in r["terms"]) != set(names):
            questions.append(f"资源 {r['name']} 请明确列出每种产品的消耗；不消耗时填 0。")
    if questions:
        return {"status": "needs_clarification", "questions": questions, "model": None}
    model = {
        "name": "生产计划", "assumptions": ["单位利润和资源消耗固定，收益与产量线性相加。", "仅考虑输入中列出的限制；现实条件完整性需用户确认。"],
        "variables": [{"name": name, "description": f"产品 {name} 产量", "unit": "件", "kind": "integer" if kind == "整数" else "continuous", "lower": 0, "upper": None} for name, _, kind in products],
        "objective": {"sense": "max", "terms": [{"variable": name, "coefficient": profit} for name, profit, _ in products], "unit": "元"},
        "constraints": resources,
    }
    validate_model(model)
    for constraint in extra:
        model = add_constraint(model, constraint)
    return {"status": "ready", "questions": [], "model": model}
