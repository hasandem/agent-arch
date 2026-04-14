"""Flush pipeline for architecture-relevant knowledge capture."""

from __future__ import annotations

import time
from pathlib import Path

from .config import find_knowledge_root, get_llm_config
from .llm import AdapterError, call_llm_task
from .utils import append_to_daily, load_state, save_state

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
    """Filter input for architecture-relevant content and store it."""
    knowledge_root = find_knowledge_root()
    if not knowledge_root:
        return "ERROR: No docs/arch-knowledge/ found. Run arch-knowledge bootstrap first."

    state_path = knowledge_root / ".state.json"
    if session_id:
        state = load_state(state_path)
        last_flush = state.get("last_flush", {})
        last_time = last_flush.get(session_id, 0)
        if time.time() - last_time < FLUSH_DEDUP_WINDOW_SECONDS:
            return "FLUSH_OK"

    max_chars = 15000
    if len(input_text) > max_chars:
        input_text = input_text[:max_chars] + "\n\n[... truncated ...]"

    try:
        result = call_llm_task(
            task="flush",
            input_data=input_text,
            options={"max_chars": max_chars},
            system=FLUSH_SYSTEM_PROMPT,
            config=get_llm_config(knowledge_root),
        ).strip()
    except AdapterError as exc:
        return f"ERROR: {exc}"

    if result == "FLUSH_OK":
        return result

    append_to_daily(knowledge_root / "daily", result)

    if session_id:
        state = load_state(state_path)
        state.setdefault("last_flush", {})[session_id] = time.time()
        save_state(state_path, state)

    return result


def flush_from_file(filepath: str, session_id: str = "") -> str:
    """Read a file and flush its contents."""
    return flush(Path(filepath).read_text(encoding="utf-8"), session_id=session_id)
