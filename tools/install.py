"""Install curated skills into agent skill directories."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


def install_skill(source: Path, destination: Path, mode: str) -> None:
    """Install a skill by symlink or copy."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() or destination.is_symlink():
        if destination.is_dir() and not destination.is_symlink():
            shutil.rmtree(destination)
        else:
            destination.unlink()
    if mode == "symlink":
        destination.symlink_to(source, target_is_directory=True)
    else:
        shutil.copytree(source, destination)


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(description="Install curated skills")
    parser.add_argument(
        "--mode",
        choices=["symlink", "copy"],
        default="symlink",
    )
    parser.add_argument(
        "--codex-dir",
        type=Path,
        default=Path.home() / ".codex" / "skills",
    )
    parser.add_argument(
        "--claude-dir",
        type=Path,
        default=Path.home() / ".claude" / "skills",
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=Path("skills/.curated"),
    )
    args = parser.parse_args(argv)

    if not args.source.exists():
        sys.stdout.write(f"Source directory not found: {args.source}\n")
        return 1

    skills = [path for path in args.source.iterdir() if path.is_dir()]
    for skill in skills:
        install_skill(skill, args.codex_dir / skill.name, args.mode)
        install_skill(skill, args.claude_dir / skill.name, args.mode)

    sys.stdout.write(
        f"Installed {len(skills)} skills to {args.codex_dir} and {args.claude_dir}\n",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
