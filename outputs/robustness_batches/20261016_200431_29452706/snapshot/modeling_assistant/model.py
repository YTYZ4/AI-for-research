"""Shared, data-only linear model contract and local validation."""

import math

from jsonschema import Draft202012Validator


class ModelClarificationError(ValueError):
    """A well-formed model has a parameter that requires user correction."""
    def __init__(self, message):
        super().__init__(message)
        self.question = message


def obj(properties):
    return {"type": "object", "properties": properties,
            "required": list(properties), "additionalProperties": False}


TERM = obj({"variable": {"type": "string"}, "coefficient": {"type": "number"}})
TERMS = {"type": "array", "items": TERM}
CONSTRAINT = obj({"name": {"type": "string"}, "terms": TERMS,
                  "sense": {"type": "string", "enum": ["<=", ">=", "="]},
                  "rhs": {"type": "number"}, "unit": {"type": "string"}})
MODEL_SCHEMA = obj({
    "name": {"type": "string"},
    "assumptions": {"type": "array", "items": {"type": "string"}},
    "variables": {"type": "array", "items": obj({
        "name": {"type": "string"}, "description": {"type": "string"},
        "unit": {"type": "string"}, "kind": {"type": "string", "enum": ["integer", "continuous"]},
        "lower": {"type": "number"}, "upper": {"type": ["number", "null"]}})},
    "objective": obj({"sense": {"type": "string", "enum": ["max", "min"]},
                      "terms": TERMS, "unit": {"type": "string"}}),
    "constraints": {"type": "array", "items": CONSTRAINT},
})
FIT_SCHEMA = obj({
    "task_type": {"type": "string", "enum": ["polynomial_fit"]},
    "name": {"type": "string"},
    "assumptions": {"type": "array", "items": {"type": "string"}},
    "degree": {"type": ["integer", "null"], "minimum": 1, "maximum": 5},
    "x_unit": {"type": "string"}, "y_unit": {"type": "string"},
})
DYNAMICS_SCHEMA = obj({
    "task_type": {"type": "string", "enum": ["dynamics"]},
    "name": {"type": "string"},
    "system": {"type": "string", "enum": ["newton_cooling", "logistic"]},
    "initial": {"type": "number"},
    "rate": {"type": "number"},
    "equilibrium": {"type": "number"},
    "duration": {"type": "number"},
    "time_unit": {"type": "string", "enum": ["s", "min", "hour", "day", "year"]},
    "rate_unit": {"type": "string", "enum": ["1/s", "1/min", "1/hour", "1/day", "1/year"]},
    "state_unit": {"type": "string"},
    "assumptions": {"type": "array", "items": {"type": "string"}},
})
GRAPH_SCHEMA = obj({
    "task_type": {"type": "string", "enum": ["graph"]},
    "name": {"type": "string"},
    "problem": {"type": "string", "enum": ["shortest_path", "max_flow"]},
    "nodes": {"type": "array", "items": {"type": "string"}},
    "source": {"type": "string"}, "target": {"type": "string"},
    "edges": {"type": "array", "items": obj({
        "source": {"type": "string"}, "target": {"type": "string"}, "weight": {"type": "number"}})},
    "unit": {"type": "string"},
    "assumptions": {"type": "array", "items": {"type": "string"}},
})
ENVELOPE_SCHEMA = obj({
    "status": {"type": "string", "enum": ["ready", "needs_clarification", "unsupported"]},
    "questions": {"type": "array", "items": {"type": "string"}},
    "model": {"anyOf": [MODEL_SCHEMA, FIT_SCHEMA, DYNAMICS_SCHEMA, GRAPH_SCHEMA, {"type": "null"}]},
})


