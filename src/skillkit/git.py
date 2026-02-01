"""Git helpers."""

from __future__ import annotations

from pathlib import Path

from skillkit.proc import run


def git_root(cwd: Path) -> Path | None:
    """Return the git repository root or None."""
    result = run(["git", "rev-parse", "--show-toplevel"], cwd=cwd, timeout=10)
    if result.exit_code != 0:
        return None
    return Path(result.stdout.strip())


def is_dirty(cwd: Path) -> bool:
    """Return True if git working tree has changes."""
    result = run(["git", "status", "--porcelain"], cwd=cwd, timeout=10)
    return result.exit_code == 0 and result.stdout.strip() != ""


def current_branch(cwd: Path) -> str | None:
    """Return current branch name or None."""
    result = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=cwd, timeout=10)
    if result.exit_code != 0:
        return None
    return result.stdout.strip()
