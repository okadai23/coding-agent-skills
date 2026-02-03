"""Build skill index metadata."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

import yaml

FRONT_MATTER_SPLIT = 3


@dataclass(frozen=True)
class SkillEntry:
    """Serializable entry for skill index."""

    name: str
    description: str
    path: str
    tier: str


def load_meta(skill_dir: Path) -> SkillEntry:
    """Load metadata for a skill."""
    content = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    parts = content.split("---", 2)
    if len(parts) < FRONT_MATTER_SPLIT:
        msg = f"{skill_dir} invalid front matter"
        raise ValueError(msg)
    data = yaml.safe_load(parts[1])
    if not isinstance(data, dict):
        msg = f"{skill_dir} invalid front matter"
        raise TypeError(msg)
    name = data.get("name")
    description = data.get("description")
    if not isinstance(name, str) or not isinstance(description, str):
        msg = f"{skill_dir} missing name/description"
        raise TypeError(msg)
    tier = skill_dir.parents[0].name.lstrip(".")
    return SkillEntry(
        name=name,
        description=description,
        path=str(skill_dir.as_posix()),
        tier=tier,
    )


def build_index(root: Path) -> list[SkillEntry]:
    """Collect all skill entries."""
    entries = [load_meta(skill_path.parent) for skill_path in root.rglob("SKILL.md")]
    return sorted(entries, key=lambda entry: (entry.tier, entry.name))


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(description="Build skill index")
    parser.add_argument("--root", type=Path, default=Path("skills"))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("skills/index.json"),
    )
    args = parser.parse_args(argv)

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

    from skillkit.fs import atomic_write

    entries = build_index(args.root)
    payload = json.dumps(
        [asdict(entry) for entry in entries],
        ensure_ascii=False,
        indent=2,
    )
    atomic_write(args.output, payload + "\n")
    sys.stdout.write(f"Wrote {args.output}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
