"""Deterministic linting for local architecture knowledge."""

from __future__ import annotations

from pathlib import Path

from .utils import extract_frontmatter, extract_knowledge_links, file_hash, load_state

REQUIRED_FRONTMATTER_KEYS = {"type", "status", "date", "sources"}


def lint_knowledge(knowledge_root: Path) -> list[str]:
    """Return a list of knowledge base problems."""
    problems: list[str] = []
    knowledge_dir = knowledge_root / "knowledge"
    daily_dir = knowledge_root / "daily"
    state_path = knowledge_root / ".state.json"

    if not knowledge_dir.exists():
        return ["knowledge/ directory is missing"]

    index_path = knowledge_dir / "index.md"
    if not index_path.exists():
        problems.append("knowledge/index.md is missing")

    article_paths = [
        path
        for path in sorted(knowledge_dir.glob("*.md"))
        if path.name not in {"index.md", "log.md"}
    ]

    known_slugs = {path.stem for path in article_paths}
    seen_slugs: set[str] = set()
    for article_path in article_paths:
        if article_path.stem in seen_slugs:
            problems.append(f"{article_path.name}: duplicate slug")
        seen_slugs.add(article_path.stem)

        text = article_path.read_text(encoding="utf-8")
        frontmatter, body = extract_frontmatter(text)
        if not frontmatter:
            problems.append(f"{article_path.name}: missing frontmatter")
            continue

        missing = REQUIRED_FRONTMATTER_KEYS - set(frontmatter.keys())
        if missing:
            problems.append(
                f"{article_path.name}: missing frontmatter keys: {', '.join(sorted(missing))}"
            )

        if "**Sammendrag**:" not in body:
            problems.append(f"{article_path.name}: missing summary")

        for source in frontmatter.get("sources", []):
            if isinstance(source, str) and not (knowledge_root / source).exists():
                problems.append(f"{article_path.name}: missing source file {source}")

        for link in extract_knowledge_links(body):
            if link not in known_slugs:
                problems.append(f"{article_path.name}: broken knowledge link [[{link}]]")

    if daily_dir.exists():
        state = load_state(state_path)
        compiled_hashes = state.get("compiled_hashes", {})
        if not compiled_hashes:
            return problems
        for log_path in sorted(daily_dir.glob("*.md")):
            if compiled_hashes.get(log_path.name) != file_hash(log_path):
                problems.append(f"daily/{log_path.name}: not compiled into knowledge")

    return problems
