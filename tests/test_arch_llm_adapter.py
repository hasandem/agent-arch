"""Tests for the generic arch-llm-adapter helper."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


def _run_adapter(adapter_path: Path, payload: dict, env: dict[str, str]) -> dict:
    completed = subprocess.run(
        ["python3", str(adapter_path)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )
    assert completed.returncode == 0
    return json.loads(completed.stdout)


def test_arch_llm_adapter_reports_missing_tool_command():
    """The adapter should fail clearly when no tool command is configured."""
    repo_root = Path(__file__).resolve().parents[1]
    adapter_path = repo_root / "scripts" / "arch-llm-adapter.py"
    env = dict(os.environ)
    env.pop("ARCH_LLM_TOOL_CMD", None)

    result = _run_adapter(adapter_path, {"task": "flush", "system": "", "input": "x"}, env)

    assert result["ok"] is False
    assert "ARCH_LLM_TOOL_CMD" in result["error"]


def test_arch_llm_adapter_wraps_plain_stdin_stdout_command():
    """The adapter should wrap any prompt-on-stdin tool command."""
    repo_root = Path(__file__).resolve().parents[1]
    adapter_path = repo_root / "scripts" / "arch-llm-adapter.py"
    env = dict(os.environ)
    env["ARCH_LLM_TOOL_CMD"] = (
        "python3 -c \"import sys; data=sys.stdin.read(); print(data.upper())\""
    )

    result = _run_adapter(
        adapter_path,
        {"task": "flush", "system": "system", "input": "hello world", "options": {}},
        env,
    )

    assert result["ok"] is True
    assert "HELLO WORLD" in result["content"]
