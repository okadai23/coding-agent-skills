"""Subprocess helpers."""

from __future__ import annotations

from dataclasses import dataclass
from subprocess import CompletedProcess, run as run_subprocess
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


@dataclass(frozen=True)
class ProcResult:
    """Result of a subprocess execution."""

    cmd: list[str]
    cwd: Path
    exit_code: int
    stdout: str
    stderr: str


def run(
    cmd: list[str],
    *,
    cwd: Path,
    timeout: int,
    env: dict[str, str] | None = None,
) -> ProcResult:
    """Run an external command and capture output."""
    if not cmd or not all(isinstance(part, str) and part for part in cmd):
        msg = "cmd must be a non-empty list of strings"
        raise ValueError(msg)

    # Bandit S603: commands are list-args validated above and executed without shell.
    completed: CompletedProcess[str] = run_subprocess(  # noqa: S603
        cmd,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )

    return ProcResult(
        cmd=cmd,
        cwd=cwd,
        exit_code=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )
