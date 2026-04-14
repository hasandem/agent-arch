#!/usr/bin/env python3
"""Generic adapter for arch-knowledge using any prompt-on-stdin CLI."""

from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys


def build_prompt(payload: dict) -> str:
    task = payload.get("task", "unknown")
    system = payload.get("system", "").strip()
    input_data = payload.get("input", "")
    options = payload.get("options", {})
    parts = [
        f"Task: {task}",
        "",
        "System instructions:",
        system or "(none)",
        "",
        "Input:",
        json.dumps(input_data, ensure_ascii=False, indent=2)
        if not isinstance(input_data, str)
        else input_data,
    ]
    if options:
        parts.extend(["", "Options:", json.dumps(options, ensure_ascii=False, indent=2)])
    return "\n".join(parts).strip() + "\n"


def main() -> int:
    tool_cmd = os.environ.get("ARCH_LLM_TOOL_CMD", "").strip()
    if not tool_cmd:
        json.dump(
            {
                "ok": False,
                "error": (
                    "ARCH_LLM_TOOL_CMD is not set. Point it at a command that reads "
                    "prompt text on stdin and returns plain text on stdout."
                ),
            },
            sys.stdout,
        )
        sys.stdout.write("\n")
        return 0

    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        json.dump({"ok": False, "error": "Invalid JSON request"}, sys.stdout)
        sys.stdout.write("\n")
        return 0

    prompt = build_prompt(payload)
    try:
        completed = subprocess.run(
            shlex.split(tool_cmd),
            input=prompt,
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError as exc:
        json.dump({"ok": False, "error": f"Failed to run ARCH_LLM_TOOL_CMD: {exc}"}, sys.stdout)
        sys.stdout.write("\n")
        return 0

    if completed.returncode != 0:
        json.dump(
            {
                "ok": False,
                "error": completed.stderr.strip()
                or f"LLM command failed with exit code {completed.returncode}",
            },
            sys.stdout,
        )
        sys.stdout.write("\n")
        return 0

    json.dump({"ok": True, "content": completed.stdout.strip()}, sys.stdout)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
