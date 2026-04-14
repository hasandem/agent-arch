"""Tests for compile pipeline."""

from __future__ import annotations

from unittest.mock import patch

from arch_knowledge.compile import compile_knowledge

MOCK_LLM_RESPONSE = """FILENAME: event-sourcing.md
---
type: decision
status: active
date: 2026-04-14
sources:
  - daily/2026-04-14.md
---

# Event Sourcing

**Sammendrag**: We chose event sourcing for audit trail requirements.

---

Event sourcing stores all state changes as immutable events.
This enables full [[audit-logging]] and temporal queries.

## Changelog

| Dato | Endring | Begrunnelse |
|---|---|---|
| 2026-04-14 | Opprettet | Initial decision |

## Relaterte artikler

- [[audit-logging]]
- [[cqrs-pattern]]
"""


def test_compile_creates_articles_and_index(tmp_path):
    """Compile writes validated articles and rebuilds the index."""
    knowledge_root = tmp_path / "docs" / "arch-knowledge"
    daily_dir = knowledge_root / "daily"
    daily_dir.mkdir(parents=True)
    (daily_dir / "2026-04-14.md").write_text("# Daily\n\n## Decision\n- Chose event sourcing", encoding="utf-8")

    with (
        patch("arch_knowledge.compile.find_knowledge_root", return_value=knowledge_root),
        patch("arch_knowledge.compile.call_llm_task", return_value=MOCK_LLM_RESPONSE),
    ):
        paths = compile_knowledge()

    assert len(paths) == 1
    article = knowledge_root / "knowledge" / "event-sourcing.md"
    assert article.exists()
    assert "event sourcing" in article.read_text(encoding="utf-8").lower()
    index = knowledge_root / "knowledge" / "index.md"
    assert index.exists()
    assert "event-sourcing" in index.read_text(encoding="utf-8")


def test_compile_skips_unchanged_logs(tmp_path):
    """Compile should skip daily logs that have already been processed."""
    knowledge_root = tmp_path / "docs" / "arch-knowledge"
    daily_dir = knowledge_root / "daily"
    daily_dir.mkdir(parents=True)
    (daily_dir / "2026-04-14.md").write_text("# Daily\n\nSome content", encoding="utf-8")

    with (
        patch("arch_knowledge.compile.find_knowledge_root", return_value=knowledge_root),
        patch("arch_knowledge.compile.call_llm_task", return_value=MOCK_LLM_RESPONSE),
    ):
        first = compile_knowledge()
        second = compile_knowledge()

    assert len(first) == 1
    assert second == ["No new or changed daily logs to compile."]


def test_compile_rejects_invalid_article_output(tmp_path):
    """Compile should report invalid article output instead of writing junk."""
    knowledge_root = tmp_path / "docs" / "arch-knowledge"
    daily_dir = knowledge_root / "daily"
    daily_dir.mkdir(parents=True)
    (daily_dir / "2026-04-14.md").write_text("# Daily\n\nSome content", encoding="utf-8")

    with (
        patch("arch_knowledge.compile.find_knowledge_root", return_value=knowledge_root),
        patch("arch_knowledge.compile.call_llm_task", return_value="FILENAME: broken.md\n\nno frontmatter"),
    ):
        result = compile_knowledge()

    assert result[0].startswith("ERROR:")
    assert not (knowledge_root / "knowledge" / "broken.md").exists()
