"""
utils.py - File and text utilities for arch-knowledge.

Provides:
- file_hash()            SHA-256 hash of a file
- slugify()              URL/filename-safe slug from a string
- now_iso()              current datetime in ISO-8601
- today_iso()            current date in ISO-8601
- extract_frontmatter()  parse YAML frontmatter from markdown
- extract_knowledge_links() find [[wiki-links]] in text
- read_index()           read wiki/index.md
- append_to_daily()      append a line to a dated daily log file
- append_to_log()        append a line to wiki/log.md
- load_state()           load JSON state file
- save_state()           save JSON state file
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# Hashing
# ---------------------------------------------------------------------------


def file_hash(path: Path) -> str:
    """Return the SHA-256 hex digest of the file at *path*."""
    sha = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            sha.update(chunk)
    return sha.hexdigest()


# ---------------------------------------------------------------------------
# String helpers
# ---------------------------------------------------------------------------


def slugify(text: str) -> str:
    """
    Convert *text* to a URL/filename-safe slug.

    Steps:
    1. Normalise unicode to NFKD, drop non-ASCII characters.
    2. Lower-case.
    3. Replace runs of non-alphanumeric characters with a single hyphen.
    4. Strip leading/trailing hyphens.
    """
    normalised = unicodedata.normalize("NFKD", text)
    ascii_text = normalised.encode("ascii", "ignore").decode("ascii")
    lowered = ascii_text.lower()
    slugged = re.sub(r"[^a-z0-9]+", "-", lowered)
    return slugged.strip("-")


# ---------------------------------------------------------------------------
# Time helpers
# ---------------------------------------------------------------------------


def now_iso() -> str:
    """Return the current UTC datetime as an ISO-8601 string (seconds precision)."""
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def today_iso() -> str:
    """Return today's date as an ISO-8601 string (YYYY-MM-DD)."""
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")


# ---------------------------------------------------------------------------
# Frontmatter
# ---------------------------------------------------------------------------

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def extract_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """
    Parse YAML frontmatter from *text*.

    Returns (frontmatter_dict, body) where body is the text after the closing
    ``---`` delimiter.  If no frontmatter is found, returns ({}, text).
    """
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return {}, text

    raw_yaml = match.group(1)
    data = _parse_frontmatter(raw_yaml)

    body = text[match.end():]
    return (data if isinstance(data, dict) else {}), body


def _parse_frontmatter(raw_yaml: str) -> dict[str, Any]:
    """Parse simple YAML frontmatter with an optional PyYAML dependency."""
    if yaml is not None:
        try:
            data = yaml.safe_load(raw_yaml)
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    result: dict[str, Any] = {}
    current_list_key: str | None = None
    for raw_line in raw_yaml.splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            continue
        stripped = line.strip()
        if stripped.startswith("- ") and current_list_key:
            result.setdefault(current_list_key, []).append(stripped[2:].strip())
            continue
        current_list_key = None
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not value:
            result[key] = []
            current_list_key = key
            continue
        result[key] = value
    return result


# ---------------------------------------------------------------------------
# Wiki-link extraction
# ---------------------------------------------------------------------------

_WIKI_LINK_RE = re.compile(r"\[\[([^\]]+)\]\]")


def extract_knowledge_links(text: str) -> list[str]:
    """
    Return a list of all [[wiki-link]] targets found in *text*.

    Duplicate targets are preserved (caller can deduplicate if needed).
    """
    return _WIKI_LINK_RE.findall(text)


# ---------------------------------------------------------------------------
# Index
# ---------------------------------------------------------------------------


def read_index(wiki_root: Path) -> str:
    """
    Read wiki/index.md relative to *wiki_root*.

    Returns the file contents, or an empty string if the file does not exist.
    """
    index_path = wiki_root / "index.md"
    if not index_path.exists():
        return ""
    return index_path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Log helpers
# ---------------------------------------------------------------------------


def append_to_daily(log_dir: Path, line: str, date: str | None = None) -> Path:
    """
    Append *line* (with a trailing newline) to a dated daily log file.

    The file is named ``<date>.md`` inside *log_dir* (created if needed).
    *date* defaults to today (ISO-8601, UTC).

    Returns the path to the daily log file.
    """
    date = date or today_iso()
    log_dir.mkdir(parents=True, exist_ok=True)
    daily_path = log_dir / f"{date}.md"
    with daily_path.open("a", encoding="utf-8") as fh:
        fh.write(line if line.endswith("\n") else line + "\n")
    return daily_path


def append_to_log(wiki_root: Path, line: str) -> Path:
    """
    Append *line* (with a trailing newline) to wiki/log.md inside *wiki_root*.

    The file is created if it does not exist.  Prepends a timestamp.

    Returns the path to log.md.
    """
    log_path = wiki_root / "log.md"
    wiki_root.mkdir(parents=True, exist_ok=True)
    timestamp = now_iso()
    entry = f"- {timestamp} {line}" if not line.startswith("-") else f"- {timestamp} {line.lstrip('- ')}"
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(entry if entry.endswith("\n") else entry + "\n")
    return log_path


# ---------------------------------------------------------------------------
# State management (JSON)
# ---------------------------------------------------------------------------


def load_state(state_path: Path) -> dict[str, Any]:
    """
    Load a JSON state file.

    Returns an empty dict if the file does not exist or is not valid JSON.
    """
    if not state_path.exists():
        return {}
    try:
        with state_path.open(encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def save_state(state_path: Path, state: dict[str, Any]) -> None:
    """
    Save *state* as pretty-printed JSON to *state_path*.

    Creates parent directories as needed.
    """
    state_path.parent.mkdir(parents=True, exist_ok=True)
    with state_path.open("w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
