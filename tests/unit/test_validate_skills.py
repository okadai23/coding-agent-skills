from __future__ import annotations

from typing import TYPE_CHECKING

from tools.validate_skills import validate_skill_dir

if TYPE_CHECKING:
    from pathlib import Path


def test_validate_skill_dir_success(tmp_path: Path) -> None:
    """Valid SKILL.md should pass validation."""
    skill_dir = tmp_path / "build-go"
    skill_dir.mkdir()
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(
        "---\nname: build-go\ndescription: Build Go projects\n---\n",
        encoding="utf-8",
    )
    diagnostics = validate_skill_dir(skill_dir)
    assert diagnostics == []


def test_validate_skill_dir_name_mismatch(tmp_path: Path) -> None:
    """Name mismatch should be reported as diagnostics."""
    skill_dir = tmp_path / "build-go"
    skill_dir.mkdir()
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(
        "---\nname: build-node\ndescription: Build Node projects\n---\n",
        encoding="utf-8",
    )
    diagnostics = validate_skill_dir(skill_dir)
    assert diagnostics
