# Creativity-First Architecture Governance — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace sequential gating architecture governance with a creativity-first model: knowledge context in, compliance out, using an agent-universal CLI and automatic knowledge capture pipeline.

**Architecture:** A Python-based CLI (`arch-knowledge`) with subcommands (context, flush, compile, lint, compliance, propose, bootstrap) backed by a three-layer knowledge structure (raw/daily/knowledge). Agent-specific adapters (Claude Code hooks, .cursorrules, AGENTS.md) wrap the CLI. Skills are thin SKILL.md wrappers that instruct agents to use the CLI.

**Tech Stack:** Python 3.12+, shell scripts, markdown, YAML, git hooks. LLM calls via configurable provider (anthropic SDK default, openai compatible).

**Spec:** `docs/superpowers/specs/2026-04-12-creativity-first-architecture-governance-design.md`

---

## Task 1: Python project setup and core configuration

**Files:**
- Create: `scripts/arch_knowledge/__init__.py`
- Create: `scripts/arch_knowledge/config.py`
- Create: `scripts/arch_knowledge/utils.py`
- Create: `scripts/arch_knowledge/llm.py`
- Create: `pyproject.toml`
- Create: `scripts/arch-knowledge` (CLI entrypoint, shell wrapper)

This is the foundation. Config reads `arch-statement.md` and `compliance-profile.yaml`. Utils handles file hashing, slug generation, frontmatter parsing, knowledge-link extraction. LLM abstraction allows switching providers.

- [ ] **Step 1: Create pyproject.toml**

```toml
[project]
name = "arch-knowledge"
version = "0.1.0"
description = "Creativity-first architecture governance CLI"
requires-python = ">=3.12"
dependencies = [
    "anthropic>=0.42.0",
    "openai>=1.50.0",
    "python-dotenv>=1.0.0",
    "pyyaml>=6.0",
]

[project.optional-dependencies]
dev = ["pytest>=8.0", "pytest-cov"]

[project.scripts]
arch-knowledge = "arch_knowledge.cli:main"
```

- [ ] **Step 2: Create config.py — reads arch-statement.md and compliance-profile.yaml**

```python
# scripts/arch_knowledge/config.py
"""Configuration management for arch-knowledge.

Reads arch-statement.md (mode, central repo) and compliance-profile.yaml
(rules, scope, LLM settings). All paths are relative to the knowledge root.
"""
import os
import re
import yaml
from pathlib import Path


def find_knowledge_root(start: Path | None = None) -> Path | None:
    """Walk up from start (default cwd) looking for docs/arch-knowledge/."""
    current = start or Path.cwd()
    for parent in [current, *current.parents]:
        candidate = parent / "docs" / "arch-knowledge"
        if candidate.is_dir():
            return candidate
    return None


def find_repo_root(start: Path | None = None) -> Path:
    """Walk up from start (default cwd) looking for .git."""
    current = start or Path.cwd()
    for parent in [current, *current.parents]:
        if (parent / ".git").exists():
            return parent
    return current


def parse_arch_statement(knowledge_root: Path) -> dict:
    """Parse arch-statement.md for mode and central-repo settings.

    Returns dict with keys: mode ('standalone'|'connected'),
    central_repo (str|None), central_repo_url (str|None),
    description (str).
    """
    statement_path = knowledge_root / "arch-statement.md"
    result = {
        "mode": "standalone",
        "central_repo": None,
        "central_repo_url": None,
        "description": "",
    }
    if not statement_path.exists():
        return result

    text = statement_path.read_text(encoding="utf-8")
    mode_match = re.search(r"^mode:\s*(\S+)", text, re.MULTILINE)
    if mode_match:
        result["mode"] = mode_match.group(1)
    repo_match = re.search(r"^central-repo:\s*(\S+)", text, re.MULTILINE)
    if repo_match:
        result["central_repo"] = repo_match.group(1)
    url_match = re.search(r"^central-repo-url:\s*(\S+)", text, re.MULTILINE)
    if url_match:
        result["central_repo_url"] = url_match.group(1)
    return result


def load_compliance_profile(knowledge_root: Path) -> dict:
    """Load compliance-profile.yaml. Returns empty dict if not found."""
    profile_path = knowledge_root / "compliance-profile.yaml"
    if not profile_path.exists():
        return {}
    return yaml.safe_load(profile_path.read_text(encoding="utf-8")) or {}


def get_llm_config(profile: dict) -> dict:
    """Extract LLM configuration from compliance profile."""
    llm = profile.get("llm", {})
    return {
        "provider": llm.get("provider", "anthropic"),
        "model": llm.get("model", "claude-sonnet-4-20250514"),
        "endpoint": llm.get("endpoint"),
    }
```

- [ ] **Step 3: Create utils.py — file hashing, frontmatter, knowledge-links**

```python
# scripts/arch_knowledge/utils.py
"""Shared utilities for arch-knowledge.

File hashing, frontmatter parsing, knowledge-link extraction,
slug generation, and daily log management.
"""
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

KNOWLEDGE_LINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def file_hash(path: Path) -> str:
    """SHA-256 hash of file contents, truncated to 16 chars."""
    content = path.read_bytes()
    return hashlib.sha256(content).hexdigest()[:16]


def slugify(text: str) -> str:
    """Convert text to lowercase hyphenated slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return re.sub(r"-+", "-", text).strip("-")


def now_iso() -> str:
    """Current UTC datetime in ISO format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def today_iso() -> str:
    """Current UTC date in ISO format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def extract_frontmatter(text: str) -> dict:
    """Extract YAML frontmatter from markdown text. Returns empty dict if none."""
    import yaml
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}
    return yaml.safe_load(match.group(1)) or {}


def extract_knowledge_links(text: str) -> list[str]:
    """Extract all [[knowledge-links]] from text."""
    return KNOWLEDGE_LINK_RE.findall(text)


def read_index(knowledge_dir: Path) -> list[dict]:
    """Read knowledge/index.md and parse article entries.

    Expected format: | slug | title | type | status | summary |
    Returns list of dicts with those keys.
    """
    index_path = knowledge_dir / "index.md"
    if not index_path.exists():
        return []

    entries = []
    text = index_path.read_text(encoding="utf-8")
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("|") and not line.startswith("| slug") and "---" not in line:
            parts = [p.strip() for p in line.split("|")[1:-1]]
            if len(parts) >= 5:
                entries.append({
                    "slug": parts[0],
                    "title": parts[1],
                    "type": parts[2],
                    "status": parts[3],
                    "summary": parts[4],
                })
    return entries


def append_to_daily(knowledge_root: Path, content: str) -> Path:
    """Append timestamped entry to today's daily log."""
    daily_dir = knowledge_root / "daily"
    daily_dir.mkdir(parents=True, exist_ok=True)
    daily_path = daily_dir / f"{today_iso()}.md"

    timestamp = now_iso()
    entry = f"\n## {timestamp}\n\n{content}\n"

    if not daily_path.exists():
        daily_path.write_text(f"# Daily Log — {today_iso()}\n{entry}", encoding="utf-8")
    else:
        with open(daily_path, "a", encoding="utf-8") as f:
            f.write(entry)
    return daily_path


def append_to_log(knowledge_dir: Path, message: str) -> None:
    """Append timestamped entry to knowledge/log.md."""
    log_path = knowledge_dir / "log.md"
    timestamp = now_iso()
    entry = f"- {timestamp} — {message}\n"

    if not log_path.exists():
        log_path.write_text(f"# Knowledge Log\n\n{entry}", encoding="utf-8")
    else:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(entry)


def load_state(knowledge_root: Path) -> dict:
    """Load persistent state from .state.json."""
    state_path = knowledge_root / ".state.json"
    if not state_path.exists():
        return {}
    return json.loads(state_path.read_text(encoding="utf-8"))


def save_state(knowledge_root: Path, state: dict) -> None:
    """Save persistent state to .state.json."""
    state_path = knowledge_root / ".state.json"
    state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
```

- [ ] **Step 4: Create llm.py — provider-agnostic LLM abstraction**

