"""Configuration loading for arch-knowledge."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# Root discovery
# ---------------------------------------------------------------------------


def find_knowledge_root(start: Path | None = None) -> Path | None:
    """Walk up from start (default: cwd) looking for docs/arch-knowledge/."""
    current = (start or Path.cwd()).resolve()
    for directory in [current, *current.parents]:
        candidate = directory / "docs" / "arch-knowledge"
        if candidate.is_dir():
            return candidate
    return None


def find_repo_root(start: Path | None = None) -> Path | None:
    """Walk up from start (default: cwd) looking for a .git directory."""
    current = (start or Path.cwd()).resolve()
    for directory in [current, *current.parents]:
        if (directory / ".git").exists():
            return directory
    return None


# ---------------------------------------------------------------------------
# arch-statement.md
# ---------------------------------------------------------------------------


def parse_arch_statement(knowledge_root: Path) -> dict[str, str]:
    """
    Parse docs/arch-knowledge/arch-statement.md.

    Expects simple key: value lines in the markdown, e.g.:

        mode: standalone
        central-wiki: https://github.com/org/arch-repo
        sync-branch: main

    Returns a dict of all key/value pairs found.
    """
    statement_path = knowledge_root / "arch-statement.md"
    if not statement_path.exists():
        return {}

    result: dict[str, str] = {}
    kv_pattern = re.compile(r"^(\w[\w-]*):\s*(.+)$")

    for line in statement_path.read_text(encoding="utf-8").splitlines():
        m = kv_pattern.match(line.strip())
        if m:
            result[m.group(1)] = m.group(2).strip()

    return result


# ---------------------------------------------------------------------------
# compliance-profile.yaml
# ---------------------------------------------------------------------------


def load_compliance_profile(knowledge_root: Path) -> dict[str, Any]:
    """
    Load docs/arch-knowledge/compliance-profile.yaml.

    Returns the parsed YAML as a dict, or an empty dict if the file does not exist.
    """
    profile_path = knowledge_root / "compliance-profile.yaml"
    if not profile_path.exists():
        return {}

    if yaml is None:
        return {}

    with profile_path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)

    return data if isinstance(data, dict) else {}


# ---------------------------------------------------------------------------
# LLM config
# ---------------------------------------------------------------------------


def get_llm_config(knowledge_root: Path | None = None) -> dict[str, Any]:
    """
    Return LLM configuration, merging sources in priority order:

    1. Environment variables (ARCH_LLM_ADAPTER, ARCH_LLM_TIMEOUT_SECONDS)
    2. compliance-profile.yaml [llm] section
    3. arch-statement.md llm-* keys
    4. Built-in defaults

    The returned dict has keys: adapter_command and timeout_seconds.
    """
    defaults: dict[str, Any] = {
        "adapter_command": "",
        "timeout_seconds": 60,
    }

    # Layer 3: arch-statement.md
    if knowledge_root is not None:
        statement = parse_arch_statement(knowledge_root)
        if "llm-adapter-command" in statement:
            defaults["adapter_command"] = statement["llm-adapter-command"]
        if "llm-timeout-seconds" in statement:
            try:
                defaults["timeout_seconds"] = int(statement["llm-timeout-seconds"])
            except ValueError:
                pass

    # Layer 2: compliance-profile.yaml [llm] section
    if knowledge_root is not None:
        profile = load_compliance_profile(knowledge_root)
        llm_section = profile.get("llm", {})
        if isinstance(llm_section, dict):
            if "adapter_command" in llm_section:
                defaults["adapter_command"] = llm_section["adapter_command"]
            if "timeout_seconds" in llm_section:
                try:
                    defaults["timeout_seconds"] = int(llm_section["timeout_seconds"])
                except (TypeError, ValueError):
                    pass

    # Layer 1: environment variables (highest priority)
    adapter_command = os.environ.get("ARCH_LLM_ADAPTER")
    if adapter_command:
        defaults["adapter_command"] = adapter_command

    timeout_value = os.environ.get("ARCH_LLM_TIMEOUT_SECONDS")
    if timeout_value:
        try:
            defaults["timeout_seconds"] = int(timeout_value)
        except ValueError:
            pass

    return defaults
