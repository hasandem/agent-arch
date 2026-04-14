"""Compile daily architecture logs into validated knowledge articles."""

from __future__ import annotations

from pathlib import Path

from .config import find_knowledge_root, get_llm_config
from .llm import AdapterError, call_llm_task
from .utils import (
    append_to_log,
    extract_frontmatter,
    file_hash,
    load_state,
    now_iso,
    save_state,
    today_iso,
)

COMPILE_SYSTEM_PROMPT = """\
You are an architecture knowledge compiler. Given daily logs and existing
knowledge articles, synthesize the information into structured articles.

Each article must:
- start with a FILENAME: slug-name.md line
- include valid YAML frontmatter with type, status, date, and sources
- include a markdown title
- include a **Sammendrag** line
- include at least two [[knowledge-links]] where appropriate

Separate multiple articles with ===ARTICLE_BREAK===.
Return only article content."""

REQUIRED_FRONTMATTER_KEYS = {"type", "status", "date", "sources"}


def compile_knowledge(all_mode: bool = False, specific_file: str | None = None) -> list[str]:
    """Compile changed daily logs into knowledge articles."""
    knowledge_root = find_knowledge_root()
    if not knowledge_root:
        return ["ERROR: No docs/arch-knowledge/ found."]

    daily_dir = knowledge_root / "daily"
    knowledge_dir = knowledge_root / "knowledge"
    state_path = knowledge_root / ".state.json"
    knowledge_dir.mkdir(parents=True, exist_ok=True)

    if not daily_dir.exists():
        return ["No daily logs found."]

    state = load_state(state_path)
    compiled_hashes = state.get("compiled_hashes", {})
    logs_to_process = _select_logs(daily_dir, compiled_hashes, all_mode, specific_file)
    if not logs_to_process:
        return ["No new or changed daily logs to compile."]

    prompt_input = {
        "daily_logs": _combine_files(logs_to_process, prefix="Source"),
        "existing_articles": _combine_existing_articles(knowledge_dir),
    }

    try:
        response = call_llm_task(
            task="compile",
            system=COMPILE_SYSTEM_PROMPT,
            input_data=prompt_input,
            config=get_llm_config(knowledge_root),
            options={"date": today_iso()},
        )
    except AdapterError as exc:
        return [f"ERROR: {exc}"]

    articles = _parse_articles(response)
    if not articles:
        return ["ERROR: No valid articles returned by compile adapter."]

    created_paths: list[str] = []
    for filename, content in articles:
        error = _validate_article(content, knowledge_root)
        if error:
            return [f"ERROR: {filename}: {error}"]

        article_path = knowledge_dir / filename
        article_path.write_text(content.rstrip() + "\n", encoding="utf-8")
        created_paths.append(str(article_path))
        append_to_log(knowledge_dir, f"Compiled: {filename}")

    for log_path in logs_to_process:
        compiled_hashes[log_path.name] = file_hash(log_path)
    state["compiled_hashes"] = compiled_hashes
    save_state(state_path, state)
    _rebuild_index(knowledge_dir)
    return created_paths


def _select_logs(
    daily_dir: Path,
    compiled_hashes: dict,
    all_mode: bool,
    specific_file: str | None,
) -> list[Path]:
    if specific_file:
        candidates = [daily_dir / specific_file]
    else:
        candidates = sorted(daily_dir.glob("*.md"))
    if all_mode:
        return [path for path in candidates if path.exists()]
    return [
        path
        for path in candidates
        if path.exists() and file_hash(path) != compiled_hashes.get(path.name)
    ]


def _combine_files(paths: list[Path], *, prefix: str) -> str:
    chunks = []
    for path in paths:
        chunks.append(f"### {prefix}: {path.name}\n\n{path.read_text(encoding='utf-8')}")
    return "\n\n".join(chunks)


def _combine_existing_articles(knowledge_dir: Path) -> str:
    article_paths = [
        path
        for path in sorted(knowledge_dir.glob("*.md"))
        if path.name not in {"index.md", "log.md"}
    ]
    return _combine_files(article_paths, prefix="Existing") if article_paths else "(none yet)"


def _parse_articles(response: str) -> list[tuple[str, str]]:
    articles: list[tuple[str, str]] = []
    for block in response.split("===ARTICLE_BREAK==="):
        text = block.strip()
        if not text:
            continue
        lines = text.splitlines()
        filename = ""
        content_lines: list[str] = []
        for index, line in enumerate(lines):
            if line.startswith("FILENAME:"):
                filename = line.split(":", 1)[1].strip()
                content_lines = lines[index + 1 :]
                break
        if not filename:
            continue
        if not filename.endswith(".md"):
            filename += ".md"
        articles.append((filename, "\n".join(content_lines).strip()))
    return articles


def _validate_article(content: str, knowledge_root: Path) -> str | None:
    frontmatter, body = extract_frontmatter(content)
    if not frontmatter:
        return "missing frontmatter"
    missing = REQUIRED_FRONTMATTER_KEYS - set(frontmatter.keys())
    if missing:
        return f"missing frontmatter keys: {', '.join(sorted(missing))}"
    if not isinstance(frontmatter.get("sources"), list) or not frontmatter["sources"]:
        return "sources must be a non-empty list"
    for source in frontmatter["sources"]:
        if not isinstance(source, str):
            return "sources entries must be strings"
        if not (knowledge_root / source).exists():
            return f"missing source file: {source}"
    if "# " not in body:
        return "missing markdown title"
    if "**Sammendrag**:" not in body:
        return "missing summary"
    return None


def _rebuild_index(knowledge_dir: Path) -> None:
    entries = []
    for article_path in sorted(knowledge_dir.glob("*.md")):
        if article_path.name in {"index.md", "log.md"}:
            continue
        text = article_path.read_text(encoding="utf-8")
        frontmatter, body = extract_frontmatter(text)
        title = article_path.stem.replace("-", " ").title()
        for line in body.splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                break
        summary = ""
        for line in body.splitlines():
            if line.startswith("**Sammendrag**:"):
                summary = line.split(":", 1)[1].strip()
                break
        entries.append(
            {
                "slug": article_path.stem,
                "title": title,
                "type": frontmatter.get("type", "unknown"),
                "status": frontmatter.get("status", "unknown"),
                "summary": summary,
            }
        )

    lines = [
        "# Knowledge Index",
        "",
        f"**Last compiled**: {now_iso()}",
        f"**Articles**: {len(entries)}",
        "",
        "| slug | title | type | status | summary |",
        "|---|---|---|---|---|",
    ]
    for entry in entries:
        lines.append(
            f"| {entry['slug']} | {entry['title']} | {entry['type']} | {entry['status']} | {entry['summary']} |"
        )
    lines.append("")
    (knowledge_dir / "index.md").write_text("\n".join(lines), encoding="utf-8")