```python
# scripts/arch_knowledge/llm.py
"""LLM abstraction layer for arch-knowledge.

Supports anthropic, openai, and ollama providers.
Configured via compliance-profile.yaml llm section.
"""
import os


def call_llm(prompt: str, system: str = "", config: dict | None = None) -> str:
    """Send prompt to configured LLM provider and return response text.

    Args:
        prompt: The user prompt
        system: Optional system prompt
        config: LLM config dict with provider, model, endpoint keys.
                Defaults to anthropic/claude-sonnet if not provided.

    Returns:
        Response text from the LLM.
    """
    config = config or {}
    provider = config.get("provider", "anthropic")
    model = config.get("model", "claude-sonnet-4-20250514")
    endpoint = config.get("endpoint")

    if provider == "anthropic":
        return _call_anthropic(prompt, system, model)
    elif provider in ("openai", "custom"):
        return _call_openai_compatible(prompt, system, model, endpoint)
    elif provider == "ollama":
        return _call_openai_compatible(
            prompt, system, model,
            endpoint or "http://localhost:11434/v1"
        )
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")


def _call_anthropic(prompt: str, system: str, model: str) -> str:
    """Call Anthropic API."""
    from anthropic import Anthropic

    client = Anthropic()  # Uses ANTHROPIC_API_KEY env var
    messages = [{"role": "user", "content": prompt}]
    response = client.messages.create(
        model=model,
        max_tokens=4096,
        system=system or "You are a helpful architecture knowledge assistant.",
        messages=messages,
    )
    return response.content[0].text


def _call_openai_compatible(
    prompt: str, system: str, model: str, endpoint: str | None
) -> str:
    """Call OpenAI-compatible API (OpenAI, Ollama, custom)."""
    from openai import OpenAI

    kwargs = {}
    if endpoint:
        kwargs["base_url"] = endpoint
    client = OpenAI(**kwargs)  # Uses OPENAI_API_KEY env var

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=model,
        max_tokens=4096,
        messages=messages,
    )
    return response.choices[0].message.content
```

- [ ] **Step 5: Create `__init__.py`**

```python
# scripts/arch_knowledge/__init__.py
"""arch-knowledge: Creativity-first architecture governance CLI."""
```

- [ ] **Step 6: Create CLI shell wrapper**

```bash
#!/usr/bin/env bash
# scripts/arch-knowledge
# Universal CLI entrypoint for arch-knowledge.
# Works with any agent — Claude Code, Cursor, Copilot, Codex, etc.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Recursion guard
if [ "${ARCH_KNOWLEDGE_INVOKED_BY:-}" = "hook" ]; then
    exit 0
fi

# Try uv first, fall back to python
if command -v uv &>/dev/null; then
    exec uv run python -m arch_knowledge.cli "$@"
elif command -v python3 &>/dev/null; then
    PYTHONPATH="$SCRIPT_DIR:${PYTHONPATH:-}" exec python3 -m arch_knowledge.cli "$@"
else
    echo "Error: Python 3.12+ required. Install via https://python.org" >&2
    exit 1
fi
```

- [ ] **Step 7: Run basic import test**

Run: `cd /path/to/repo && python3 -c "from arch_knowledge import config, utils, llm; print('OK')"`
Expected: `OK`

- [ ] **Step 8: Commit**

```bash
git add pyproject.toml scripts/arch_knowledge/ scripts/arch-knowledge
git commit -m "feat: add core Python infrastructure for arch-knowledge CLI

Config reads arch-statement.md and compliance-profile.yaml.
Utils handles hashing, frontmatter, knowledge-links, daily logs.
LLM abstraction supports anthropic, openai, and ollama providers."
```

---

## Task 2: Flush pipeline — filter architecture-relevant knowledge

**Files:**
- Create: `scripts/arch_knowledge/flush.py`

Flush takes raw input (conversation excerpt, commit diff, or arbitrary text), asks an LLM to filter for architecture-relevant content, and appends to today's daily log. Returns quickly — designed to be called from hooks.

- [ ] **Step 1: Create flush.py**

```python
# scripts/arch_knowledge/flush.py
"""Flush pipeline: filter and store architecture-relevant knowledge.

Takes raw input (conversation, diff, or text), asks LLM to identify
architecture-relevant content, and appends to the daily log.

Inspired by Cole Medin's claude-memory-compiler flush.py.
"""
import os
import time
from pathlib import Path

from .config import find_knowledge_root, load_compliance_profile, get_llm_config
from .llm import call_llm
from .utils import append_to_daily, load_state, save_state, now_iso

FLUSH_SYSTEM_PROMPT = """\
You are an architecture knowledge filter. Given a conversation excerpt or 
code diff, extract ONLY architecture-relevant information.

Categorize findings into:
- **Decisions**: Design choices, technology selections, trade-offs made
- **Patterns**: Recurring solutions, best practices discovered
- **Concepts**: Domain understanding, key abstractions learned
- **Lessons**: What worked, what didn't, surprises encountered

Rules:
- Skip routine tool calls, file reads, trivial edits
- Skip pure implementation details with no architectural significance
- Keep it concise — bullet points, not paragraphs
- If nothing architecture-relevant was found, respond with exactly: FLUSH_OK

Format your response as markdown with the category headers above."""

FLUSH_DEDUP_WINDOW_SECONDS = 60


def flush(input_text: str, session_id: str = "") -> str:
    """Filter input for architecture-relevant content and store in daily log.

    Args:
        input_text: Raw text to filter (conversation, diff, etc.)
        session_id: Optional session ID for deduplication.

    Returns:
        "FLUSH_OK" if nothing relevant, or the filtered content.
    """
    knowledge_root = find_knowledge_root()
    if not knowledge_root:
        return "ERROR: No docs/arch-knowledge/ found. Run arch-knowledge bootstrap first."

    # Deduplication: skip if same session flushed recently
    if session_id:
        state = load_state(knowledge_root)
        last_flush = state.get("last_flush", {})
        last_time = last_flush.get(session_id, 0)
        if time.time() - last_time < FLUSH_DEDUP_WINDOW_SECONDS:
            return "FLUSH_OK"

    # Ask LLM to filter
    profile = load_compliance_profile(knowledge_root)
    llm_config = get_llm_config(profile)

    # Truncate input to avoid token waste
    max_chars = 15000
    if len(input_text) > max_chars:
        input_text = input_text[:max_chars] + "\n\n[... truncated ...]"

    result = call_llm(
        prompt=f"Filter the following for architecture-relevant content:\n\n{input_text}",
        system=FLUSH_SYSTEM_PROMPT,
        config=llm_config,
    )

    if result.strip() == "FLUSH_OK":
        return "FLUSH_OK"

    # Append to daily log
    append_to_daily(knowledge_root, result)

    # Update dedup state
    if session_id:
        state = load_state(knowledge_root)
        state.setdefault("last_flush", {})[session_id] = time.time()
        save_state(knowledge_root, state)

    return result


def flush_from_file(filepath: str, session_id: str = "") -> str:
    """Convenience: read a file and flush its contents."""
    text = Path(filepath).read_text(encoding="utf-8")
    return flush(text, session_id)
```

- [ ] **Step 2: Write test for flush**

```python
# tests/test_flush.py
"""Tests for flush pipeline."""
from pathlib import Path
from unittest.mock import patch

from arch_knowledge.flush import flush


def test_flush_ok_when_nothing_relevant(tmp_path):
    """Flush returns FLUSH_OK when LLM finds nothing relevant."""
    # Set up knowledge root
    knowledge_root = tmp_path / "docs" / "arch-knowledge"
    knowledge_root.mkdir(parents=True)

    with patch("arch_knowledge.flush.find_knowledge_root", return_value=knowledge_root), \
         patch("arch_knowledge.flush.call_llm", return_value="FLUSH_OK"):
        result = flush("just some routine file reading")
        assert result == "FLUSH_OK"


def test_flush_appends_to_daily_when_relevant(tmp_path):
    """Flush appends filtered content to daily log."""
    knowledge_root = tmp_path / "docs" / "arch-knowledge"
    knowledge_root.mkdir(parents=True)
    daily_dir = knowledge_root / "daily"

    with patch("arch_knowledge.flush.find_knowledge_root", return_value=knowledge_root), \
         patch("arch_knowledge.flush.call_llm", return_value="## Decisions\n- Chose event sourcing"):
        result = flush("We decided to use event sourcing for audit trail")
        assert "Decisions" in result
        assert daily_dir.exists()
        daily_files = list(daily_dir.glob("*.md"))
        assert len(daily_files) == 1
        content = daily_files[0].read_text()
        assert "event sourcing" in content


def test_flush_deduplicates_by_session(tmp_path):
    """Flush skips if same session flushed within dedup window."""
    knowledge_root = tmp_path / "docs" / "arch-knowledge"
    knowledge_root.mkdir(parents=True)

    with patch("arch_knowledge.flush.find_knowledge_root", return_value=knowledge_root), \
         patch("arch_knowledge.flush.call_llm", return_value="## Decisions\n- Something"):
        # First flush should work
        result1 = flush("some input", session_id="session-1")
        assert result1 != "FLUSH_OK"

        # Second flush with same session should be deduped
        result2 = flush("some input", session_id="session-1")
        assert result2 == "FLUSH_OK"
```

- [ ] **Step 3: Run tests**

Run: `cd /path/to/repo && python3 -m pytest tests/test_flush.py -v`
Expected: 3 tests PASS

- [ ] **Step 4: Commit**

```bash
git add scripts/arch_knowledge/flush.py tests/test_flush.py
git commit -m "feat: add flush pipeline for architecture knowledge filtering

Filters raw input via LLM, appends to daily log.
Includes deduplication by session ID and input truncation."
```

---

## Task 3: Compile pipeline — synthesize daily logs into knowledge articles

**Files:**
- Create: `scripts/arch_knowledge/compile.py`

Compile reads daily logs and existing knowledge articles, asks an LLM to synthesize new/updated articles, and writes them with proper frontmatter and knowledge-links.

