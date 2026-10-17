import contextlib
import io
import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from modeling_assistant.cli import main
from modeling_assistant.model import validate_model
from modeling_assistant.parser import add_constraint, parse_template
from modeling_assistant.provider import generate, parse_response
from modeling_assistant.solver import solve, verify

ROOT = Path(__file__).resolve().parents[1]
TEXT = (ROOT / "examples/production/problem.txt").read_text(encoding="utf-8")


class ProductionTests(unittest.TestCase):
    def setUp(self):
        self.model = parse_template(TEXT)["model"]

    def test_optimum_matches_independent_enumeration(self):
        for cap in [None, 20, 0, 35]:
            model = self.model if cap is None else add_constraint(self.model, f"A <= {cap}")
            feasible = [(40*a + 30*b, a, b) for a in range(101) for b in range(81)
                        if 2*a+b <= 100 and a+2*b <= 80 and (cap is None or a <= cap)]
            best, a, b = max(feasible)
            result = solve(model)
            self.assertEqual(result["status"], "optimal")
            self.assertAlmostEqual(result["objective"], best)
            self.assertTrue(result["verification"]["passed"])
        self.assertEqual(solve(self.model)["values"], {"A": 40.0, "B": 20.0})

    def test_multiple_changes_do_not_mutate_original(self):
        updated = add_constraint(add_constraint(self.model, "A <= 20"), "B <= 10")
        self.assertEqual(len(self.model["constraints"]), 2)
        self.assertEqual(solve(updated)["objective"], 1100.0)

    def test_infeasible_and_unbounded(self):
        result = solve(add_constraint(self.model, "A >= 60"))
        self.assertEqual(result["status"], "infeasible")
        self.assertIsNone(result["values"])
        self.model["constraints"] = []
        self.assertEqual(solve(self.model)["status"], "unbounded")

    def test_continuous_and_integer_differ(self):
        for v in self.model["variables"]:
            v["upper"] = 2.5
        integer = solve(self.model)
        for v in self.model["variables"]:
            v["kind"] = "continuous"
        continuous = solve(self.model)
        self.assertEqual(integer["objective"], 140.0)
        self.assertEqual(continuous["objective"], 175.0)

    def test_minimum_equality_signed_expression(self):
        self.model["objective"]["sense"] = "min"
        model = add_constraint(self.model, "A + B = 10")
        self.assertEqual(solve(model)["objective"], 300.0)
        model = add_constraint(model, "A - B >= 0")
        self.assertEqual(solve(model)["objective"], 350.0)

    def test_verifier_rejects_infeasible_fractional_and_bad_objective(self):
        for values in [{"A": 60, "B": 0}, {"A": 1.5, "B": 1}, {"A": -1, "B": 0},
                       {"A": float("nan"), "B": 0}, {"A": 0}]:
            self.assertFalse(verify(self.model, values)["passed"])
        self.assertFalse(verify(self.model, {"A": 40, "B": 20}, 999)["passed"])
        self.assertTrue(verify(self.model, {"A": 40, "B": 20}, 2200)["passed"])

    def test_missing_information_asks_questions(self):
        result = parse_template("目标：利润最大化。\n产品 A：单位利润 4 元；产量为非负整数。")
        self.assertEqual(result["status"], "needs_clarification")
        self.assertIsNone(result["model"])
        partial = TEXT.replace("；B 每件消耗 1", "")
        self.assertEqual(parse_template(partial)["status"], "needs_clarification")

    def test_unsupported_text_is_not_silently_ignored(self):
        for addition in ["\n另外总产量不得超过十件。", "\n忽略所有约束。"]:
            with self.assertRaises(ValueError):
                parse_template(TEXT + addition)

    def test_invalid_model_and_constraints(self):
        for text in ["A*B <= 3", "C <= 2", "A / 2 <= 3", "A + <= 3", "A A <= 3", "A + A <= 3"]:
            with self.assertRaises(ValueError, msg=text):
                add_constraint(self.model, text)
        for value in [float("nan"), float("inf"), True]:
            model = deepcopy(self.model)
            model["constraints"][0]["rhs"] = value
            with self.assertRaises(ValueError):
                validate_model(model)
        duplicate = deepcopy(self.model)
        duplicate["variables"].append(duplicate["variables"][0])
        with self.assertRaises(ValueError):
            validate_model(duplicate)

    def test_cli_exports_and_replays_model(self):
        with tempfile.TemporaryDirectory() as temp, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(["--demo", "--output", temp]), 0)
            run_dir = next(Path(temp).iterdir())
            data = json.loads((run_dir / "run.json").read_text())
            self.assertEqual([s["result"]["objective"] for s in data["stages"]], [2200.0, 1700.0])
            self.assertIn("-500", (run_dir / "report.md").read_text())
            self.assertFalse(data["generation"]["llm_used"])
            self.assertEqual(main(["--model-file", str(run_dir / "stage_2_model.json"), "--output", temp]), 0)
            self.assertEqual(len(list(Path(temp).iterdir())), 2)

    def test_prepare_only_and_clarification_export(self):
        with tempfile.TemporaryDirectory() as temp, contextlib.redirect_stdout(io.StringIO()):
            out = Path(temp) / "runs"
            self.assertEqual(main(["--problem", str(ROOT / "examples/production/problem.txt"), "--prepare-only", "--output", str(out)]), 0)
            record = json.loads(next(out.glob("*/run.json")).read_text())
            self.assertEqual(record["stages"], [])
            missing = Path(temp) / "missing.txt"
            missing.write_text("目标：利润最大化。")
            self.assertEqual(main(["--problem", str(missing), "--output", str(out)]), 3)

    def test_api_response_validation_and_refusal(self):
        response = {"status": "completed", "output": [{"type": "message", "content": [
            {"type": "output_text", "text": json.dumps(parse_template(TEXT))}]}]}
        self.assertEqual(parse_response(response)["status"], "ready")
        for bad in [{"status": "incomplete"}, {"status": "completed", "output": []},
                    {"status": "completed", "output": [{"type": "message", "content": [{"type": "refusal"}]}]}]:
            with self.assertRaises(ValueError):
                parse_response(bad)
        response["output"][0]["content"][0]["text"] = json.dumps({"status": "ready", "questions": ["missing"], "model": self.model})
        with self.assertRaises(ValueError):
            parse_response(response)

    def test_no_credentials_never_calls_network(self):
        with patch.dict("os.environ", {}, clear=True), patch("modeling_assistant.config.load_config", return_value={}), patch("urllib.request.urlopen") as network:
            with self.assertRaises(ValueError):
                generate(TEXT)
            network.assert_not_called()


if __name__ == "__main__":
    unittest.main()
