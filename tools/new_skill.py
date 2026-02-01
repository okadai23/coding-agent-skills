"""Create a new skill scaffold."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MAX_NAME_LENGTH = 64


def validate_name(name: str) -> None:
    """Validate skill name against constraints."""
    if len(name) > MAX_NAME_LENGTH:
        msg = "name must be <= 64 characters"
        raise ValueError(msg)
    if not NAME_RE.match(name):
        msg = "name must be lowercase alnum and hyphens, no leading/trailing hyphen"
        raise ValueError(msg)


def build_skill_md(name: str, description: str, compatibility: str | None) -> str:
    """Build a SKILL.md template."""
    compatibility_line = ""
    if compatibility:
        compatibility_line = f"compatibility: {compatibility}\n"
    return (
        "---\n"
        f"name: {name}\n"
        f"description: {description}\n"
        f"{compatibility_line}"
        "---\n\n"
        f"# {name}\n\n"
        "## What this skill does\n"
        "- TODO: describe behavior\n\n"
        "## Scripts\n"
        "- Run: `uv run python scripts/run.py --cwd . --json --check`\n"
        "- Apply: `uv run python scripts/run.py --cwd . --json --apply`\n\n"
        "## Troubleshooting\n"
        "See [references/REFERENCE.md](references/REFERENCE.md).\n"
    )


def build_run_py() -> str:
    """Return a skeleton run.py."""
    return (
        "from __future__ import annotations\n\n"
        "from skillkit import ExitCode, Report, emit_report, parse_script_args\n\n\n"
        "def main() -> int:\n"
        "    options = parse_script_args()\n"
        '    report = Report(ok=True, summary="TODO: implement")\n'
        "    emit_report(report, json_output=options.json)\n"
        "    return int(ExitCode.SUCCESS)\n\n\n"
        'if __name__ == "__main__":\n'
        "    raise SystemExit(main())\n"
    )


def build_reference_md() -> str:
    """Return a skeleton reference doc."""
    return "# Reference\n\nTODO: detailed usage and troubleshooting.\n"


def write_scaffold(
    base_dir: Path,
    name: str,
    description: str,
    compatibility: str | None,
) -> None:
    """Write scaffold files to disk."""
    from skillkit.fs import atomic_write

    scripts_dir = base_dir / "scripts"
    references_dir = base_dir / "references"

    scripts_dir.mkdir(parents=True, exist_ok=True)
    references_dir.mkdir(parents=True, exist_ok=True)

    atomic_write(
        base_dir / "SKILL.md",
        build_skill_md(name, description, compatibility),
    )
    atomic_write(scripts_dir / "run.py", build_run_py())
    atomic_write(references_dir / "REFERENCE.md", build_reference_md())


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(description="Create a new skill scaffold")
    parser.add_argument("--name", required=True)
    parser.add_argument("--description", required=True)
    parser.add_argument("--compatibility")
    parser.add_argument(
        "--tier",
        choices=["curated", "experimental", "system"],
        default="experimental",
    )
    args = parser.parse_args(argv)

    validate_name(args.name)

    base_dir = Path("skills") / f".{args.tier}" / args.name
    if base_dir.exists():
        msg = f"{base_dir} already exists"
        raise SystemExit(msg)

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

    write_scaffold(base_dir, args.name, args.description, args.compatibility)

    sys.stdout.write(f"Created {base_dir}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
