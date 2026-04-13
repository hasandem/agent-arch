"""
config.py - Configuration loading for arch-knowledge.

Reads arch-statement.md and compliance-profile.yaml from the knowledge root.
"""

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

    with profile_path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)

    return data if isinstance(data, dict) else {}


# ---------------------------------------------------------------------------
# LLM config
# ---------------------------------------------------------------------------


def get_llm_config(knowledge_root: Path | None = None) -> dict[str, Any]:
    """
    Return LLM configuration, merging sources in priority order:

    1. Environment variables (ARCH_LLM_PROVIDER, ARCH_LLM_MODEL, ARCH_LLM_BASE_URL, ARCH_LLM_API_KEY)
    2. compliance-profile.yaml [llm] section
    3. arch-statement.md llm-* keys
    4. Built-in defaults (provider=anthropic, model=claude-3-5-haiku-20241022)

    The returned dict has keys: provider, model, base_url (optional), api_key (optional).
    """
    defaults: dict[str, Any] = {
        "provider": "anthropic",
        "model": "claude-3-5-haiku-20241022",
    }

    # Layer 3: arch-statement.md
    if knowledge_root is not None:
        statement = parse_arch_statement(knowledge_root)
        if "llm-provider" in statement:
            defaults["provider"] = statement["llm-provider"]
        if "llm-model" in statement:
            defaults["model"] = statement["llm-model"]
        if "llm-base-url" in statement:
            defaults["base_url"] = statement["llm-base-url"]
        if "llm-api-key" in statement:
            defaults["api_key"] = statement["llm-api-key"]

    # Layer 2: compliance-profile.yaml [llm] section
    if knowledge_root is not None:
        profile = load_compliance_profile(knowledge_root)
        llm_section = profile.get("llm", {})
        if isinstance(llm_section, dict):
            for key in ("provider", "model", "base_url", "api_key"):
                if key in llm_section:
                    defaults[key] = llm_section[key]

    # Layer 1: environment variables (highest priority)
    env_map = {
        "ARCH_LLM_PROVIDER": "provider",
        "ARCH_LLM_MODEL": "model",
        "ARCH_LLM_BASE_URL": "base_url",
        "ARCH_LLM_API_KEY": "api_key",
    }
    for env_var, cfg_key in env_map.items():
        value = os.environ.get(env_var)
        if value:
            defaults[cfg_key] = value

    return defaults
