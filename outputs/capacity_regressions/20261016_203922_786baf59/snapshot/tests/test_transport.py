import json
import unittest
from pathlib import Path

from modeling_assistant.solver import solve
from evaluation.transport import evaluate_plan


class TransportTests(unittest.TestCase):
    def setUp(self):
        self.model = json.loads((Path(__file__).resolve().parents[1] / "examples/transport/reference_model.json").read_text())

    def test_transport_matches_independent_cost_lower_bound(self):
        result = solve(self.model)
        self.assertEqual(result["status"], "optimal")
        # Any delivery costs at least the cheapest route for each destination.
        lower_bound = 20 * min(2, 3) + 30 * min(4, 1) + 20 * min(5, 7)
        self.assertEqual(result["objective"], lower_bound)
        self.assertTrue(evaluate_plan(result["values"], result["objective"])["passed"])
        x = result["values"]
        self.assertAlmostEqual(sum(x[f'W1_S{j}'] for j in [1, 2, 3]), 40)
        self.assertAlmostEqual(sum(x[f'W2_S{j}'] for j in [1, 2, 3]), 30)
        for j, demand in [(1, 20), (2, 30), (3, 20)]:
            self.assertAlmostEqual(x[f'W1_S{j}'] + x[f'W2_S{j}'], demand)

    def test_independent_checker_rejects_missing_demand_and_wrong_cost(self):
        plan = {"W1_S1": 20, "W1_S2": 0, "W1_S3": 20, "W2_S1": 0, "W2_S2": 30, "W2_S3": 0}
        self.assertFalse(evaluate_plan(plan, 100)["passed"])
        plan["W2_S2"] = 0
        self.assertFalse(evaluate_plan(plan)["passed"])
        plan["W2_S2"] = float("nan")
        self.assertFalse(evaluate_plan(plan)["passed"])

    def test_shortage_is_infeasible_without_dummy_supply(self):
        self.model["constraints"][0]["rhs"] = 30
        result = solve(self.model)
        self.assertEqual(result["status"], "infeasible")
        self.assertIn("infeasibility_explanation", result)

    def test_fractional_production_requires_integer_domain(self):
        self.model = {"name": "integer counterexample", "assumptions": [],
            "variables": [{"name": "x", "description": "整件产品", "unit": "件", "kind": "integer", "lower": 0, "upper": None}],
            "objective": {"sense": "max", "terms": [{"variable": "x", "coefficient": 10}], "unit": "元"},
            "constraints": [{"name": "工时", "terms": [{"variable": "x", "coefficient": 2}], "sense": "<=", "rhs": 5, "unit": "小时"}]}
        self.assertEqual(solve(self.model)["objective"], 20)
        self.model["variables"][0]["kind"] = "continuous"
        self.assertEqual(solve(self.model)["objective"], 25)
