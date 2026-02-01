from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    """Run git status checks and emit a report."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "src"))
    from skillkit import (
        ExitCode,
        Report,
        emit_report,
        git_root,
        is_dirty,
        parse_script_args,
    )
    from skillkit.proc import run
    from skillkit.report import Action, Diagnostic

    options = parse_script_args()
    root = git_root(options.cwd)
    if root is None:
        report = Report(
            ok=False,
            summary="git repository not found",
            diagnostics=[Diagnostic(level="error", message="not a git repository")],
        )
        emit_report(report, json_output=options.json)
        return int(ExitCode.PRECONDITION)

    status = run(["git", "status", "--short"], cwd=root, timeout=options.timeout)
    diff = run(["git", "diff", "--stat"], cwd=root, timeout=options.timeout)
    actions = [
        Action(
            cmd="git status --short",
            cwd=str(root),
            exit_code=status.exit_code,
            stdout=status.stdout,
            stderr=status.stderr,
        ),
        Action(
            cmd="git diff --stat",
            cwd=str(root),
            exit_code=diff.exit_code,
            stdout=diff.stdout,
            stderr=diff.stderr,
        ),
    ]

    dirty = is_dirty(root)
    summary = "working tree clean" if not dirty else "working tree has changes"
    report = Report(
        ok=not dirty,
        summary=summary,
        actions=actions,
    )
    emit_report(report, json_output=options.json)
    return int(ExitCode.SUCCESS if not dirty else ExitCode.UNMET)


if __name__ == "__main__":
    raise SystemExit(main())