- [ ] **Step 1: Create compile.py**

```python
# scripts/arch_knowledge/compile.py
"""Compile pipeline: synthesize daily logs into knowledge articles.

Reads daily/ logs and existing knowledge/ articles, asks LLM to create
or update structured articles with typed frontmatter and knowledge-links.

Inspired by Cole Medin's claude-memory-compiler compile.py.
"""
from pathlib import Path

from .config import find_knowledge_root, load_compliance_profile, get_llm_config
from .llm import call_llm
from .utils import (
    file_hash, slugify, read_index, append_to_log,
    load_state, save_state, today_iso, now_iso,
)

COMPILE_SYSTEM_PROMPT = """\
You are an architecture knowledge compiler. Given daily logs and existing 
knowledge articles, synthesize the information into structured articles.

Each article MUST follow this exact format:

```
---
type: concept | decision | contract | pattern | review
status: draft | active | superseded | deprecated
date: {date}
sources:
  - daily/YYYY-MM-DD.md
---

# Article Title

**Sammendrag**: One to two sentences describing this article.

---

Main content with clear headings and short paragraphs.
Link to related concepts using [[article-slug]] throughout.
Cite sources: (kilde: daily/2026-04-12.md)

## Relaterte artikler

- [[related-slug-1]]
- [[related-slug-2]]
```

For type: decision, also include Changelog section:

```
## Changelog

| Dato | Endring | Begrunnelse |
|---|---|---|
| YYYY-MM-DD | Opprettet | Initial reason |
```

Rules:
- Each article must link to at least 2 other articles via [[slug]]
- Use lowercase hyphenated slugs for article filenames
- Merge information about the same concept into one article (don't duplicate)
- If updating an existing article, preserve its changelog and add a new entry
- Respond with each article separated by ===ARTICLE_BREAK===
- Start each article with the filename: FILENAME: slug-name.md"""


def compile_knowledge(all_mode: bool = False, specific_file: str | None = None) -> list[str]:
    """Compile daily logs into knowledge articles.

    Args:
        all_mode: If True, recompile all logs regardless of hash.
        specific_file: If set, compile only this daily log file.

    Returns:
        List of created/updated article paths.
    """
    knowledge_root = find_knowledge_root()
    if not knowledge_root:
        return ["ERROR: No docs/arch-knowledge/ found."]

    knowledge_dir = knowledge_root / "knowledge"
    knowledge_dir.mkdir(parents=True, exist_ok=True)
    daily_dir = knowledge_root / "daily"

    if not daily_dir.exists():
        return ["No daily logs found."]

    # Determine which logs to process
    state = load_state(knowledge_root)
    compiled_hashes = state.get("compiled_hashes", {})

    if specific_file:
        logs_to_process = [daily_dir / specific_file]
    else:
        logs_to_process = sorted(daily_dir.glob("*.md"))

    if not all_mode:
        logs_to_process = [
            log for log in logs_to_process
            if log.exists() and file_hash(log) != compiled_hashes.get(log.name)
        ]

    if not logs_to_process:
        return ["No new or changed daily logs to compile."]

    # Read all daily logs to compile
    daily_content = ""
    for log_path in logs_to_process:
        daily_content += f"\n\n### Source: {log_path.name}\n\n"
        daily_content += log_path.read_text(encoding="utf-8")

    # Read existing articles for context
    existing_articles = ""
    for article_path in sorted(knowledge_dir.glob("*.md")):
        if article_path.name in ("index.md", "log.md"):
            continue
        existing_articles += f"\n\n### Existing: {article_path.name}\n\n"
        existing_articles += article_path.read_text(encoding="utf-8")

    # Ask LLM to compile
    profile = load_compliance_profile(knowledge_root)
    llm_config = get_llm_config(profile)

    prompt = f"""Compile the following daily logs into knowledge articles.

## Existing articles (for context and merging):
{existing_articles or "(none yet)"}

## Daily logs to compile:
{daily_content}

Create new articles or update existing ones as appropriate."""

    result = call_llm(
        prompt=prompt,
        system=COMPILE_SYSTEM_PROMPT.format(date=today_iso()),
        config=llm_config,
    )

    # Parse and write articles
    created_paths = []
    articles = result.split("===ARTICLE_BREAK===")

    for article_text in articles:
        article_text = article_text.strip()
        if not article_text:
            continue

        # Extract filename
        lines = article_text.split("\n")
        filename = None
        content_start = 0
        for i, line in enumerate(lines):
            if line.startswith("FILENAME:"):
                filename = line.replace("FILENAME:", "").strip()
                content_start = i + 1
                break

        if not filename:
            filename = slugify(lines[0][:60]) + ".md"

        if not filename.endswith(".md"):
            filename += ".md"

        article_content = "\n".join(lines[content_start:]).strip()
        article_path = knowledge_dir / filename
        article_path.write_text(article_content + "\n", encoding="utf-8")
        created_paths.append(str(article_path))
        append_to_log(knowledge_dir, f"Compiled: {filename}")

    # Update compiled hashes
    for log_path in logs_to_process:
        if log_path.exists():
            compiled_hashes[log_path.name] = file_hash(log_path)
    state["compiled_hashes"] = compiled_hashes
    save_state(knowledge_root, state)

    # Rebuild index
    _rebuild_index(knowledge_dir)

    return created_paths


def _rebuild_index(knowledge_dir: Path) -> None:
    """Rebuild knowledge/index.md from all articles."""
    from .utils import extract_frontmatter

    entries = []
    for article_path in sorted(knowledge_dir.glob("*.md")):
        if article_path.name in ("index.md", "log.md"):
            continue
        text = article_path.read_text(encoding="utf-8")
        fm = extract_frontmatter(text)

        # Extract summary from **Sammendrag** line
        summary = ""
        for line in text.split("\n"):
            if line.startswith("**Sammendrag**:"):
                summary = line.replace("**Sammendrag**:", "").strip()
                break

        entries.append({
            "slug": article_path.stem,
            "title": article_path.stem.replace("-", " ").title(),
            "type": fm.get("type", "concept"),
            "status": fm.get("status", "draft"),
            "summary": summary[:80],
        })

    # Write index
    lines = ["# Knowledge Index\n"]
    lines.append(f"**Last compiled**: {now_iso()}\n")
    lines.append(f"**Articles**: {len(entries)}\n\n")
    lines.append("| slug | title | type | status | summary |")
    lines.append("|---|---|---|---|---|")
    for e in entries:
        lines.append(f"| {e['slug']} | {e['title']} | {e['type']} | {e['status']} | {e['summary']} |")
    lines.append("")

    index_path = knowledge_dir / "index.md"
    index_path.write_text("\n".join(lines), encoding="utf-8")
```

- [ ] **Step 2: Write test for compile**

```python
# tests/test_compile.py
"""Tests for compile pipeline."""
from pathlib import Path
from unittest.mock import patch

from arch_knowledge.compile import compile_knowledge, _rebuild_index


MOCK_LLM_RESPONSE = """FILENAME: event-sourcing.md
---
type: decision
status: active
date: 2026-04-13
sources:
  - daily/2026-04-13.md
---

# Event Sourcing

**Sammendrag**: We chose event sourcing for audit trail requirements.

---

Event sourcing stores all state changes as immutable events.
This enables full [[audit-logging]] and temporal queries.

## Changelog

| Dato | Endring | Begrunnelse |
|---|---|---|
| 2026-04-13 | Opprettet | Initial decision |

## Relaterte artikler

- [[audit-logging]]
- [[cqrs-pattern]]"""


def test_compile_creates_articles(tmp_path):
    """Compile creates knowledge articles from daily logs."""
    knowledge_root = tmp_path / "docs" / "arch-knowledge"
    knowledge_root.mkdir(parents=True)
    daily_dir = knowledge_root / "daily"
    daily_dir.mkdir()
    (daily_dir / "2026-04-13.md").write_text("# Daily\n\n## Decision\n- Chose event sourcing")

    with patch("arch_knowledge.compile.find_knowledge_root", return_value=knowledge_root), \
         patch("arch_knowledge.compile.call_llm", return_value=MOCK_LLM_RESPONSE):
        paths = compile_knowledge()
        assert len(paths) == 1
        assert "event-sourcing.md" in paths[0]

    # Check article was written
    article = knowledge_root / "knowledge" / "event-sourcing.md"
    assert article.exists()
    content = article.read_text()
    assert "type: decision" in content
    assert "[[audit-logging]]" in content

    # Check index was rebuilt
    index = knowledge_root / "knowledge" / "index.md"
    assert index.exists()
    assert "event-sourcing" in index.read_text()


def test_compile_skips_unchanged_logs(tmp_path):
    """Compile skips logs that haven't changed since last compile."""
    knowledge_root = tmp_path / "docs" / "arch-knowledge"
    knowledge_root.mkdir(parents=True)
    daily_dir = knowledge_root / "daily"
    daily_dir.mkdir()
    (daily_dir / "2026-04-13.md").write_text("# Daily\n\nSome content")

    with patch("arch_knowledge.compile.find_knowledge_root", return_value=knowledge_root), \
         patch("arch_knowledge.compile.call_llm", return_value=MOCK_LLM_RESPONSE):
        # First compile should work
        paths1 = compile_knowledge()
        assert len(paths1) == 1

        # Second compile should skip (no changes)
        paths2 = compile_knowledge()
        assert "No new or changed" in paths2[0]
```

