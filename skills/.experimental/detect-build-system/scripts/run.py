from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    """Detect build system markers and emit a report."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "src"))
    from skillkit import (
        ExitCode,
        Report,
        detect_build_system,
        emit_report,
        parse_script_args,
    )
    from skillkit.report import Diagnostic

    options = parse_script_args()
    detected = detect_build_system(options.cwd)
    if not detected:
        report = Report(
            ok=False,
            summary="no build system detected",
            diagnostics=[
                Diagnostic(level="warning", message="no known build markers found"),
            ],
        )
        emit_report(report, json_output=options.json)
        return int(ExitCode.UNMET)

    report = Report(
        ok=True,
        summary="detected build systems: " + ", ".join(detected),
        artifacts=detected,
    )
    emit_report(report, json_output=options.json)
    return int(ExitCode.SUCCESS)


if __name__ == "__main__":
    raise SystemExit(main())
