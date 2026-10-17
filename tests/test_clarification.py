import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from assistant.cli import main
from assistant.parser import parse_template


class ClarificationTests(unittest.TestCase):
    def test_answer_keeps_question_and_all_paid_responses(self):
        text = (Path(__file__).resolve().parents[1] / "examples/production/problem.txt").read_text()
        missing = {"status": "needs_clarification", "questions": ["煤是否有限？"], "model": None}
        ready = parse_template(text)
        with tempfile.TemporaryDirectory() as temp, patch("builtins.input", side_effect=["原始题目", "", "煤不限"]), patch("assistant.cli.generate", side_effect=[(missing, {"backend": "deepseek"}), (ready, {"backend": "deepseek"})]) as generate, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(["--backend", "deepseek", "--interactive", "--output", temp]), 0)
            self.assertEqual(generate.call_count, 2)
            self.assertIn("原始题目", generate.call_args.args[0])
            self.assertIn("煤不限", generate.call_args.args[0])
            records = [json.loads(p.read_text()) for p in Path(temp).glob("*/run.json")]
            self.assertEqual(len(records), 2)
            solved = next(r for r in records if r["stages"])
            self.assertEqual(solved["original_input"], "原始题目")
            self.assertEqual(solved["clarification_history"][0]["answer"], "煤不限")

    def test_cancel_no_extra_request(self):
        missing = {"status": "needs_clarification", "questions": ["缺少数据"], "model": None}
        with tempfile.TemporaryDirectory() as temp, patch("builtins.input", side_effect=["题目", "", "/quit"]), patch("assistant.cli.generate", return_value=(missing, {"backend": "deepseek"})) as generate, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(["--backend", "deepseek", "--interactive", "--output", temp]), 3)
            self.assertEqual(generate.call_count, 1)
            self.assertEqual(len(list(Path(temp).glob("*/run.json"))), 1)

    def test_followup_failure_preserves_previous_response(self):
        missing = {"status": "needs_clarification", "questions": ["缺少数据"], "model": None}
        with tempfile.TemporaryDirectory() as temp, patch("builtins.input", side_effect=["题目", "", "回答"]), patch("assistant.cli.generate", side_effect=[(missing, {"backend": "deepseek"}), ValueError("network failed")]), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["--backend", "deepseek", "--interactive", "--output", temp]), 2)
            self.assertEqual(len(list(Path(temp).glob("*/run.json"))), 1)

    def test_clarification_round_limit(self):
        missing = {"status": "needs_clarification", "questions": ["缺少数据"], "model": None}
        with tempfile.TemporaryDirectory() as temp, patch("builtins.input", side_effect=["题目", "", "回答"]), patch("assistant.cli.generate", return_value=(missing, {"backend": "deepseek"})) as generate, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(["--backend", "deepseek", "--interactive", "--max-clarifications", "1", "--output", temp]), 3)
            self.assertEqual(generate.call_count, 2)
            self.assertEqual(len(list(Path(temp).glob("*/run.json"))), 2)
