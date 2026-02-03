from __future__ import annotations

from typing import TYPE_CHECKING

from tools.generate_skill_tests import main

if TYPE_CHECKING:
    from pathlib import Path


def test_generate_skill_tests_creates_file(tmp_path: Path) -> None:
    """Script-backed skills should get a pytest skeleton."""
    skills_root = tmp_path / "skills"
    skill_dir = skills_root / ".experimental" / "build-go"
    (skill_dir / "scripts").mkdir(parents=True)
    (skill_dir / "scripts" / "run.py").write_text(
        "#!/usr/bin/env python3\n",
        encoding="utf-8",
    )
    (skill_dir / "SKILL.md").write_text(
        "---\nname: build-go\ndescription: Build Go projects\n---\n",
        encoding="utf-8",
    )

    tests_dir = tmp_path / "tests" / "skills"
    assert main(["--skills-root", str(skills_root), "--tests-dir", str(tests_dir)]) == 0

    test_file = tests_dir / "test_build_go.py"
    assert test_file.exists()