- [ ] **Step 3: Run tests**

Run: `cd /path/to/repo && python3 -m pytest tests/test_compile.py -v`
Expected: 2 tests PASS

- [ ] **Step 4: Commit**

```bash
git add scripts/arch_knowledge/compile.py tests/test_compile.py
git commit -m "feat: add compile pipeline for knowledge synthesis

Reads daily logs, synthesizes via LLM into typed knowledge articles.
Hash-based change detection, automatic index rebuild."
```

---

## Task 4: Lint — knowledge health checks

**Files:**
- Create: `scripts/arch_knowledge/lint.py`

Seven structural checks plus optional LLM-based contradiction detection.

- [ ] **Step 1: Create lint.py**

```python
# scripts/arch_knowledge/lint.py
"""Knowledge health checks (lint).

Seven checks inspired by Cole Medin's lint.py:
1. Broken links (free)
2. Orphan articles (free)
3. Uncompiled daily logs (free)
4. Stale articles (free)
5. Missing backlinks (free)
6. Sparse articles (free)
7. Contradictions (LLM-based, optional)
"""
from pathlib import Path

from .config import find_knowledge_root, load_compliance_profile, get_llm_config
from .utils import extract_knowledge_links, extract_frontmatter, load_state, file_hash


def lint(structural_only: bool = False) -> list[dict]:
    """Run all lint checks. Returns list of findings.

    Each finding: {"check": str, "level": "error"|"warning"|"info",
                   "message": str, "file": str|None}
    """
    knowledge_root = find_knowledge_root()
    if not knowledge_root:
        return [{"check": "setup", "level": "error",
                 "message": "No docs/arch-knowledge/ found", "file": None}]

    knowledge_dir = knowledge_root / "knowledge"
    daily_dir = knowledge_root / "daily"

    if not knowledge_dir.exists():
        return [{"check": "setup", "level": "error",
                 "message": "No knowledge/ directory found", "file": None}]

    # Build article map
    articles = {}
    for path in knowledge_dir.glob("*.md"):
        if path.name in ("index.md", "log.md"):
            continue
        text = path.read_text(encoding="utf-8")
        articles[path.stem] = {
            "path": path,
            "text": text,
            "frontmatter": extract_frontmatter(text),
            "links": extract_knowledge_links(text),
            "word_count": len(text.split()),
        }

    findings = []

    # Check 1: Broken links
    all_slugs = set(articles.keys())
    for slug, article in articles.items():
        for link in article["links"]:
            if link not in all_slugs:
                findings.append({
                    "check": "broken-link",
                    "level": "error",
                    "message": f"Broken link [[{link}]] in {slug}.md",
                    "file": str(article["path"]),
                })

    # Check 2: Orphan articles (no inbound links)
    inbound = {slug: set() for slug in all_slugs}
    for slug, article in articles.items():
        for link in article["links"]:
            if link in inbound:
                inbound[link].add(slug)
    for slug, sources in inbound.items():
        if not sources:
            findings.append({
                "check": "orphan",
                "level": "warning",
                "message": f"Orphan article: {slug}.md (no inbound links)",
                "file": str(articles[slug]["path"]),
            })

    # Check 3: Uncompiled daily logs
    if daily_dir.exists():
        state = load_state(knowledge_root)
        compiled_hashes = state.get("compiled_hashes", {})
        for log_path in daily_dir.glob("*.md"):
            current_hash = file_hash(log_path)
            if log_path.name not in compiled_hashes or compiled_hashes[log_path.name] != current_hash:
                findings.append({
                    "check": "uncompiled",
                    "level": "warning",
                    "message": f"Uncompiled daily log: {log_path.name}",
                    "file": str(log_path),
                })

    # Check 4: Stale articles (based on config threshold)
    profile = load_compliance_profile(knowledge_root)
    health_config = profile.get("knowledge-health", {})
    stale_threshold = health_config.get("check-stale-articles", "90d")
    if stale_threshold:
        import re
        from datetime import datetime, timedelta, timezone
        days_match = re.match(r"(\d+)d", str(stale_threshold))
        if days_match:
            max_age = timedelta(days=int(days_match.group(1)))
            now = datetime.now(timezone.utc)
            for slug, article in articles.items():
                date_str = article["frontmatter"].get("date")
                if date_str:
                    try:
                        article_date = datetime.fromisoformat(str(date_str)).replace(
                            tzinfo=timezone.utc
                        )
                        if now - article_date > max_age:
                            findings.append({
                                "check": "stale",
                                "level": "info",
                                "message": f"Stale article: {slug}.md (last updated {date_str})",
                                "file": str(article["path"]),
                            })
                    except (ValueError, TypeError):
                        pass

    # Check 5: Missing backlinks (A links to B, but B doesn't link to A)
    for slug, article in articles.items():
        for link in article["links"]:
            if link in articles and slug not in articles[link]["links"]:
                findings.append({
                    "check": "missing-backlink",
                    "level": "info",
                    "message": f"{slug}.md links to [[{link}]] but not vice versa",
                    "file": str(article["path"]),
                })

    # Check 6: Sparse articles (under 200 words)
    for slug, article in articles.items():
        if article["word_count"] < 200:
            findings.append({
                "check": "sparse",
                "level": "warning",
                "message": f"Sparse article: {slug}.md ({article['word_count']} words)",
                "file": str(article["path"]),
            })

    # Check 7: Contradictions (LLM-based, optional)
    if not structural_only and len(articles) >= 2:
        contradiction_findings = _check_contradictions(articles, knowledge_root)
        findings.extend(contradiction_findings)

    return findings


def _check_contradictions(articles: dict, knowledge_root: Path) -> list[dict]:
    """LLM-based contradiction check between articles."""
    from .llm import call_llm

    profile = load_compliance_profile(knowledge_root)
    llm_config = get_llm_config(profile)

    # Build condensed article summaries
    summaries = []
    for slug, article in articles.items():
        fm = article["frontmatter"]
        summaries.append(f"### {slug} (type: {fm.get('type', '?')})\n{article['text'][:500]}")

    prompt = f"""Check these knowledge articles for contradictions.
Only report genuine contradictions where two articles make conflicting claims.
Do NOT report differences in scope or perspective.

If no contradictions found, respond with exactly: NO_CONTRADICTIONS

Otherwise, list each contradiction as:
CONTRADICTION: [slug-a] vs [slug-b]: description

Articles:
{"".join(summaries)}"""

    try:
        result = call_llm(prompt=prompt, system="You detect contradictions in knowledge bases.", config=llm_config)
        if "NO_CONTRADICTIONS" in result:
            return []

        findings = []
        for line in result.split("\n"):
            if line.startswith("CONTRADICTION:"):
                findings.append({
                    "check": "contradiction",
                    "level": "warning",
                    "message": line,
                    "file": None,
                })
        return findings
    except Exception:
        return []
```

- [ ] **Step 2: Write test for lint**

```python
# tests/test_lint.py
"""Tests for knowledge lint checks."""
from pathlib import Path
from unittest.mock import patch

from arch_knowledge.lint import lint


def _setup_articles(knowledge_root: Path, articles: dict[str, str]) -> None:
    """Helper: write articles to knowledge dir."""
    knowledge_dir = knowledge_root / "knowledge"
    knowledge_dir.mkdir(parents=True, exist_ok=True)
    for name, content in articles.items():
        (knowledge_dir / name).write_text(content)


def test_lint_finds_broken_links(tmp_path):
    knowledge_root = tmp_path / "docs" / "arch-knowledge"
    _setup_articles(knowledge_root, {
        "foo.md": "---\ntype: concept\nstatus: active\ndate: 2026-04-13\n---\n# Foo\n\n**Sammendrag**: Foo.\n\nSee [[nonexistent]].\n\n## Relaterte artikler\n\n- [[nonexistent]]",
    })
    with patch("arch_knowledge.lint.find_knowledge_root", return_value=knowledge_root):
        findings = lint(structural_only=True)
    broken = [f for f in findings if f["check"] == "broken-link"]
    assert len(broken) >= 1


def test_lint_finds_orphans(tmp_path):
    knowledge_root = tmp_path / "docs" / "arch-knowledge"
    _setup_articles(knowledge_root, {
        "foo.md": "---\ntype: concept\nstatus: active\ndate: 2026-04-13\n---\n# Foo\n\n**Sammendrag**: Foo.\n\nContent.\n\n## Relaterte artikler\n\n- [[bar]]",
        "bar.md": "---\ntype: concept\nstatus: active\ndate: 2026-04-13\n---\n# Bar\n\n**Sammendrag**: Bar.\n\nContent.\n\n## Relaterte artikler\n\n- [[foo]]",
        "orphan.md": "---\ntype: concept\nstatus: active\ndate: 2026-04-13\n---\n# Orphan\n\n**Sammendrag**: Lonely.\n\nNo links to me.\n\n## Relaterte artikler\n\n- [[foo]]",
    })
    with patch("arch_knowledge.lint.find_knowledge_root", return_value=knowledge_root):
        findings = lint(structural_only=True)
    orphans = [f for f in findings if f["check"] == "orphan"]
    assert any("orphan" in f["message"] for f in orphans)


def test_lint_finds_sparse_articles(tmp_path):
    knowledge_root = tmp_path / "docs" / "arch-knowledge"
    _setup_articles(knowledge_root, {
        "tiny.md": "---\ntype: concept\nstatus: active\ndate: 2026-04-13\n---\n# Tiny\n\n**Sammendrag**: Small.\n\nShort.",
    })
    with patch("arch_knowledge.lint.find_knowledge_root", return_value=knowledge_root):
        findings = lint(structural_only=True)
    sparse = [f for f in findings if f["check"] == "sparse"]
    assert len(sparse) == 1
```

