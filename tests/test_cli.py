"""Tests for the arch-knowledge CLI."""

from __future__ import annotations

from unittest.mock import patch

from arch_knowledge.cli import main


def test_cli_flush_reads_stdin(capsys):
    """The flush subcommand should read from stdin by default."""
    with patch("sys.stdin.read", return_value="hello from stdin"), patch(
        "arch_knowledge.cli.flush",
        return_value="FLUSH_OK",
    ) as flush_mock:
        exit_code = main(["flush"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "FLUSH_OK" in captured.out
    flush_mock.assert_called_once_with("hello from stdin", session_id="")


def test_cli_lint_returns_non_zero_on_problems(capsys):
    """Lint should return exit code 1 when problems are found."""
    with patch("arch_knowledge.cli.find_knowledge_root") as root_mock, patch(
        "arch_knowledge.cli.lint_knowledge",
        return_value=["problem one", "problem two"],
    ):
        root_mock.return_value = object()
        exit_code = main(["lint"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "problem one" in captured.out


def test_cli_doctor_returns_zero_when_clean(capsys):
    """Doctor should return exit code 0 when no problems are found."""
    with patch("arch_knowledge.cli.doctor_knowledge", return_value=[]):
        exit_code = main(["doctor"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "doctor checks passed" in captured.out
