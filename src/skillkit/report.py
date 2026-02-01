"""Reporting helpers for skills."""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass, field
from enum import IntEnum
from typing import TYPE_CHECKING


class ExitCode(IntEnum):
    """Standard exit codes for skill scripts."""

    SUCCESS = 0
    UNMET = 2
    PRECONDITION = 3
    ERROR = 4


@dataclass(frozen=True)
class Action:
    """Action executed by a skill."""

    cmd: str
    cwd: str
    exit_code: int
    stdout: str | None = None
    stderr: str | None = None


@dataclass(frozen=True)
class Diagnostic:
    """Diagnostic message for a skill run."""

    level: str
    message: str


@dataclass(frozen=True)
class Report:
    """Normalized report for skill scripts."""

    ok: bool
    summary: str
    actions: list[Action] = field(default_factory=list)
    diagnostics: list[Diagnostic] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        """Convert report to a dictionary for JSON output."""
        return {
            "ok": self.ok,
            "summary": self.summary,
            "actions": [asdict(action) for action in self.actions],
            "diagnostics": [asdict(diag) for diag in self.diagnostics],
            "artifacts": list(self.artifacts),
        }


def emit_report(report: Report, *, json_output: bool) -> None:
    """Emit report to stdout."""
    if json_output:
        sys.stdout.write(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
        sys.stdout.write("\n")
        return
    sys.stdout.write(report.summary)
    sys.stdout.write("\n")


if TYPE_CHECKING:
    from pathlib import Path


def action_from_proc(
    cmd: list[str],
    cwd: Path,
    exit_code: int,
    stdout: str,
    stderr: str,
) -> Action:
    """Create an action from a subprocess result."""
    return Action(
        cmd=" ".join(cmd),
        cwd=str(cwd),
        exit_code=exit_code,
        stdout=stdout,
        stderr=stderr,
    )
