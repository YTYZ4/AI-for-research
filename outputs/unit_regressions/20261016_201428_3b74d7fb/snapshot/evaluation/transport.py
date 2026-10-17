"""Independent OPT02 development-case checker using original problem data."""

import math

COST = {"W1_S1": 2, "W1_S2": 4, "W1_S3": 5, "W2_S1": 3, "W2_S2": 1, "W2_S3": 7}
SUPPLY = {"W1": 40, "W2": 30}
DEMAND = {"S1": 20, "S2": 30, "S3": 20}


def evaluate_plan(plan, claimed_cost=None):
    """plan keys are canonical route IDs, mapped by an offline reviewer.

    Does not read the model's constraints, solver status, or verification fields.
    """
    if set(plan) != set(COST) or any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in plan.values()):
        return {"passed": False, "reason": "六条路线必须完整且数值有限"}
    checks = {"nonnegative": all(v >= -1e-6 for v in plan.values())}
    for warehouse, cap in SUPPLY.items():
        checks[warehouse] = sum(plan[f"{warehouse}_{shop}"] for shop in DEMAND) <= cap + 1e-6
    for shop, need in DEMAND.items():
        checks[shop] = abs(sum(plan[f"{warehouse}_{shop}"] for warehouse in SUPPLY) - need) <= 1e-6
    cost = sum(COST[route] * value for route, value in plan.items())
    # Every demand unit must pay at least that destination's cheapest route.
    lower_bound = sum(need * min(COST[f"{warehouse}_{shop}"] for warehouse in SUPPLY) for shop, need in DEMAND.items())
    checks["optimal_cost"] = abs(cost - lower_bound) <= 1e-6
    if claimed_cost is not None:
        checks["claimed_cost"] = isinstance(claimed_cost, (int, float)) and math.isfinite(claimed_cost) and abs(claimed_cost - cost) <= 1e-6
    return {"passed": all(checks.values()), "checks": checks, "cost": cost, "proven_lower_bound": lower_bound,
            "scope": "仅适用于 OPT02 原始开发数据；不评价自然语言建模完整性。"}
