from __future__ import annotations

from pathlib import Path

import pytest

from tools.new_skill import (
    CreateSkillRequest,
    parse_tags,
    render_skill_md,
    validate_skill_name,
)


def test_validate_name_accepts_valid() -> None:
    """Valid names should pass validation."""
    validate_skill_name("build-go")


@pytest.mark.parametrize("name", ["Build-Go", "build_go", "-bad", "bad-", "bad--name"])
def test_validate_name_rejects_invalid(name: str) -> None:
    """Invalid names should raise ValueError."""
    with pytest.raises(ValueError, match="skill name must"):
        validate_skill_name(name)


def test_render_skill_md_includes_front_matter() -> None:
    """Template should include required front matter fields."""
    req = CreateSkillRequest(
        name="build-go",
        description="Build Go projects",
        tier=".experimental",
        run_type="instruction",
        out_root=Path("skills"),
        license_name="MIT",
        author=None,
        tags=[],
        make_tests=False,
    )
    content = render_skill_md(req)
    assert "name: build-go" in content
    assert 'description: "Build Go projects"' in content
    assert "license:" in content


def test_parse_tags_splits_and_strips() -> None:
    """Tags should be parsed from comma-separated input."""
    assert parse_tags("build, git , go") == ["build", "git", "go"]
    assert parse_tags(None) == []
