"""Deterministic setup checks for arch-knowledge."""

from __future__ import annotations

import os
import shlex
import subprocess
from pathlib import Path

from .config import find_repo_root

DEFAULT_SOURCE_REPO = "hasandem/agent-arch"


def _default_arch_dir() -> Path:
    cache_home = Path(os.environ.get("XDG_CACHE_HOME", str(Path.home() / ".cache")))
    return Path(os.environ.get("ARCH_DIR", cache_home / "agent-arch")).expanduser()


def _load_source_metadata(repo_root: Path) -> dict[str, str]:
    metadata_path = repo_root / ".github" / "agent-arch" / "source.env"
    if not metadata_path.exists():
        return {}

    values: dict[str, str] = {}
    for line in metadata_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def _remediation_adapter() -> str:
    return 'export ARCH_LLM_ADAPTER="$PWD/scripts/arch-llm-adapter.py"'


def _resolve_adapter_path(raw_value: str, repo_root: Path) -> tuple[Path | None, str | None]:
    try:
        parts = shlex.split(raw_value)
    except ValueError:
        return None, "ARCH_LLM_ADAPTER could not be parsed as a path."

    if len(parts) != 1:
        return None, "ARCH_LLM_ADAPTER must point directly to an executable file."

    candidate = Path(parts[0]).expanduser()
    if candidate.is_absolute():
        return candidate, None

    cwd_candidate = (Path.cwd() / candidate).resolve()
    if cwd_candidate.exists():
        return cwd_candidate, None

    return (repo_root / candidate).resolve(), None


def _path_contains(target: Path) -> bool:
    target_resolved = target.resolve()
    for entry in os.environ.get("PATH", "").split(os.pathsep):
        base = Path.cwd() if entry == "" else Path(entry).expanduser()
        try:
            if base.resolve() == target_resolved:
                return True
        except OSError:
            continue
    return False


def doctor_knowledge(start: Path | None = None) -> list[str]:
    """Return deterministic setup problems with concrete remediation commands."""
    repo_root = find_repo_root(start) or (start.resolve() if start else Path.cwd().resolve())
    scripts_dir = repo_root / "scripts"
    metadata = _load_source_metadata(repo_root)
    source_repo = os.environ.get("AGENT_ARCH_SOURCE_REPO", metadata.get("AGENT_ARCH_SOURCE_REPO", "")).strip()
    arch_dir = _default_arch_dir()
    problems: list[str] = []

    adapter_value = os.environ.get("ARCH_LLM_ADAPTER", "").strip()
    if not adapter_value:
        problems.append(
            "ERROR: ARCH_LLM_ADAPTER is not set. "
            f"Run: {_remediation_adapter()}"
        )
    else:
        adapter_path, adapter_error = _resolve_adapter_path(adapter_value, repo_root)
        if adapter_error:
            problems.append(
                f"ERROR: {adapter_error} Run: {_remediation_adapter()}"
            )
        elif adapter_path is None or not adapter_path.is_file() or not os.access(adapter_path, os.X_OK):
            problems.append(
                f"ERROR: ARCH_LLM_ADAPTER points to '{adapter_path}', but that is not an executable file. "
                f"Run: {_remediation_adapter()}"
            )

    if not os.environ.get("ARCH_LLM_TOOL_CMD", "").strip():
        problems.append(
            "ERROR: ARCH_LLM_TOOL_CMD is not set. "
            'Run: export ARCH_LLM_TOOL_CMD="python3 scripts/my-company-llm-wrapper.py"'
        )

    repo_for_clone = source_repo or DEFAULT_SOURCE_REPO
    if not arch_dir.exists():
        problems.append(
            f"ERROR: ARCH_DIR '{arch_dir}' does not exist. "
            f"Run: export ARCH_DIR=\"{arch_dir}\" && git clone --depth 1 "
            f"\"https://github.com/{repo_for_clone}.git\" \"{arch_dir}\""
        )
    else:
        try:
            git_check = subprocess.run(
                ["git", "-C", str(arch_dir), "rev-parse", "--is-inside-work-tree"],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
        except OSError as exc:
            problems.append(
                f"ERROR: Could not run git for ARCH_DIR validation: {exc}. "
                'Run: git --version'
            )
        else:
            if git_check.returncode != 0 or git_check.stdout.strip() != "true":
                problems.append(
                    f"ERROR: ARCH_DIR '{arch_dir}' is not a valid git repository. "
                    f"Run: rm -rf \"{arch_dir}\" && git clone --depth 1 "
                    f"\"https://github.com/{repo_for_clone}.git\" \"{arch_dir}\""
                )

    if not _path_contains(scripts_dir):
        problems.append(
            f"ERROR: PATH does not include '{scripts_dir}'. "
            'Run: export PATH="$PATH:$PWD/scripts"'
        )

    if not source_repo:
        problems.append(
            "ERROR: Could not resolve AGENT_ARCH_SOURCE_REPO from .github/agent-arch/source.env. "
            f"Run: sh scripts/arch-init --repo {DEFAULT_SOURCE_REPO}"
        )
        return problems

    repo_url = f"https://github.com/{source_repo}.git"
    try:
        remote_check = subprocess.run(
            ["git", "ls-remote", repo_url],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except OSError as exc:
        problems.append(
            f"ERROR: Could not run git ls-remote for {repo_url}: {exc}. "
            'Run: git --version'
        )
        return problems

    if remote_check.returncode != 0:
        stderr = remote_check.stderr.strip()
        suffix = f" ({stderr})" if stderr else ""
        problems.append(
            f"ERROR: git ls-remote failed for {repo_url}{suffix}. "
            f"Run: git ls-remote \"{repo_url}\""
        )

    return problems
