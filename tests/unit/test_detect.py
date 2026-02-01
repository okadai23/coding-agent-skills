from __future__ import annotations

from pathlib import Path

from skillkit.detect import detect_build_system


def test_detect_build_system_go_fixture() -> None:
    """Detect Go markers in fixture."""
    fixture = Path("fixtures/go-simple")
    assert "go" in detect_build_system(fixture)


def test_detect_build_system_node_fixture() -> None:
    """Detect Node markers in fixture."""
    fixture = Path("fixtures/node-simple")
    assert "node" in detect_build_system(fixture)
