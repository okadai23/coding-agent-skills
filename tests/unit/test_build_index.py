from __future__ import annotations

from typing import TYPE_CHECKING

from tools.build_index import build_index

if TYPE_CHECKING:
    from pathlib import Path


def test_build_index_collects_skill(tmp_path: Path) -> None:
    """Index builder should collect skill metadata."""
    skill_dir = tmp_path / ".curated" / "git-status"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: git-status\ndescription: Git status helper\n---\n",
        encoding="utf-8",
    )
    entries = build_index(tmp_path)
    assert len(entries) == 1
    assert entries[0].name == "git-status"
    assert entries[0].tier == "curated"
