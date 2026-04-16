"""Tests for the arch-init bootstrap wrapper."""

from __future__ import annotations

import subprocess
from pathlib import Path


def test_arch_init_dry_run_has_no_side_effects(tmp_path):
    """Dry-run should show planned bootstrap work without writing files."""
    repo_root = Path(__file__).resolve().parents[1]
    target_repo = tmp_path / "consumer-repo"
    target_repo.mkdir()

    completed = subprocess.run(
        [
            str(repo_root / "scripts" / "arch-init"),
            "--dry-run",
            "--repo",
            "hasandem/agent-arch",
            "--arch-dir",
            str(tmp_path / "arch-cache"),
        ],
        cwd=target_repo,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0
    assert "Would install bootstrap skill" in completed.stdout
    assert "Method surface materialized" in completed.stdout
    assert "ARCH_DIR ready" in completed.stdout
    assert not (target_repo / ".agents").exists()
    assert not (target_repo / ".github").exists()
