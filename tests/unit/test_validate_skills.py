from __future__ import annotations

import json
from typing import TYPE_CHECKING

from tools.validate_skills import main

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


def test_validate_skills_ok(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Matching name/description should produce an OK summary."""
    skills_root = tmp_path / "skills"
    skill_dir = skills_root / ".experimental" / "build-go"
    (skill_dir / "references").mkdir(parents=True)
    (skill_dir / "references" / "README.md").write_text(
        "# References\n",
        encoding="utf-8",
    )
    (skill_dir / "SKILL.md").write_text(
        "---\nname: build-go\ndescription: Build Go projects\n---\n",
        encoding="utf-8",
    )

    assert main(["--skills-root", str(skills_root), "--json"]) == 0
    output = capsys.readouterr().out
    payload = json.loads(output)
    assert payload["summary"]["errors"] == 0
    assert payload["summary"]["ok"] is True


def test_validate_skills_name_mismatch(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Name mismatch should be reported as an error."""
    skills_root = tmp_path / "skills"
    skill_dir = skills_root / ".experimental" / "build-go"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: build-node\ndescription: Build Node projects\n---\n",
        encoding="utf-8",
    )

    assert main(["--skills-root", str(skills_root), "--json"]) == 1
    output = capsys.readouterr().out
    payload = json.loads(output)
    assert payload["summary"]["errors"] >= 1