- [ ] **Step 3: Run tests**

Run: `cd /path/to/repo && python3 -m pytest tests/test_lint.py -v`
Expected: 3 tests PASS

- [ ] **Step 4: Commit**

```bash
git add scripts/arch_knowledge/lint.py tests/test_lint.py
git commit -m "feat: add knowledge lint with 7 health checks

Structural: broken links, orphans, uncompiled logs, stale articles,
missing backlinks, sparse articles. Optional: LLM contradiction check."
```

---

## Task 5: CLI entrypoint — all subcommands

**Files:**
- Create: `scripts/arch_knowledge/cli.py`

The unified CLI that ties everything together. Every command is a thin wrapper around the core modules.

- [ ] **Step 1: Create cli.py**

```python
# scripts/arch_knowledge/cli.py
"""arch-knowledge CLI: universal interface for architecture knowledge.

Subcommands:
  bootstrap   — First-time setup of knowledge structure
  context     — Read relevant architecture context
  ingest      — Ingest a source document into knowledge
  search      — Search the knowledge base
  flush       — Filter and store architecture-relevant knowledge
  compile     — Synthesize daily logs into knowledge articles
  lint        — Check knowledge base health
  compliance  — Run compliance check against profile
  propose     — Propose architecture change to central repo
"""
import argparse
import json
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        prog="arch-knowledge",
        description="Creativity-first architecture governance CLI",
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    # bootstrap
    p_bootstrap = sub.add_parser("bootstrap", help="First-time setup")
    p_bootstrap.add_argument("--mode", choices=["standalone", "connected"], default=None,
                             help="Architecture mode")
    p_bootstrap.add_argument("--central-repo", default=None,
                             help="Central architecture repo (org/name)")

    # context
    p_context = sub.add_parser("context", help="Read architecture context")
    p_context.add_argument("--task", default="", help="Current task description")

    # ingest
    p_ingest = sub.add_parser("ingest", help="Ingest a source document")
    p_ingest.add_argument("file", help="Path to source document")

    # search
    p_search = sub.add_parser("search", help="Search knowledge base")
    p_search.add_argument("term", help="Search term")

    # flush
    p_flush = sub.add_parser("flush", help="Filter and store knowledge")
    p_flush.add_argument("--input", dest="input_file", help="Input file path")
    p_flush.add_argument("--session-id", default="", help="Session ID for dedup")

    # compile
    p_compile = sub.add_parser("compile", help="Synthesize daily logs")
    p_compile.add_argument("--all", action="store_true", dest="all_mode",
                           help="Recompile all logs")
    p_compile.add_argument("--file", default=None, help="Specific daily log file")
    p_compile.add_argument("--dry-run", action="store_true", help="Preview only")

    # lint
    p_lint = sub.add_parser("lint", help="Check knowledge health")
    p_lint.add_argument("--structural-only", action="store_true",
                        help="Skip LLM-based checks")
    p_lint.add_argument("--json", action="store_true", dest="json_output",
                        help="Output as JSON")

    # compliance
    p_compliance = sub.add_parser("compliance", help="Run compliance check")
    p_compliance.add_argument("--scope", default=None, help="Scope description")
    p_compliance.add_argument("--structural-only", action="store_true",
                              help="Skip LLM-based checks")

    # propose
    p_propose = sub.add_parser("propose", help="Propose architecture change")
    p_propose.add_argument("--issue-first", action="store_true",
                           help="Create issue instead of PR")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "bootstrap":
        cmd_bootstrap(args)
    elif args.command == "context":
        cmd_context(args)
    elif args.command == "flush":
        cmd_flush(args)
    elif args.command == "compile":
        cmd_compile(args)
    elif args.command == "lint":
        cmd_lint(args)
    elif args.command == "compliance":
        cmd_compliance(args)
    elif args.command == "ingest":
        cmd_ingest(args)
    elif args.command == "search":
        cmd_search(args)
    elif args.command == "propose":
        cmd_propose(args)
    else:
        parser.print_help()
        sys.exit(1)


def cmd_bootstrap(args):
    """First-time setup of knowledge structure."""
    from .config import find_repo_root

    repo_root = find_repo_root()
    knowledge_root = repo_root / "docs" / "arch-knowledge"

    if knowledge_root.exists():
        print(f"Knowledge structure already exists at {knowledge_root}")
        return

    # Create directory structure
    for subdir in ["raw/central", "raw/local", "raw/external", "daily", "knowledge"]:
        (knowledge_root / subdir).mkdir(parents=True, exist_ok=True)

    # Create arch-statement.md
    mode = args.mode or "standalone"
    statement = f"""# Architecture Statement

## Modus
mode: {mode}
"""
    if args.central_repo:
        statement += f"""
## Sentralt arkitekturrepo
central-repo: {args.central_repo}
central-repo-url: https://github.com/{args.central_repo}.git
"""
    statement += """
## Beskrivelse
Kort beskrivelse av dette repoets arkitekturelle kontekst.
"""
    (knowledge_root / "arch-statement.md").write_text(statement, encoding="utf-8")

    # Create default compliance-profile.yaml
    default_profile = """\
# Compliance Profile
# Configure which rules are hard (must fix), soft (should consider), or info.

source:
  sync-strategy: manual

rules:
  hard: []
  soft: []
  info: []

scope:
  include:
    - src/**
    - api/**
  exclude:
    - tests/**

knowledge-health:
  check-orphans: true
  check-missing-concepts: true
  check-stale-articles: 90d
  check-source-conflicts: true
  check-sparse-articles: true
  check-broken-links: true

llm:
  provider: anthropic
  model: claude-sonnet-4-20250514
"""
    (knowledge_root / "compliance-profile.yaml").write_text(default_profile, encoding="utf-8")

    # Create initial index and log
    from .utils import now_iso
    (knowledge_root / "knowledge" / "index.md").write_text(
        f"# Knowledge Index\n\n**Last compiled**: {now_iso()}\n**Articles**: 0\n\n"
        "| slug | title | type | status | summary |\n|---|---|---|---|---|\n",
        encoding="utf-8",
    )
    (knowledge_root / "knowledge" / "log.md").write_text(
        f"# Knowledge Log\n\n- {now_iso()} — Knowledge base initialized\n",
        encoding="utf-8",
    )

    print(f"Knowledge structure created at {knowledge_root}")
    print(f"Mode: {mode}")
    if args.central_repo:
        print(f"Central repo: {args.central_repo}")
    print("\nNext steps:")
    print("1. Edit arch-statement.md with your repo description")
    print("2. Edit compliance-profile.yaml with your rules")
    print("3. Run: arch-knowledge context --task 'describe your first task'")


def cmd_context(args):
    """Read and display relevant architecture context."""
    from .config import find_knowledge_root, parse_arch_statement
    from .utils import read_index

    knowledge_root = find_knowledge_root()
    if not knowledge_root:
        print("No knowledge base found. Run: arch-knowledge bootstrap")
        return

    knowledge_dir = knowledge_root / "knowledge"
    statement = parse_arch_statement(knowledge_root)

    print(f"# Architecture Context")
    print(f"\nMode: {statement['mode']}")
    if statement['central_repo']:
        print(f"Central repo: {statement['central_repo']}")

    # Show index
    entries = read_index(knowledge_dir)
    if entries:
        print(f"\n## Knowledge Base ({len(entries)} articles)\n")
        for e in entries:
            print(f"- **[[{e['slug']}]]** ({e['type']}) — {e['summary']}")
    else:
        print("\n## Knowledge Base\n\nNo articles yet. Run flush/compile or ingest sources.")

    # Show latest daily log
    daily_dir = knowledge_root / "daily"
    if daily_dir.exists():
        daily_logs = sorted(daily_dir.glob("*.md"), reverse=True)
        if daily_logs:
            latest = daily_logs[0]
            content = latest.read_text(encoding="utf-8")
            # Truncate to last 30 lines
            lines = content.splitlines()
            if len(lines) > 30:
                lines = lines[-30:]
            print(f"\n## Latest Daily Log ({latest.name})\n")
            print("\n".join(lines))


def cmd_flush(args):
    """Flush architecture-relevant knowledge."""
    from .flush import flush, flush_from_file

    if args.input_file:
        result = flush_from_file(args.input_file, args.session_id)
    else:
        # Read from stdin
        import sys
        text = sys.stdin.read()
        result = flush(text, args.session_id)

    if result == "FLUSH_OK":
        print("Nothing architecture-relevant found.")
    else:
        print(f"Flushed to daily log:\n{result}")


def cmd_compile(args):
    """Compile daily logs into knowledge articles."""
    from .compile import compile_knowledge

    if args.dry_run:
        print("DRY RUN — would compile the following logs:")
        from .config import find_knowledge_root
        from .utils import load_state, file_hash
        kr = find_knowledge_root()
        if kr:
            daily_dir = kr / "daily"
            state = load_state(kr)
            compiled = state.get("compiled_hashes", {})
            for log in sorted(daily_dir.glob("*.md")):
                h = file_hash(log)
                if log.name not in compiled or compiled[log.name] != h:
                    print(f"  - {log.name}")
        return

    paths = compile_knowledge(all_mode=args.all_mode, specific_file=args.file)
    for p in paths:
        print(p)


def cmd_lint(args):
    """Run knowledge health checks."""
    from .lint import lint as run_lint

    findings = run_lint(structural_only=args.structural_only)

    if args.json_output:
        print(json.dumps(findings, indent=2))
        return

    if not findings:
        print("Knowledge base is healthy.")
        return

    errors = [f for f in findings if f["level"] == "error"]
    warnings = [f for f in findings if f["level"] == "warning"]
    infos = [f for f in findings if f["level"] == "info"]

    if errors:
        print(f"\n## Errors ({len(errors)})\n")
        for f in errors:
            print(f"  ERROR [{f['check']}] {f['message']}")
    if warnings:
        print(f"\n## Warnings ({len(warnings)})\n")
        for f in warnings:
            print(f"  WARN  [{f['check']}] {f['message']}")
    if infos:
        print(f"\n## Info ({len(infos)})\n")
        for f in infos:
            print(f"  INFO  [{f['check']}] {f['message']}")

    sys.exit(1 if errors else 0)


def cmd_compliance(args):
    """Run compliance check. Placeholder — requires Task 7 implementation."""
    print("Compliance check: not yet implemented. Use arch-knowledge lint for knowledge health.")


def cmd_ingest(args):
    """Ingest a source document. Placeholder — requires Task 6 implementation."""
    print(f"Ingest: not yet implemented. File: {args.file}")


def cmd_search(args):
    """Search knowledge base. Placeholder — requires Task 6 implementation."""
    print(f"Search: not yet implemented. Term: {args.term}")


def cmd_propose(args):
    """Propose architecture change. Placeholder — requires Task 8 implementation."""
    print("Propose: not yet implemented.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Test CLI help and bootstrap**

Run: `cd /path/to/repo && python3 -m arch_knowledge.cli --help`
Expected: Shows usage with all subcommands

Run: `cd /path/to/repo && python3 -m arch_knowledge.cli bootstrap --mode standalone`
Expected: Creates docs/arch-knowledge/ with all directories and files

- [ ] **Step 3: Commit**

```bash
git add scripts/arch_knowledge/cli.py
git commit -m "feat: add arch-knowledge CLI with all subcommands

