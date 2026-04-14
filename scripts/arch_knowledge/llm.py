"""Generic adapter-based LLM invocation for arch-knowledge."""

from __future__ import annotations

import json
import os
import shlex
import subprocess
from typing import Any


class AdapterError(RuntimeError):
    """Raised when the configured LLM adapter fails."""


def call_llm(
    prompt: str,
    *,
    system: str = "",
    config: dict[str, Any] | None = None,
    max_tokens: int = 4096,
) -> str:
    """Backwards-compatible generic wrapper around the adapter contract."""
    return call_llm_task(
        task="generic",
        system=system,
        input_data=prompt,
        config=config,
        options={"max_tokens": max_tokens},
    )


def call_llm_task(
    *,
    task: str,
    system: str,
    input_data: Any,
    config: dict[str, Any] | None = None,
    options: dict[str, Any] | None = None,
) -> str:
    """Call the configured adapter command and return its text content."""
    cfg = config or {}
    adapter_command = os.environ.get("ARCH_LLM_ADAPTER", str(cfg.get("adapter_command", ""))).strip()
    if not adapter_command:
        raise AdapterError(
            "No LLM adapter configured. Set ARCH_LLM_ADAPTER or llm.adapter_command."
        )
    timeout_seconds = int(os.environ.get("ARCH_LLM_TIMEOUT_SECONDS", cfg.get("timeout_seconds", 60)))

    payload = {
        "task": task,
        "system": system,
        "input": input_data,
        "options": options or {},
    }

    try:
        completed = subprocess.run(
            shlex.split(adapter_command),
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
        )
    except OSError as exc:
        raise AdapterError(f"Failed to start adapter command: {exc}") from exc
    except subprocess.TimeoutExpired as exc:
        raise AdapterError(f"Adapter command timed out after {exc.timeout} seconds") from exc

    if completed.returncode != 0:
        stderr = completed.stderr.strip()
        raise AdapterError(
            f"Adapter command failed with exit code {completed.returncode}: {stderr or 'no stderr'}"
        )

    try:
        response = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise AdapterError("Adapter command did not return valid JSON") from exc

    if not isinstance(response, dict):
        raise AdapterError("Adapter response must be a JSON object")
    if not response.get("ok"):
        raise AdapterError(str(response.get("error", "adapter returned ok=false")))

    content = response.get("content", "")
    if not isinstance(content, str):
        raise AdapterError("Adapter response field 'content' must be a string")
    return content
