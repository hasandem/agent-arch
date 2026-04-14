"""Tests for the flush pipeline."""

from __future__ import annotations

from unittest.mock import patch

from arch_knowledge.flush import flush


def test_flush_ok_when_nothing_relevant(tmp_path):
    """Flush returns FLUSH_OK when the LLM finds nothing relevant."""
    knowledge_root = tmp_path / "docs" / "arch-knowledge"
    knowledge_root.mkdir(parents=True)

    with (
        patch("arch_knowledge.flush.find_knowledge_root", return_value=knowledge_root),
        patch("arch_knowledge.flush.call_llm_task", return_value="FLUSH_OK"),
    ):
        result = flush("just some routine file reading")

    assert result == "FLUSH_OK"


def test_flush_appends_to_daily_when_relevant(tmp_path):
    """Flush appends filtered content to the daily log."""
    knowledge_root = tmp_path / "docs" / "arch-knowledge"
    knowledge_root.mkdir(parents=True)

    with (
        patch("arch_knowledge.flush.find_knowledge_root", return_value=knowledge_root),
        patch(
            "arch_knowledge.flush.call_llm_task",
            return_value="## Decisions\n- Chose event sourcing",
        ),
    ):
        result = flush("We decided to use event sourcing for audit trail")

    assert "Decisions" in result
    daily_dir = knowledge_root / "daily"
    daily_files = list(daily_dir.glob("*.md"))
    assert len(daily_files) == 1
    assert "event sourcing" in daily_files[0].read_text(encoding="utf-8")


def test_flush_deduplicates_by_session(tmp_path):
    """Flush skips when the same session flushed within the dedup window."""
    knowledge_root = tmp_path / "docs" / "arch-knowledge"
    knowledge_root.mkdir(parents=True)

    with (
        patch("arch_knowledge.flush.find_knowledge_root", return_value=knowledge_root),
        patch("arch_knowledge.flush.call_llm_task", return_value="## Decisions\n- Something"),
    ):
        result1 = flush("some input", session_id="session-1")
        result2 = flush("some input", session_id="session-1")

    assert result1 != "FLUSH_OK"
    assert result2 == "FLUSH_OK"
