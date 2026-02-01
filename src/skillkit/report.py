"""Reporting helpers for skills."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from enum import IntEnum
from typing import TYPE_CHECKING, TypedDict


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


def _empty_actions() -> list[Action]:
    """Return empty action list."""
    return []


def _empty_diagnostics() -> list[Diagnostic]:
    """Return empty diagnostic list."""
    return []


def _empty_artifacts() -> list[str]:
    """Return empty artifacts list."""
    return []


@dataclass(frozen=True)
class Report:
    """Normalized report for skill scripts."""

    ok: bool
    summary: str
    actions: list[Action] = field(default_factory=_empty_actions)
    diagnostics: list[Diagnostic] = field(default_factory=_empty_diagnostics)
    artifacts: list[str] = field(default_factory=_empty_artifacts)

    def to_dict(self) -> ReportPayload:
        """Convert report to a dictionary for JSON output."""
        return {
            "ok": self.ok,
            "summary": self.summary,
            "actions": [_serialize_action(action) for action in self.actions],
            "diagnostics": [_serialize_diagnostic(diag) for diag in self.diagnostics],
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


class ActionPayload(TypedDict):
    """Serialized Action payload."""

    cmd: str
    cwd: str
    exit_code: int
    stdout: str | None
    stderr: str | None


class DiagnosticPayload(TypedDict):
    """Serialized Diagnostic payload."""

    level: str
    message: str


class ReportPayload(TypedDict):
    """Serialized Report payload."""

    ok: bool
    summary: str
    actions: list[ActionPayload]
    diagnostics: list[DiagnosticPayload]
    artifacts: list[str]


def _serialize_action(action: Action) -> ActionPayload:
    """Serialize an Action to a payload."""
    return ActionPayload(
        cmd=action.cmd,
        cwd=action.cwd,
        exit_code=action.exit_code,
        stdout=action.stdout,
        stderr=action.stderr,
    )


def _serialize_diagnostic(diagnostic: Diagnostic) -> DiagnosticPayload:
    """Serialize a Diagnostic to a payload."""
    return DiagnosticPayload(
        level=diagnostic.level,
        message=diagnostic.message,
    )


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