def validate_model(model):
    if isinstance(model, dict) and model.get("task_type") == "graph":
        errors = list(Draft202012Validator(GRAPH_SCHEMA).iter_errors(model))
        if errors:
            raise ValueError("图模型格式错误：" + errors[0].message)
        nodes = model["nodes"]
        if not 2 <= len(nodes) <= 100 or len(set(nodes)) != len(nodes) or any(not n.strip() for n in nodes):
            raise ValueError("需要2–100个互异非空节点")
        if model["source"] not in nodes or model["target"] not in nodes or model["source"] == model["target"]:
            raise ValueError("起终点必须是图中不同节点")
        if len(model["edges"]) > 500 or not model["unit"].strip():
            raise ValueError("最多500条边且必须说明单位")
        seen = set()
        for edge in model["edges"]:
            u,v,w = edge["source"],edge["target"],edge["weight"]
            if u not in nodes or v not in nodes or u == v or (u,v) in seen:
                raise ValueError("边端点无效、自环或重复有向边；不支持平行边")
            if not math.isfinite(w) or not 0 <= w <= 1e9:
                raise ValueError("边权须有限且在0到1e9之间")
            if model["problem"] == "max_flow" and int(w) != w:
                raise ValueError("当前最大流要求非负整数容量；请明确单位后换算")
            seen.add((u,v))
        return model

    if isinstance(model, dict) and model.get("task_type") == "dynamics":
        errors = list(Draft202012Validator(DYNAMICS_SCHEMA).iter_errors(model))
        if errors:
            raise ValueError("动态模型格式错误：" + errors[0].message)
        for key in ("initial", "rate", "equilibrium", "duration"):
            if not math.isfinite(model[key]) or abs(model[key]) > 1e12:
                raise ValueError("动态模型数值须有限且绝对值不超过1e12")
        if model["rate"] <= 0 or model["duration"] <= 0 or model["rate"] * model["duration"] > 1000:
            raise ModelClarificationError("请核对速率与时长：二者须为正，且当前支持 rate*duration <= 1000；请明确修正值，不会自动修改参数。")
        if model["rate_unit"] != "1/" + model["time_unit"]:
            raise ModelClarificationError("速率单位与时间单位不一致，请确认统一后的速率、时长及单位；不会直接执行混用单位的模型。")
        if not model["state_unit"].strip():
            raise ValueError("状态量单位不能为空")
        if model["system"] == "logistic" and (model["initial"] < 0 or model["equilibrium"] <= 0):
            raise ModelClarificationError("Logistic 初值须非负、环境容量 K 须为正；K=0 时 N/K 无定义。请确认并提供有效的初值和容量，不会擅自替换数值。")
        return model
    if isinstance(model, dict) and model.get("task_type") == "polynomial_fit":
        errors = list(Draft202012Validator(FIT_SCHEMA).iter_errors(model))
        if errors:
            raise ValueError("拟合模型格式错误：" + errors[0].message)
        return model
    errors = sorted(Draft202012Validator(MODEL_SCHEMA).iter_errors(model), key=lambda e: str(e.path))
    if errors:
        raise ValueError("模型格式错误：" + errors[0].message)

    def finite(value):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError("模型数值必须为有限数字")
    variables = model["variables"]
    if not 1 <= len(variables) <= 100 or len(model["constraints"]) > 500:
        raise ValueError("当前限制为 1–100 个变量、最多 500 条约束")
    names = [v["name"] for v in variables]
    if any(not name or not name.isascii() or not name.isidentifier() for name in names):
        raise ValueError("变量名须为 ASCII 标识符，例如 A、B、product_1")
    if len(set(names)) != len(names):
        raise ValueError("变量名重复")
    constraint_names = [c["name"] for c in model["constraints"]]
    if any(not n for n in constraint_names) or len(set(constraint_names)) != len(constraint_names):
        raise ValueError("约束名不能为空或重复")
    for v in variables:
        finite(v["lower"])
        if v["lower"] < 0:
            raise ValueError("当前生产计划只支持非负变量")
        if v["upper"] is not None:
            finite(v["upper"])
            if v["upper"] < v["lower"]:
                raise ValueError("变量上限小于下限")
    for expression in [model["objective"], *model["constraints"]]:
        seen = set()
        if not expression["terms"]:
            raise ValueError("线性表达式不能为空")
        for t in expression["terms"]:
            if t["variable"] not in names:
                raise ValueError("未声明的变量：" + t["variable"])
            if t["variable"] in seen:
                raise ValueError("表达式中变量重复，请合并系数")
            seen.add(t["variable"])
            finite(t["coefficient"])
        if "rhs" in expression:
            finite(expression["rhs"])
    return model


def validate_envelope(envelope):
    errors = list(Draft202012Validator(ENVELOPE_SCHEMA).iter_errors(envelope))
    if errors:
        raise ValueError("建模响应格式错误：" + errors[0].message)
    if envelope["status"] == "ready":
        if envelope["questions"]:
            raise ValueError("仍有待澄清问题，不能标为 ready")
        validate_model(envelope["model"])
    elif envelope["model"] is not None or not envelope["questions"]:
        raise ValueError("未就绪响应必须不含模型，且说明待澄清或不支持的原因")
    return envelope
