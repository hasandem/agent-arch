"""Tests for arch-knowledge doctor."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch

from arch_knowledge.doctor import doctor_knowledge


def test_doctor_reports_remediation_commands(tmp_path, monkeypatch):
    """Doctor should return concrete remediation commands for missing setup."""
    repo_root = tmp_path / "repo"
    (repo_root / ".git").mkdir(parents=True)
    (repo_root / "scripts").mkdir()
    monkeypatch.chdir(repo_root)
    monkeypatch.delenv("ARCH_LLM_ADAPTER", raising=False)
    monkeypatch.delenv("ARCH_LLM_TOOL_CMD", raising=False)
    monkeypatch.delenv("ARCH_DIR", raising=False)
    monkeypatch.delenv("AGENT_ARCH_SOURCE_REPO", raising=False)
    monkeypatch.setenv("PATH", "/usr/bin")

    problems = doctor_knowledge(start=repo_root)

    assert any('export ARCH_LLM_ADAPTER="$PWD/scripts/arch-llm-adapter.py"' in problem for problem in problems)
    assert any('export ARCH_LLM_TOOL_CMD="python3 scripts/my-company-llm-wrapper.py"' in problem for problem in problems)
    assert any('export PATH="$PATH:$PWD/scripts"' in problem for problem in problems)
    assert any("sh scripts/arch-init --repo hasandem/agent-arch" in problem for problem in problems)


def test_doctor_accepts_valid_setup(tmp_path, monkeypatch):
    """Doctor should accept a fully configured repository."""
    repo_root = tmp_path / "repo"
    (repo_root / ".git").mkdir(parents=True)
    scripts_dir = repo_root / "scripts"
    scripts_dir.mkdir()
    adapter = scripts_dir / "arch-llm-adapter.py"
    adapter.write_text("#!/usr/bin/env python3\nprint('ok')\n", encoding="utf-8")
    adapter.chmod(0o755)

    metadata_dir = repo_root / ".github" / "agent-arch"
    metadata_dir.mkdir(parents=True)
    (metadata_dir / "source.env").write_text("AGENT_ARCH_SOURCE_REPO=hasandem/agent-arch\n", encoding="utf-8")

    arch_dir = tmp_path / "agent-arch-cache"
    (arch_dir / ".git").mkdir(parents=True)

    monkeypatch.chdir(repo_root)
    monkeypatch.setenv("ARCH_LLM_ADAPTER", str(adapter))
    monkeypatch.setenv("ARCH_LLM_TOOL_CMD", "python3 scripts/my-company-llm-wrapper.py")
    monkeypatch.setenv("ARCH_DIR", str(arch_dir))
    monkeypatch.setenv("PATH", f"{scripts_dir}:/usr/bin")

    git_process = Mock(returncode=0, stdout="true\n", stderr="")
    ls_remote_process = Mock(returncode=0, stdout="deadbeef\tHEAD\n", stderr="")

    with patch("arch_knowledge.doctor.subprocess.run", side_effect=[git_process, ls_remote_process]):
        problems = doctor_knowledge(start=repo_root)

    assert problems == []


def test_doctor_rejects_adapter_shell_command(tmp_path, monkeypatch):
    """Doctor should require ARCH_LLM_ADAPTER to be a direct executable path."""
    repo_root = tmp_path / "repo"
    (repo_root / ".git").mkdir(parents=True)
    (repo_root / "scripts").mkdir()
    monkeypatch.chdir(repo_root)
    monkeypatch.setenv("ARCH_LLM_ADAPTER", "python3 scripts/arch-llm-adapter.py")
    monkeypatch.setenv("ARCH_LLM_TOOL_CMD", "python3 scripts/my-company-llm-wrapper.py")
    monkeypatch.setenv("PATH", f"{repo_root / 'scripts'}:/usr/bin")

    problems = doctor_knowledge(start=repo_root)

    assert any("must point directly to an executable file" in problem for problem in problems)


def test_doctor_reports_unreadable_source_metadata(tmp_path, monkeypatch):
    """Doctor should report a remediation command when source metadata cannot be read."""
    repo_root = tmp_path / "repo"
    (repo_root / ".git").mkdir(parents=True)
    (repo_root / "scripts").mkdir()
    metadata_dir = repo_root / ".github" / "agent-arch"
    metadata_dir.mkdir(parents=True)
    source_env = metadata_dir / "source.env"
    source_env.write_text("AGENT_ARCH_SOURCE_REPO=hasandem/agent-arch\n", encoding="utf-8")
    monkeypatch.chdir(repo_root)
    monkeypatch.setenv("PATH", "/usr/bin")

    with patch("pathlib.Path.read_text", side_effect=UnicodeDecodeError("utf-8", b"x", 0, 1, "boom")):
        problems = doctor_knowledge(start=repo_root)

    assert any("Could not read .github/agent-arch/source.env" in problem for problem in problems)
