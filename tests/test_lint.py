"""Tests for deterministic knowledge linting."""

from __future__ import annotations

from arch_knowledge.lint import lint_knowledge


def test_lint_reports_missing_index_and_frontmatter(tmp_path):
    """Lint should report basic structural problems."""
    knowledge_root = tmp_path / "docs" / "arch-knowledge"
    knowledge_dir = knowledge_root / "knowledge"
    knowledge_dir.mkdir(parents=True)
    (knowledge_dir / "broken.md").write_text("# Broken\n\nNo frontmatter here.", encoding="utf-8")

    problems = lint_knowledge(knowledge_root)

    assert any("index.md is missing" in problem for problem in problems)
    assert any("missing frontmatter" in problem for problem in problems)


def test_lint_accepts_valid_structure(tmp_path):
    """Lint should return no problems for a minimal valid knowledge base."""
    knowledge_root = tmp_path / "docs" / "arch-knowledge"
    knowledge_dir = knowledge_root / "knowledge"
    daily_dir = knowledge_root / "daily"
    knowledge_dir.mkdir(parents=True)
    daily_dir.mkdir(parents=True)
    (daily_dir / "2026-04-14.md").write_text("# Daily", encoding="utf-8")
    (knowledge_dir / "index.md").write_text(
        "# Knowledge Index\n\n| slug | title | type | status | summary |\n|---|---|---|---|---|\n| event-sourcing | Event Sourcing | decision | active | Summary |\n",
        encoding="utf-8",
    )
    (knowledge_dir / "event-sourcing.md").write_text(
        """---
type: decision
status: active
date: 2026-04-14
sources:
  - daily/2026-04-14.md
---

# Event Sourcing

**Sammendrag**: Summary

---

Uses [[audit-logging]] and [[cqrs-pattern]].
""",
        encoding="utf-8",
    )
    (knowledge_dir / "audit-logging.md").write_text(
        """---
type: concept
status: active
date: 2026-04-14
sources:
  - daily/2026-04-14.md
---

# Audit Logging

**Sammendrag**: Summary

---

Related to [[event-sourcing]] and [[cqrs-pattern]].
""",
        encoding="utf-8",
    )
    (knowledge_dir / "cqrs-pattern.md").write_text(
        """---
type: pattern
status: active
date: 2026-04-14
sources:
  - daily/2026-04-14.md
---

# CQRS Pattern

**Sammendrag**: Summary

---

Related to [[event-sourcing]] and [[audit-logging]].
""",
        encoding="utf-8",
    )

    problems = lint_knowledge(knowledge_root)

    assert problems == []