bootstrap, context, flush, compile, lint implemented.
compliance, ingest, search, propose stubbed for later tasks."
```

---

## Task 6: Agent adapter templates

**Files:**
- Create: `install/adapters/claude/settings.json`
- Create: `install/adapters/claude/CLAUDE.md`
- Create: `install/adapters/cursor/.cursorrules`
- Create: `install/adapters/github-copilot/copilot-instructions.md`
- Create: `install/adapters/generic/AGENTS.md`
- Create: `install/adapters/git-hooks/post-commit`
- Create: `install/adapters/git-hooks/pre-push`

These are the thin adapters that make the CLI accessible to each agent platform.

- [ ] **Step 1: Create Claude Code adapter (hooks + instructions)**

`install/adapters/claude/settings.json`:
```json
{
  "hooks": {
    "SessionStart": [
      {
        "type": "command",
        "command": "python3 scripts/arch_knowledge/hooks/session_start.py",
        "timeout": 15000
      }
    ],
    "PreCompact": [
      {
        "type": "command",
        "command": "python3 scripts/arch_knowledge/hooks/pre_compact.py",
        "timeout": 10000
      }
    ],
    "SessionEnd": [
      {
        "type": "command",
        "command": "python3 scripts/arch_knowledge/hooks/session_end.py",
        "timeout": 10000
      }
    ]
  }
}
```

`install/adapters/claude/CLAUDE.md`:
```markdown
# Architecture Knowledge

This repository uses arch-knowledge for architecture governance.

## Available commands

- `arch-knowledge context` — Read relevant architecture context (use before starting work)
- `arch-knowledge compliance` — Run compliance check (use after implementation)
- `arch-knowledge propose` — Propose changes to central architecture
- `arch-knowledge ingest <file>` — Ingest a new source document
- `arch-knowledge search <term>` — Search the knowledge base
- `arch-knowledge lint` — Check knowledge base health

## Knowledge base

Architecture knowledge lives in `docs/arch-knowledge/`:
- `knowledge/index.md` — Start here for an overview
- `knowledge/` — Synthesized articles (concepts, decisions, patterns)
- `daily/` — Daily logs (append-only, auto-captured)
- `raw/` — Imported source documents

## How it works

Knowledge is captured automatically via hooks. You don't need to remember
to document — the system captures architecture-relevant decisions from your
conversations. You can also manually write knowledge articles in `knowledge/`.

Compliance is checked on-demand, not automatically. Run it when you want
to understand how your work aligns with architecture guidelines.
```

- [ ] **Step 2: Create Cursor adapter**

`install/adapters/cursor/.cursorrules`:
```markdown
# Architecture Knowledge

This repository uses arch-knowledge for architecture governance.
Architecture knowledge lives in docs/arch-knowledge/.

Before starting work, read docs/arch-knowledge/knowledge/index.md for context.

Available commands:
- arch-knowledge context — Read relevant architecture context
- arch-knowledge compliance — Run compliance check after implementation
- arch-knowledge flush — Capture architecture decisions from current work
- arch-knowledge lint — Check knowledge base health

After making significant design decisions, run:
arch-knowledge flush --input <relevant-file>

Periodically check compliance:
arch-knowledge compliance
```

- [ ] **Step 3: Create GitHub Copilot adapter**

`install/adapters/github-copilot/copilot-instructions.md`:
```markdown
# Architecture Knowledge

This repository uses arch-knowledge for architecture governance.

## Quick start
1. Read `docs/arch-knowledge/knowledge/index.md` for architecture overview
2. Use `arch-knowledge context` for relevant context before starting work
3. Use `arch-knowledge compliance` to check compliance after implementation

## Knowledge base location
- `docs/arch-knowledge/knowledge/` — Architecture articles
- `docs/arch-knowledge/daily/` — Daily logs (auto-captured)
- `docs/arch-knowledge/raw/` — Source documents

## Commands
- `arch-knowledge context` — Architecture context
- `arch-knowledge compliance` — Compliance check
- `arch-knowledge flush` — Capture architecture decisions
- `arch-knowledge lint` — Knowledge base health
- `arch-knowledge propose` — Propose architecture changes
```

- [ ] **Step 4: Create generic AGENTS.md adapter**

`install/adapters/generic/AGENTS.md`:
```markdown
# Architecture Knowledge — Agent Instructions

This repository uses the arch-knowledge system for architecture governance.

## For any AI agent

1. **Before starting work**: Read `docs/arch-knowledge/knowledge/index.md`
2. **During work**: Make architecture decisions freely
3. **After work**: Run `arch-knowledge compliance` to check alignment
4. **To propose changes**: Run `arch-knowledge propose`

## CLI commands

All commands work from the repository root:

```bash
arch-knowledge context              # Read architecture context
arch-knowledge ingest <file>        # Ingest a source document
arch-knowledge search <term>        # Search knowledge base
arch-knowledge flush --input <file> # Capture architecture knowledge
arch-knowledge compile              # Synthesize daily logs
arch-knowledge lint                 # Check knowledge health
arch-knowledge compliance           # Run compliance check
arch-knowledge propose              # Propose architecture change
arch-knowledge bootstrap            # First-time setup
```

## Knowledge structure

```
docs/arch-knowledge/
├── raw/           — Imported source documents (don't modify)
├── daily/         — Daily logs (append-only, auto-captured)
├── knowledge/     — Synthesized articles (read and write)
│   ├── index.md   — Start here
│   └── *.md       — Typed articles (concept/decision/contract/pattern/review)
├── arch-statement.md       — Repository configuration
└── compliance-profile.yaml — Compliance rules
```
```

- [ ] **Step 5: Create git hooks (universal fallback)**

`install/adapters/git-hooks/post-commit`:
```bash
#!/usr/bin/env bash
# Git post-commit hook: capture architecture knowledge from commit diff.
# Universal fallback for agents without rich hook support.

