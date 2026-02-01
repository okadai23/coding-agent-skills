from __future__ import annotations

from pathlib import Path

from skillkit.cli import parse_script_args


def test_parse_script_args_defaults() -> None:
    """Default args should map to check mode and cwd."""
    options = parse_script_args([])
    assert options.cwd == Path()
    assert options.json is False
    assert options.apply is False
    assert options.check is True
    assert options.timeout == 60


def test_parse_script_args_apply() -> None:
    """Apply mode should flip check and parse arguments."""
    options = parse_script_args(
        ["--apply", "--cwd", "fixtures/go-simple", "--json", "--timeout", "5"],
    )
    assert options.apply is True
    assert options.check is False
    assert options.json is True
    assert options.timeout == 5
