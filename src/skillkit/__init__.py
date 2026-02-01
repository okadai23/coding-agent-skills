"""Shared utilities for Agent Skills scripts."""

from skillkit.cli import ScriptOptions, parse_script_args
from skillkit.detect import detect_build_system
from skillkit.fs import atomic_write
from skillkit.git import current_branch, git_root, is_dirty
from skillkit.proc import ProcResult, run
from skillkit.report import Action, Diagnostic, ExitCode, Report, emit_report

__all__ = [
    "Action",
    "Diagnostic",
    "ExitCode",
    "ProcResult",
    "Report",
    "ScriptOptions",
    "atomic_write",
    "current_branch",
    "detect_build_system",
    "emit_report",
    "git_root",
    "is_dirty",
    "parse_script_args",
    "run",
]
