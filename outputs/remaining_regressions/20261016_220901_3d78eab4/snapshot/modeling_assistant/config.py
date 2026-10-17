"""Local credentials outside the project; never include secrets in diagnostics."""

import json
import os
import tempfile
from pathlib import Path


PROVIDERS = {
    "openai": {"key_env": "OPENAI_API_KEY", "model_env": "MODEL_ASSISTANT_MODEL",
               "default_model": "gpt-4.1-mini", "endpoint": "https://api.openai.com/v1/responses"},
    "deepseek": {"key_env": "DEEPSEEK_API_KEY", "model_env": "DEEPSEEK_MODEL",
                 "default_model": "deepseek-flash", "endpoint": "https://api.deepseek.com/chat/completions"},
}


def config_path(backend="openai"):
    if backend not in PROVIDERS:
        raise ValueError("不支持的服务商")
    return Path.home() / ".config" / "aiforresearch" / (backend + ".json")


def load_config(backend="openai"):
    path = config_path(backend)
    if not path.exists():
        return {}
    if path.stat().st_mode & 0o077:
        raise ValueError(f"配置文件权限过宽，请执行 chmod 600 '{path}'")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ValueError("本地 API 配置无法读取；请重新运行配置向导") from exc
    if not isinstance(data, dict) or any(not isinstance(data.get(k), str) for k in ("api_key", "model")):
        raise ValueError("本地 API 配置格式错误；请重新运行配置向导")
    return data


def credentials(model_name=None, backend="openai"):
    if backend not in PROVIDERS:
        raise ValueError("不支持的服务商")
    provider = PROVIDERS[backend]
    key = os.environ.get(provider["key_env"], "").strip()
    model = (model_name or os.environ.get(provider["model_env"], "")).strip()
    local = load_config(backend) if not key or not model else {}
    return key or local.get("api_key", ""), model or local.get("model", "")


def save_config(key, model, backend="openai"):
    key, model = key.strip(), model.strip()
    if not key or not model or any(c.isspace() for c in key + model):
        raise ValueError("密钥和模型 ID 不能为空或包含空白字符")
    path = config_path(backend)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix="." + backend + "-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump({"api_key": key, "model": model}, stream)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return path
