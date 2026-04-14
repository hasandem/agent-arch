"""Tests for the generic LLM adapter command contract."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from arch_knowledge.llm import AdapterError, call_llm_task


def _write_adapter(path: Path, body: str) -> None:
    path.write_text(body, encoding="utf-8")
    path.chmod(0o755)


def test_call_llm_task_uses_adapter_command(tmp_path):
    """LLM calls should flow through the configured adapter command."""
    adapter = tmp_path / "adapter.py"
    _write_adapter(
        adapter,
        """#!/usr/bin/env python3
import json, sys
request = json.load(sys.stdin)
json.dump({"ok": True, "content": f"{request['task']}::{request['input']}"}, sys.stdout)
""",
    )

    result = call_llm_task(
        task="flush",
        system="system prompt",
        input_data="hello world",
        config={"adapter_command": f"python3 {adapter}", "timeout_seconds": 5},
    )

    assert result == "flush::hello world"


def test_call_llm_task_rejects_invalid_adapter_json(tmp_path):
    """Invalid adapter JSON should raise a clear adapter error."""
    adapter = tmp_path / "adapter.py"
    _write_adapter(
        adapter,
        """#!/usr/bin/env python3
print("not-json")
""",
    )

    with pytest.raises(AdapterError):
        call_llm_task(
            task="flush",
            system="system prompt",
            input_data="hello world",
            config={"adapter_command": f"python3 {adapter}", "timeout_seconds": 5},
        )


def test_call_llm_task_prefers_env_var(tmp_path, monkeypatch):
    """Environment config should override profile config."""
    adapter = tmp_path / "adapter.py"
    _write_adapter(
        adapter,
        """#!/usr/bin/env python3
import json, sys
request = json.load(sys.stdin)
json.dump({"ok": True, "content": request["options"]["marker"]}, sys.stdout)
""",
    )
    monkeypatch.setenv("ARCH_LLM_ADAPTER", f"python3 {adapter}")

    result = call_llm_task(
        task="flush",
        system="system prompt",
        input_data="hello world",
        config={"adapter_command": "false"},
        options={"marker": "from-env"},
    )

    assert result == "from-env"
