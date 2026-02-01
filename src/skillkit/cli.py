"""CLI helpers for skill scripts."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ScriptOptions:
    """Normalized script options."""

    cwd: Path
    json: bool
    apply: bool
    timeout: int

    @property
    def check(self) -> bool:
        """Return True when running in check-only mode."""
        return not self.apply


def parse_script_args(argv: list[str] | None = None) -> ScriptOptions:
    """Parse common skill script arguments."""
    parser = argparse.ArgumentParser(description="Skill script runner")
    parser.add_argument("--cwd", type=Path, default=Path())
    parser.add_argument("--json", action="store_true")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", default=True)
    mode.add_argument("--apply", action="store_true")
    parser.add_argument("--timeout", type=int, default=60)
    args = parser.parse_args(argv)

    return ScriptOptions(
        cwd=args.cwd,
        json=args.json,
        apply=args.apply,
        timeout=args.timeout,
    )
