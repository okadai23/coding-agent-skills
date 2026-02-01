from __future__ import annotations

from skillkit.report import Action, Diagnostic, Report


def test_report_to_dict_includes_fields() -> None:
    """Report serialization should include primary fields."""
    report = Report(
        ok=True,
        summary="ok",
        actions=[Action(cmd="git status", cwd=".", exit_code=0)],
        diagnostics=[Diagnostic(level="info", message="hi")],
        artifacts=["go"],
    )
    payload = report.to_dict()
    assert payload["ok"] is True
    assert payload["summary"] == "ok"
    assert payload["actions"][0]["cmd"] == "git status"
    assert payload["diagnostics"][0]["level"] == "info"
    assert payload["artifacts"] == ["go"]
