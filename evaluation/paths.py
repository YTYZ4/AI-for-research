"""Resolve pre-cleanup paths when reviewing a frozen historical batch."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def current_path(path):
    mapping = json.loads((ROOT / 'docs/paths.json').read_text())
    return mapping.get(str(path), str(path))