set -euo pipefail

# Recursion guard
if [ "${ARCH_KNOWLEDGE_INVOKED_BY:-}" = "hook" ]; then
    exit 0
fi
export ARCH_KNOWLEDGE_INVOKED_BY=hook

# Only run if arch-knowledge is available
if ! command -v arch-knowledge &>/dev/null && [ ! -f scripts/arch-knowledge ]; then
    exit 0
fi

# Get commit diff (limit size)
DIFF=$(git diff HEAD~1 HEAD --stat --patch | head -500)

if [ -z "$DIFF" ]; then
    exit 0
fi

# Write to temp file and flush in background
TMPFILE=$(mktemp)
echo "$DIFF" > "$TMPFILE"

if [ -f scripts/arch-knowledge ]; then
    nohup bash scripts/arch-knowledge flush --input "$TMPFILE" --session-id "git-$$" >/dev/null 2>&1 &
elif command -v arch-knowledge &>/dev/null; then
    nohup arch-knowledge flush --input "$TMPFILE" --session-id "git-$$" >/dev/null 2>&1 &
fi
```

`install/adapters/git-hooks/pre-push`:
```bash
#!/usr/bin/env bash
# Git pre-push hook: compile daily knowledge before pushing.
# Universal fallback for agents without rich hook support.

set -euo pipefail

# Recursion guard
if [ "${ARCH_KNOWLEDGE_INVOKED_BY:-}" = "hook" ]; then
    exit 0
fi
export ARCH_KNOWLEDGE_INVOKED_BY=hook

# Only run if arch-knowledge is available and there are daily logs
if [ ! -d docs/arch-knowledge/daily ]; then
    exit 0
fi

if [ -f scripts/arch-knowledge ]; then
    bash scripts/arch-knowledge compile 2>/dev/null || true
elif command -v arch-knowledge &>/dev/null; then
    arch-knowledge compile 2>/dev/null || true
fi
```

- [ ] **Step 6: Commit**

```bash
git add install/adapters/
git commit -m "feat: add agent-specific adapters for Claude, Cursor, Copilot, git

Claude Code: hooks (session-start, pre-compact, session-end) + CLAUDE.md
Cursor: .cursorrules with arch-knowledge instructions
GitHub Copilot: copilot-instructions.md
Generic: AGENTS.md for any AI agent
Git hooks: post-commit (flush) and pre-push (compile) as universal fallback"
```

---

## Task 7: Claude Code hooks (session-start, pre-compact, session-end)

**Files:**
- Create: `scripts/arch_knowledge/hooks/__init__.py`
- Create: `scripts/arch_knowledge/hooks/session_start.py`
- Create: `scripts/arch_knowledge/hooks/pre_compact.py`
- Create: `scripts/arch_knowledge/hooks/session_end.py`

These hooks implement the Medin pattern: fast extraction (<10s), async flush in background.

- [ ] **Step 1: Create hooks/__init__.py**

```python
# scripts/arch_knowledge/hooks/__init__.py
"""Claude Code hooks for automatic knowledge capture."""
```

- [ ] **Step 2: Create session_start.py — inject context**

```python
#!/usr/bin/env python3
# scripts/arch_knowledge/hooks/session_start.py
"""SessionStart hook: inject architecture context into Claude Code session.

Reads knowledge/index.md and latest daily log, outputs as JSON
for Claude Code's hookSpecificOutput.additionalContext.
"""
import json
import os
import sys
from pathlib import Path

# Recursion guard
if os.environ.get("ARCH_KNOWLEDGE_INVOKED_BY") == "hook":
    sys.exit(0)

def main():
    # Find knowledge root
    cwd = Path.cwd()
    knowledge_root = None
    for parent in [cwd, *cwd.parents]:
        candidate = parent / "docs" / "arch-knowledge"
        if candidate.is_dir():
            knowledge_root = candidate
            break

    if not knowledge_root:
        return

    context_parts = []
    max_chars = 20000

    # Read index
    index_path = knowledge_root / "knowledge" / "index.md"
    if index_path.exists():
        context_parts.append(index_path.read_text(encoding="utf-8"))

    # Read latest daily log (last 30 lines)
    daily_dir = knowledge_root / "daily"
    if daily_dir.exists():
        daily_logs = sorted(daily_dir.glob("*.md"), reverse=True)
        if daily_logs:
            content = daily_logs[0].read_text(encoding="utf-8")
            lines = content.splitlines()
            if len(lines) > 30:
                lines = lines[-30:]
            context_parts.append(f"\n## Latest: {daily_logs[0].name}\n" + "\n".join(lines))

    context = "\n\n".join(context_parts)
    if len(context) > max_chars:
        context = context[:max_chars] + "\n\n[truncated]"

    # Output for Claude Code hook system
    print(json.dumps({
        "additionalContext": f"# Architecture Knowledge Context\n\n{context}"
    }))


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Create pre_compact.py — capture before context compression**

