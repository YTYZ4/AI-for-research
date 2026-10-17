import unittest
from copy import deepcopy

from modeling_assistant.solver import interval_contradiction, solve


def blend():
    def row(name, a, b, sense, rhs):
        return {"name": name, "terms": [{"variable": "a", "coefficient": a}, {"variable": "b", "coefficient": b}], "sense": sense, "rhs": rhs, "unit": "kg"}
    return {"name": "blend", "assumptions": ["1kg basis"],
            "variables": [{"name": n, "description": n, "unit": "kg", "kind": "continuous", "lower": 0, "upper": None} for n in ("a", "b")],
            "objective": {"sense": "min", "terms": [{"variable": "a", "coefficient": 2}, {"variable": "b", "coefficient": 3}], "unit": "yuan"},
            "constraints": [row("mass", 1, 1, "=", 1), row("protein", .2, .3, ">=", .25), row("fat", .1, .05, ">=", .08)]}


class ExplanationTests(unittest.TestCase):
    def test_blend_algebra_and_feasible_neighbor(self):
        model = blend()
        result = solve(model)
        self.assertEqual(result["status"], "infeasible")
        text = result["infeasibility_explanation"]["summary"]
        self.assertIn("50.0%", text)
        self.assertIn("40.0%", text)
        model["constraints"][2]["rhs"] = .07
        self.assertIsNone(interval_contradiction(model))
        result = solve(model)
        self.assertEqual(result["status"], "optimal")
        self.assertNotIn("infeasibility_explanation", result)

    def test_elimination_with_reversed_variable_order(self):
        model = blend()
        model["variables"].reverse()
        text = interval_contradiction(model)
        self.assertIn("60.0%", text)
        self.assertIn("50.0%", text)

    def test_integer_only_conflict_and_irrelevant_constraint(self):
        model = blend()
        model["variables"] = model["variables"][:1]
        model["variables"][0]["kind"] = "integer"
        model["objective"]["terms"] = [{"variable": "a", "coefficient": 1}]
        model["constraints"] = [{"name": "half", "terms": [{"variable": "a", "coefficient": 1}], "sense": "=", "rhs": .5, "unit": "piece"},
                                {"name": "irrelevant", "terms": [{"variable": "a", "coefficient": 1}], "sense": "<=", "rhs": 100, "unit": "piece"}]
        original = deepcopy(model)
        result = solve(model)
        self.assertEqual(result["status"], "infeasible")
        self.assertEqual(result["infeasibility_explanation"]["constraint_names"], ["half"])
        self.assertEqual(model, original)
        model["variables"][0]["kind"] = "continuous"
        self.assertEqual(solve(model)["status"], "optimal")
