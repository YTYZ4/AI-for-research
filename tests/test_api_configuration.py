import contextlib
import io
import json
import os
import socket
import ssl
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from assistant.cli import main
from assistant.config import credentials, load_config, save_config
from assistant.configure import main as configure
from assistant.parser import parse_template
from assistant.provider import generate, parse_deepseek_response
from assistant.provider import connection_error_message

TEXT = (Path(__file__).resolve().parents[1] / "examples/production/problem.txt").read_text()


class ConfigurationTests(unittest.TestCase):
    def test_distinct_connection_errors(self):
        self.assertIn("证书", connection_error_message(ssl.SSLCertVerificationError(1, "verification failed")))
        self.assertIn("超时", connection_error_message(TimeoutError()))
        self.assertIn("域名解析", connection_error_message(socket.gaierror()))
        self.assertIn("网络连接", connection_error_message(ConnectionRefusedError()))

    def test_provider_credentials_are_isolated(self):
        with tempfile.TemporaryDirectory() as temp, patch.dict(os.environ, {}, clear=True), patch("assistant.config.config_path", side_effect=lambda backend="openai": Path(temp) / (backend + ".json")):
            save_config("openai-secret", "openai-model")
            save_config("deepseek-secret", "deepseek-flash", "deepseek")
            with patch.dict(os.environ, {"OPENAI_API_KEY": "env-openai", "MODEL_ASSISTANT_MODEL": "env-openai-model"}):
                self.assertEqual(credentials(backend="deepseek"), ("deepseek-secret", "deepseek-flash"))
                self.assertEqual(credentials(), ("env-openai", "env-openai-model"))
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(configure(["--provider", "deepseek", "--check"]), 0)
            self.assertNotIn("deepseek-secret", output.getvalue())

    def test_deepseek_request_and_full_solution_mock(self):
        response = {"model": "deepseek-flash", "usage": {"prompt_tokens": 100, "completion_tokens": 200},
                    "choices": [{"finish_reason": "stop", "message": {"content": json.dumps(parse_template(TEXT))}}]}
        with tempfile.TemporaryDirectory() as temp, patch.dict(os.environ, {"DEEPSEEK_API_KEY": "ds-secret", "DEEPSEEK_MODEL": "deepseek-flash"}), patch("urllib.request.urlopen") as request, contextlib.redirect_stdout(io.StringIO()):
            request.return_value.__enter__.return_value = io.BytesIO(json.dumps(response).encode("utf-8"))
            self.assertEqual(main(["--backend", "deepseek", "--text", "自由输入测试", "--output", temp]), 0)
            outgoing = request.call_args.args[0]
            self.assertTrue(request.call_args.kwargs["context"].check_hostname)
            self.assertEqual(request.call_args.kwargs["context"].verify_mode, ssl.CERT_REQUIRED)
            self.assertEqual(outgoing.full_url, "https://api.deepseek.com/chat/completions")
            payload = json.loads(outgoing.data)
            self.assertEqual(payload["response_format"], {"type": "json_object"})
            self.assertEqual(payload["messages"][-1]["content"], "自由输入测试")
            self.assertNotIn("text", payload)
            record_text = next(Path(temp).glob("*/run.json")).read_text()
            self.assertNotIn("ds-secret", record_text)
            record = json.loads(record_text)
            self.assertEqual(record["backend"], "deepseek")
            self.assertEqual(record["stages"][0]["result"]["objective"], 2200)

    def test_deepseek_malformed_empty_and_truncated_responses(self):
        for response in [{}, {"choices": []}, {"choices": [{"finish_reason": "length", "message": {"content": "{}"}}]},
                         {"choices": [{"finish_reason": "stop", "message": {"content": ""}}]},
                         {"choices": [{"finish_reason": "stop", "message": {"content": "not json"}}]},
                         {"choices": [{"finish_reason": "stop", "message": {"content": "{}"}}]}]:
            with self.assertRaises(ValueError):
                parse_deepseek_response(response)
        with patch.dict(os.environ, {}, clear=True), patch("assistant.config.load_config", return_value={}), patch("urllib.request.urlopen") as request:
            with self.assertRaises(ValueError):
                generate("test", backend="deepseek")
            request.assert_not_called()

    def test_private_file_and_environment_precedence(self):
        with tempfile.TemporaryDirectory() as temp, patch.dict(os.environ, {}, clear=True):
            path = Path(temp) / "settings" / "openai.json"
            with patch("assistant.config.config_path", return_value=path):
                save_config("dummy-secret", "local-model")
                self.assertEqual(path.stat().st_mode & 0o777, 0o600)
                self.assertEqual(credentials(), ("dummy-secret", "local-model"))
                with patch.dict(os.environ, {"OPENAI_API_KEY": "env-secret", "MODEL_ASSISTANT_MODEL": "env-model"}):
                    self.assertEqual(credentials("explicit-model"), ("env-secret", "explicit-model"))
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    self.assertEqual(configure(["--check"]), 0)
                self.assertNotIn("dummy-secret", output.getvalue())
                path.chmod(0o644)
                with self.assertRaises(ValueError):
                    load_config()

    def test_online_free_text_request_to_saved_solution_mock(self):
        response = {"status": "completed", "model": "mock-model", "usage": {"input_tokens": 100, "output_tokens": 200},
                    "output": [{"type": "message", "content": [{"type": "output_text", "text": json.dumps(parse_template(TEXT))}]}]}
        with tempfile.TemporaryDirectory() as temp, patch.dict(os.environ, {"OPENAI_API_KEY": "dummy-secret", "MODEL_ASSISTANT_MODEL": "mock-model"}), patch("urllib.request.urlopen") as request, contextlib.redirect_stdout(io.StringIO()):
            request.return_value.__enter__.return_value = io.BytesIO(json.dumps(response).encode("utf-8"))
            self.assertEqual(main(["--backend", "openai", "--text", "这是一个模拟的自由输入问题", "--output", temp]), 0)
            outgoing = request.call_args.args[0]
            self.assertEqual(outgoing.full_url, "https://api.openai.com/v1/responses")
            payload = json.loads(outgoing.data)
            self.assertEqual(payload["text"]["format"]["type"], "json_schema")
            self.assertEqual(payload["input"], "这是一个模拟的自由输入问题")
            record_text = next(Path(temp).glob("*/run.json")).read_text()
            self.assertNotIn("dummy-secret", record_text)
            record = json.loads(record_text)
            self.assertEqual(record["stages"][0]["result"]["objective"], 2200)
            self.assertEqual(record["generation"]["usage"]["input_tokens"], 100)

    def test_interactive_and_empty_input(self):
        with tempfile.TemporaryDirectory() as temp, patch("builtins.input", side_effect=TEXT.splitlines() + [""]), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(["--interactive", "--output", temp]), 0)
        with patch("assistant.cli.generate") as network, contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["--backend", "openai", "--text", " "]), 2)
            network.assert_not_called()


if __name__ == "__main__":
    unittest.main()