```python
#!/usr/bin/env python3
# scripts/arch_knowledge/hooks/pre_compact.py
"""PreCompact hook: capture architecture knowledge before context compression.

Extracts conversation context that would be lost during summarization
and spawns flush in background.
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# Recursion guard
if os.environ.get("ARCH_KNOWLEDGE_INVOKED_BY") == "hook":
    sys.exit(0)


def main():
    # Read conversation from stdin (Claude Code passes JSONL)
    conversation = ""
    try:
        raw = sys.stdin.read()
        if raw:
            lines = raw.strip().split("\n")
            # Parse last 30 turns, cap at 15000 chars
            turns = []
            for line in lines[-30:]:
                try:
                    entry = json.loads(line)
                    role = entry.get("role", "unknown")
                    content = entry.get("content", "")
                    if isinstance(content, list):
                        content = " ".join(
                            c.get("text", "") for c in content if isinstance(c, dict)
                        )
                    turns.append(f"**{role}**: {content}")
                except json.JSONDecodeError:
                    turns.append(line)
            conversation = "\n\n".join(turns)
    except Exception:
        return

    if not conversation or len(conversation.split()) < 50:
        return  # Too short to be worth flushing

    # Cap at 15000 chars
    if len(conversation) > 15000:
        conversation = conversation[:15000] + "\n\n[truncated]"

    # Write to temp file
    tmpfile = tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False)
    tmpfile.write(f"# Pre-compact capture\n\n{conversation}")
    tmpfile.close()

    # Spawn flush in background
    script_dir = Path(__file__).parent.parent.parent
    env = os.environ.copy()
    env["ARCH_KNOWLEDGE_INVOKED_BY"] = "hook"

    subprocess.Popen(
        [sys.executable, "-m", "arch_knowledge.cli", "flush",
         "--input", tmpfile.name, "--session-id", f"precompact-{os.getpid()}"],
        cwd=str(script_dir),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Create session_end.py — capture at session close**

```python
#!/usr/bin/env python3
# scripts/arch_knowledge/hooks/session_end.py
"""SessionEnd hook: capture architecture knowledge at session close.

Same extraction logic as pre_compact, but triggers at session end.
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# Recursion guard
if os.environ.get("ARCH_KNOWLEDGE_INVOKED_BY") == "hook":
    sys.exit(0)


def main():
    # Read conversation from stdin
    conversation = ""
    try:
        raw = sys.stdin.read()
        if raw:
            lines = raw.strip().split("\n")
            turns = []
            for line in lines[-30:]:
                try:
                    entry = json.loads(line)
                    role = entry.get("role", "unknown")
                    content = entry.get("content", "")
                    if isinstance(content, list):
                        content = " ".join(
                            c.get("text", "") for c in content if isinstance(c, dict)
                        )
                    turns.append(f"**{role}**: {content}")
                except json.JSONDecodeError:
                    turns.append(line)
            conversation = "\n\n".join(turns)
    except Exception:
        return

    if not conversation or len(conversation.split()) < 50:
        return

    if len(conversation) > 15000:
        conversation = conversation[:15000] + "\n\n[truncated]"

    tmpfile = tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False)
    tmpfile.write(f"# Session-end capture\n\n{conversation}")
    tmpfile.close()

    script_dir = Path(__file__).parent.parent.parent
    env = os.environ.copy()
    env["ARCH_KNOWLEDGE_INVOKED_BY"] = "hook"

    subprocess.Popen(
        [sys.executable, "-m", "arch_knowledge.cli", "flush",
         "--input", tmpfile.name, "--session-id", f"session-end-{os.getpid()}"],
        cwd=str(script_dir),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Commit**

```bash
git add scripts/arch_knowledge/hooks/
git commit -m "feat: add Claude Code hooks for automatic knowledge capture

session_start: injects knowledge context at session start
pre_compact: captures knowledge before context compression
session_end: captures knowledge at session close
All hooks spawn flush async in background (<10s)."
```

---

## Task 8: New skills (SKILL.md wrappers)

**Files:**
- Create: `.github/skills/arch-context/SKILL.md`
- Create: `.github/skills/arch-compliance/SKILL.md`
- Create: `.github/skills/arch-propose/SKILL.md`

Skills are thin markdown wrappers that instruct the agent to use the CLI.

- [ ] **Step 1: Create arch-context skill**

Write `.github/skills/arch-context/SKILL.md` — full skill definition that instructs the agent to use `arch-knowledge context`, `arch-knowledge ingest`, and `arch-knowledge search`. Includes bootstrap guidance, ingest workflow, and the knowledge structure explained.

- [ ] **Step 2: Create arch-compliance skill**

Write `.github/skills/arch-compliance/SKILL.md` — instructs agent to run `arch-knowledge compliance`, interpret the report, and present findings to the user. Includes guidance on hard/soft/info categories and the feedback loop.

- [ ] **Step 3: Create arch-propose skill**

Write `.github/skills/arch-propose/SKILL.md` — instructs agent to gather evidence from knowledge articles, classify the change, and create a PR via `arch-knowledge propose` or `gh`. Includes standalone/connected mode awareness.

- [ ] **Step 4: Commit**

```bash
git add .github/skills/arch-context/ .github/skills/arch-compliance/ .github/skills/arch-propose/
git commit -m "feat: add new skills (arch-context, arch-compliance, arch-propose)

Thin SKILL.md wrappers that instruct agents to use arch-knowledge CLI.
Replace arch-intake, arch-consume, arch-escalate."
```

---

## Task 9: Remove old skills and hooks

**Files:**
- Delete: `.github/skills/arch-intake/`
- Delete: `.github/skills/arch-consume/`
- Delete: `.github/skills/arch-escalate/`
- Delete: `.github/skills/arch-brainstorming/`
- Delete: `.github/skills/arch-writing-plans/`
- Delete: `.github/skills/arch-systematic-debugging/`
- Delete: `.github/skills/arch-requesting-code-review/`
- Delete: `.github/hooks/arch-policy.json`

- [ ] **Step 1: Remove old skills**

```bash
rm -rf .github/skills/arch-intake
rm -rf .github/skills/arch-consume
rm -rf .github/skills/arch-escalate
rm -rf .github/skills/arch-brainstorming
rm -rf .github/skills/arch-writing-plans
rm -rf .github/skills/arch-systematic-debugging
rm -rf .github/skills/arch-requesting-code-review
```

- [ ] **Step 2: Remove old hooks**

```bash
rm .github/hooks/arch-policy.json
```

- [ ] **Step 3: Verify remaining skills structure**

```bash
ls -la .github/skills/
# Expected:
# agent-arch-install/  (kept, will be updated)
# arch-context/        (new)
# arch-compliance/     (new)
# arch-propose/        (new)
# arch-governance/     (kept, will be updated)
```

- [ ] **Step 4: Commit**

```bash
git add -A .github/skills/ .github/hooks/
git commit -m "chore: remove old gating skills and blocking hooks

Removed: arch-intake, arch-consume, arch-escalate, arch-brainstorming,
arch-writing-plans, arch-systematic-debugging, arch-requesting-code-review.
Removed: arch-policy.json blocking hooks.
Kept: agent-arch-install, arch-governance, new skills."
```

---

## Task 10: Update installation system

**Files:**
- Modify: `install/profiles/solution-standard.manifest`
- Modify: `.github/skills/agent-arch-install/install-method.sh`
- Create: `templates/arch-statement.md.tmpl`
- Create: `templates/compliance-profile.yaml.tmpl`

- [ ] **Step 1: Create new templates**

`templates/arch-statement.md.tmpl`:
```markdown
# Architecture Statement

## Modus
mode: standalone

## Beskrivelse
[Beskriv dette repoets arkitekturelle kontekst]
```

`templates/compliance-profile.yaml.tmpl`:
```yaml
# Compliance Profile — ${REPO_NAME}

source:
  sync-strategy: manual

rules:
  hard: []
  soft: []
  info: []

scope:
  include:
    - src/**
    - api/**
  exclude:
    - tests/**

knowledge-health:
  check-orphans: true
  check-missing-concepts: true
  check-stale-articles: 90d
  check-source-conflicts: true
  check-sparse-articles: true
  check-broken-links: true

llm:
  provider: anthropic
  model: claude-sonnet-4-20250514
```

- [ ] **Step 2: Update solution-standard.manifest**

Rewrite `install/profiles/solution-standard.manifest` to map the new file structure: new skills, CLI scripts, adapters, templates, knowledge bootstrap directories.

- [ ] **Step 3: Update install-method.sh**

Update `.github/skills/agent-arch-install/install-method.sh` to:
- Use new manifest
- Bootstrap knowledge directory structure
- Install agent adapters based on detected tools
- Set up git hooks

- [ ] **Step 4: Commit**

```bash
git add install/ templates/ .github/skills/agent-arch-install/
git commit -m "feat: update installation system for knowledge-based governance

New manifest with knowledge structure, CLI scripts, agent adapters.
Templates for arch-statement.md and compliance-profile.yaml."
```

---

## Task 11: Update arch-governance for knowledge maintenance

**Files:**
- Modify: `.github/skills/arch-governance/SKILL.md`

- [ ] **Step 1: Update arch-governance skill**

Update `.github/skills/arch-governance/SKILL.md` to:
- Maintain sentral `knowledge/` in addition to `raw/`
- Use `arch-knowledge compile` for knowledge synthesis
- Use `arch-knowledge lint` for health checks
- Handle incoming PRs from `arch-propose`

- [ ] **Step 2: Commit**

```bash
git add .github/skills/arch-governance/
git commit -m "feat: update arch-governance to maintain central knowledge base

Now maintains knowledge/ layer alongside raw/ documents.
Uses arch-knowledge CLI for compilation and health checks."
```

---

## Task 12: Update documentation

**Files:**
- Modify: `docs/adoption/` — update with new model
- Modify: `docs/method/` — add knowledge pattern documentation
- Modify: `README.md` — update project description

- [ ] **Step 1: Update README.md**

Update to reflect the creativity-first model, three skills, CLI, and knowledge structure.

- [ ] **Step 2: Update docs/adoption/**

Rewrite adoption guides for the new model: bootstrap, daily use, compliance workflow.

- [ ] **Step 3: Update docs/method/**

Add knowledge pattern documentation: three layers, article types, flush/compile pipeline, agent adapters.

- [ ] **Step 4: Commit**

```bash
git add README.md docs/
git commit -m "docs: update documentation for creativity-first governance model

New adoption guides, method documentation, and README reflecting
the shift from gating to knowledge-based governance."
```

---

## Task 13: Final integration test

- [ ] **Step 1: Run full test suite**

Run: `cd /path/to/repo && python3 -m pytest tests/ -v`
Expected: All tests pass

- [ ] **Step 2: Test bootstrap end-to-end**

```bash
# Create a temp directory simulating a solution repo
mkdir -p /tmp/test-solution && cd /tmp/test-solution && git init
# Copy scripts and run bootstrap
cp -r /path/to/agent-arch/scripts .
python3 -m arch_knowledge.cli bootstrap --mode standalone
# Verify structure
ls docs/arch-knowledge/
# Expected: raw/ daily/ knowledge/ arch-statement.md compliance-profile.yaml
```

- [ ] **Step 3: Test context command**

```bash
cd /tmp/test-solution
python3 -m arch_knowledge.cli context
# Expected: Shows knowledge base (empty), mode: standalone
```

- [ ] **Step 4: Test lint on empty knowledge base**

```bash
cd /tmp/test-solution
python3 -m arch_knowledge.cli lint --structural-only
# Expected: "Knowledge base is healthy." (no articles = no issues)
```

- [ ] **Step 5: Commit final state**

```bash
git add -A
git commit -m "chore: integration test verification complete"
```

---

## Execution Summary

| Task | Description | Estimated effort |
|---|---|---|
| 1 | Python project setup + core config/utils/llm | Medium |
| 2 | Flush pipeline | Small |
| 3 | Compile pipeline | Medium |
| 4 | Lint (7 checks) | Small |
| 5 | CLI entrypoint | Medium |
| 6 | Agent adapter templates | Small |
| 7 | Claude Code hooks | Small |
| 8 | New skills (SKILL.md) | Medium |
| 9 | Remove old skills/hooks | Small |
| 10 | Update installation system | Medium |
| 11 | Update arch-governance | Small |
| 12 | Update documentation | Medium |
| 13 | Integration test | Small |

**Dependencies:**
- Tasks 2-5 depend on Task 1 (core infrastructure)
- Task 7 depends on Tasks 1-2 (flush pipeline)
- Task 8 depends on Task 5 (CLI)
- Task 9 can run independently (just deletion)
- Task 10 depends on Tasks 6, 8 (adapters and skills)
- Tasks 11-12 can run after Task 8
- Task 13 runs last
