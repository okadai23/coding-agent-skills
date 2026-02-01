"""Validate skill metadata and structure."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

from tools.new_skill import NAME_RE

FRONT_MATTER_SPLIT = 3


@dataclass(frozen=True)
class SkillMeta:
    """Parsed skill metadata."""

    name: str
    description: str


def load_front_matter(skill_path: Path) -> SkillMeta:
    """Load YAML front matter from SKILL.md."""
    skill_file = skill_path / "SKILL.md"
    content = skill_file.read_text(encoding="utf-8")
    if not content.startswith("---"):
        msg = f"{skill_file} missing front matter"
        raise ValueError(msg)
    parts = content.split("---", 2)
    if len(parts) < FRONT_MATTER_SPLIT:
        msg = f"{skill_file} front matter not closed"
        raise ValueError(msg)
    data = yaml.safe_load(parts[1])
    if not isinstance(data, dict):
        msg = f"{skill_file} front matter invalid"
        raise TypeError(msg)
    name = data.get("name")
    description = data.get("description")
    if not isinstance(name, str) or not isinstance(description, str):
        msg = f"{skill_file} requires name and description"
        raise TypeError(msg)
    return SkillMeta(name=name, description=description)


@dataclass(frozen=True)
class Diagnostic:
    """Diagnostic message for validation."""

    level: str
    message: str


def validate_skill_dir(skill_dir: Path) -> list[Diagnostic]:
    """Validate a single skill directory."""
    diagnostics: list[Diagnostic] = []
    try:
        meta = load_front_matter(skill_dir)
    except ValueError as exc:
        diagnostics.append(Diagnostic(level="error", message=str(exc)))
        return diagnostics

    if meta.name != skill_dir.name:
        diagnostics.append(
            Diagnostic(
                level="error",
                message=f"{skill_dir} name mismatch: {meta.name}",
            ),
        )
    if not NAME_RE.match(meta.name):
        diagnostics.append(
            Diagnostic(
                level="error",
                message=f"{skill_dir} invalid name: {meta.name}",
            ),
        )
    return diagnostics


def iter_skill_dirs(root: Path) -> list[Path]:
    """Collect all skill directories that include SKILL.md."""
    return [path.parent for path in root.rglob("SKILL.md")]


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(description="Validate skill directories")
    parser.add_argument("--root", type=Path, default=Path("skills"))
    args = parser.parse_args(argv)

    diagnostics: list[Diagnostic] = []
    for skill_dir in iter_skill_dirs(args.root):
        diagnostics.extend(validate_skill_dir(skill_dir))

    if diagnostics:
        for diag in diagnostics:
            sys.stdout.write(f"[{diag.level}] {diag.message}\n")
        return 1
    sys.stdout.write("All skills valid\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
