"""Solve data-only linear models, independently recompute feasibility."""

import math
import time
from copy import deepcopy

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp

from .model import validate_model


def evaluate(terms, values):
    return sum(t["coefficient"] * values[t["variable"]] for t in terms)


def verify(model, values, claimed_objective=None, tolerance=1e-6):
    validate_model(model)
    expected = {v["name"] for v in model["variables"]}
    if set(values) != expected or any(isinstance(x, bool) or not isinstance(x, (float, int)) or not math.isfinite(x) for x in values.values()):
        return {"passed": False, "checks": [{"name": "解的变量与数值", "passed": False}], "objective_recomputed": None}
    checks = []
    for v in model["variables"]:
        x = values[v["name"]]
        checks.append({"name": v["name"] + " 下界", "passed": x >= v["lower"] - tolerance})
        if v["upper"] is not None:
            checks.append({"name": v["name"] + " 上界", "passed": x <= v["upper"] + tolerance})
        if v["kind"] == "integer":
            checks.append({"name": v["name"] + " 整数性", "passed": abs(x - round(x)) <= tolerance})
    for constraint in model["constraints"]:
        lhs, rhs = evaluate(constraint["terms"], values), constraint["rhs"]
        delta = lhs - rhs
        violation = {"<=": max(0, delta), ">=": max(0, -delta), "=": abs(delta)}[constraint["sense"]]
        checks.append({"name": constraint["name"], "lhs": lhs, "sense": constraint["sense"], "rhs": rhs,
                       "violation": violation, "passed": violation <= tolerance})
    objective = evaluate(model["objective"]["terms"], values)
    if claimed_objective is not None:
        checks.append({"name": "目标值复算", "passed": math.isfinite(claimed_objective) and math.isclose(objective, claimed_objective, abs_tol=tolerance, rel_tol=1e-9)})
    return {"passed": all(c["passed"] for c in checks), "checks": checks, "objective_recomputed": objective,
            "scope": "仅检查给定模型下的可行性及目标复算；不证明自然语言建模完整或解全局最优。"}


def _solve(model, time_limit=10.0):
    validate_model(model)
    names = [v["name"] for v in model["variables"]]
    def vector(terms):
        mapping = {t["variable"]: t["coefficient"] for t in terms}
        return [mapping.get(n, 0) for n in names]
    sign = -1 if model["objective"]["sense"] == "max" else 1
    constraints = model["constraints"]
    linear = None
    if constraints:
        linear = LinearConstraint(np.array([vector(c["terms"]) for c in constraints]),
                                  [c["rhs"] if c["sense"] in (">=", "=") else -np.inf for c in constraints],
                                  [c["rhs"] if c["sense"] in ("<=", "=") else np.inf for c in constraints])
    started = time.perf_counter()
    result = milp(c=sign * np.array(vector(model["objective"]["terms"]), dtype=float),
                  integrality=[int(v["kind"] == "integer") for v in model["variables"]],
                  bounds=Bounds([v["lower"] for v in model["variables"]], [np.inf if v["upper"] is None else v["upper"] for v in model["variables"]]),
                  constraints=linear, options={"time_limit": time_limit, "mip_rel_gap": 0.0, "presolve": False})
    status = {0: "optimal", 1: "limit_reached", 2: "infeasible", 3: "unbounded", 4: "solver_error"}.get(result.status, "solver_error")
    output = {"status": status, "solver": "scipy.optimize.milp/HiGHS", "message": result.message,
              "elapsed_seconds": time.perf_counter() - started, "values": None, "objective": None, "verification": None}
    if result.x is not None and np.all(np.isfinite(result.x)):
        values = {name: float(x) for name, x in zip(names, result.x)}
        output.update(values=values, objective=float(sign * result.fun))
        output["verification"] = verify(model, values, output["objective"])
        if not output["verification"]["passed"]:
            output["status"] = "verification_failed"
    return output


def interval_contradiction(model):
    """Explain a two-variable contradiction by eliminating one equality.

    This is algebra over the supplied model, not a language-model guess.
    """
    if len(model["variables"]) != 2:
        return None
    x, y = [v["name"] for v in model["variables"]]
    for equality in model["constraints"]:
        if equality["sense"] != "=":
            continue
        coefs = {t["variable"]: t["coefficient"] for t in equality["terms"]}
        a, b = coefs.get(x, 0), coefs.get(y, 0)
        if abs(a) < 1e-10:
            continue
        lower, upper = [], []
        for constraint in model["constraints"]:
            if constraint is equality:
                continue
            terms = {t["variable"]: t["coefficient"] for t in constraint["terms"]}
            slope = terms.get(y, 0) - terms.get(x, 0) * b / a
            rhs = constraint["rhs"] - terms.get(x, 0) * equality["rhs"] / a
            if abs(slope) < 1e-10:
                continue
            bound = rhs / slope
            sense = constraint["sense"]
            if slope < 0:
                sense = {"<=": ">=", ">=": "<=", "=": "="}[sense]
            if sense in (">=", "="):
                lower.append((bound, constraint["name"]))
            if sense in ("<=", "="):
                upper.append((bound, constraint["name"]))
        if lower and upper:
            lo, loname = max(lower)
            hi, hiname = min(upper)
            if lo > hi + 1e-6:
                unit = model["variables"][1]["unit"]
                text = (f"结合“{equality['name']}”，由“{loname}”可得 {y} >= {lo:g} {unit}；"
                        f"由“{hiname}”可得 {y} <= {hi:g} {unit}。上下界矛盾，无法同时满足。")
                if a == b == equality["rhs"] == 1:
                    text += f"在总量为 1 的归一化模型中，即占比至少 {lo:.1%}，却又至多 {hi:.1%}。"
                return text
    return None


def explain_infeasible(model):
    direct = interval_contradiction(model)
    if direct:
        return {"method": "equality_elimination", "summary": direct}
    # Deletion filter keeps a solver-confirmed infeasible subset, with original
    # bounds/integrality unchanged. Timeouts never justify discarding a row.
    if len(model["constraints"]) > 12 or len(model["variables"]) > 20:
        return {"method": "status_only", "summary": "给定约束、变量上下界和整数要求无法同时满足。模型较大，本次未定位具体冲突，不自动放宽条件。"}
    candidate = deepcopy(model)
    for term in candidate["objective"]["terms"]:
        term["coefficient"] = 0
    deadline = time.perf_counter() + 5
    for constraint in list(candidate["constraints"]):
        remaining = deadline - time.perf_counter()
        if remaining <= 0:
            break
        trial = deepcopy(candidate)
        trial["constraints"] = [c for c in trial["constraints"] if c["name"] != constraint["name"]]
        if _solve(trial, time_limit=min(1.0, remaining))["status"] == "infeasible":
            candidate = trial
    names = [c["name"] for c in candidate["constraints"]]
    return {"method": "deletion_filter", "constraint_names": names,
            "summary": "以下约束在保持变量上下界和整数要求时仍无法同时满足：" + ("、".join(names) or "仅变量上下界和整数要求") + "。这是已验证的冲突组，不保证约束条数最少；请核对业务条件，不自动删除限制。"}


def solve(model):
    output = _solve(model)
    if output["status"] == "infeasible":
        output["infeasibility_explanation"] = explain_infeasible(model)
    return output
