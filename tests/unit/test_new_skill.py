from __future__ import annotations

import pytest

from tools.new_skill import build_skill_md, validate_name


def test_validate_name_accepts_valid() -> None:
    """Valid names should pass validation."""
    validate_name("build-go")


@pytest.mark.parametrize("name", ["Build-Go", "build_go", "-bad", "bad-", "bad--name"])
def test_validate_name_rejects_invalid(name: str) -> None:
    """Invalid names should raise ValueError."""
    with pytest.raises(ValueError, match="name must"):
        validate_name(name)


def test_build_skill_md_includes_front_matter() -> None:
    """Template should include required front matter fields."""
    content = build_skill_md("build-go", "Build Go projects", None)
    assert "name: build-go" in content
    assert "description: Build Go projects" in content
