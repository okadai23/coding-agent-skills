#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

AGENT_SKILLS_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MAX_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 500


def validate_skill_name(name: str) -> None:
    """Validate skill name against the Agent Skills open standard (strict subset)."""
    if not (1 <= len(name) <= MAX_NAME_LENGTH):
        msg = "skill name must be 1-64 characters"
        raise ValueError(msg)
    if not AGENT_SKILLS_NAME_RE.match(name):
        msg = (
            "skill name must match ^[a-z0-9]+(?:-[a-z0-9]+)*$ "
            "(lowercase/digits/hyphens)"
        )
        raise ValueError(msg)
    if "--" in name:
        msg = "skill name must not contain consecutive hyphens ('--')"
        raise ValueError(msg)


def single_line(text: str) -> str:
    """Collapse multi-line text into a single line."""
    text = " ".join(text.strip().splitlines()).strip()
    return re.sub(r"\s+", " ", text)


def title_from_name(name: str) -> str:
    """Create a title-cased display string from the skill name."""
    return " ".join(part.capitalize() for part in name.split("-"))


def yaml_escape_single_line(text: str) -> str:
    """Quote YAML scalar content on a single line."""
    cleaned = single_line(text)
    cleaned = cleaned.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{cleaned}"'


@dataclass(frozen=True)
class CreateSkillRequest:
    """Captured inputs for a new skill scaffold."""

    name: str
    description: str
    tier: str
    run_type: str
    out_root: Path
    license_name: str
    author: str | None
    tags: list[str]


def render_skill_md(req: CreateSkillRequest) -> str:
    """Render the SKILL.md template for a new skill."""
    title = title_from_name(req.name)

    frontmatter_lines = [
        "---",
        f"name: {req.name}",
        f"description: {yaml_escape_single_line(req.description)}",
        f"license: {yaml_escape_single_line(req.license_name)}",
        (
            'compatibility: "Requires Python and uv. Scripts follow '
            'docs/script-contract.md."'
        ),
        "metadata:",
        f"  short-description: {yaml_escape_single_line(req.description[:120])}",
    ]
    if req.author:
        frontmatter_lines.append(f"  author: {yaml_escape_single_line(req.author)}")
    if req.tags:
        tags = ", ".join(req.tags)
        frontmatter_lines.append(f"  tags: [{tags}]")
    frontmatter_lines.append("---")

    body_lines: list[str] = [
        f"# {title}",
        "",
        "## Overview",
        "- TODO: 1-2 sentencesで、このスキルが何をするか(何を助けるか)を書く。",
        "",
        "## When to use",
        (
            "- TODO: ユーザーの依頼文に現れる具体キーワード/状況"
            '(例: "build", "CI fails", "go test" など)を書く。'
        ),
        "",
        "## Workflow",
        "1. TODO: 前提確認(リポジトリ種別、言語、ビルドツールの特定)",
        "2. TODO: 実行(dry-run → apply の順、ログの提示)",
        "3. TODO: 検証(テスト/フォーマット/リンター)",
        "4. TODO: 変更がある場合は差分と理由をまとめる",
        "",
    ]

    if req.run_type == "script":
        body_lines += [
            "## Scripts",
            "This skill is script-backed.",
            "",
            "- Scripts live in `./scripts/`.",
            (
                "- Scripts MUST follow `docs/script-contract.md` "
                "(JSON output option, dry-run by default, etc.)."
            ),
            "",
            "### Quick start",
            "From the repository root (recommended):",
            "",
            "```bash",
            "uv run python <PATH_TO_SKILL_DIR>/scripts/run.py --help",
            "```",
            "",
            (
                "Note: Codex injects the skill file path into context, "
                "so you can locate `<PATH_TO_SKILL_DIR>` reliably."
            ),
            "",
        ]
    else:
        body_lines += [
            "## Notes",
            (
                "- This is an instruction-only skill. Prefer adding scripts "
                "only when you need determinism or tool orchestration."
            ),
            "",
        ]

    body_lines += [
        "## Examples",
        "- TODO: 入力例(ユーザーが言いそうな依頼)",
        "- TODO: 出力例(どういう結果/差分/ログになるべきか)",
        "",
    ]

    return "\n".join([*frontmatter_lines, "", *body_lines])


def render_script_stub(req: CreateSkillRequest) -> str:
    """Render a script stub that follows the script contract."""
    return f"""#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass
class Result:
    ok: bool
    summary: str
    changed: bool
    actions: list[dict[str, Any]]
    artifacts: list[dict[str, str]]
    warnings: list[str]
    errors: list[dict[str, str]]
    metadata: dict[str, Any]


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="{req.name}:run",
        description="Script entrypoint for the '{req.name}' skill.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit exactly one JSON object to stdout.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually modify files (default: dry-run).",
    )
    parser.add_argument(
        "--cwd",
        default=".",
        help="Working directory for relative paths.",
    )
    parser.add_argument("--verbose", action="store_true", help="More logs to stderr.")
    return parser.parse_args(argv)


def log(message: str) -> None:
    print(message, file=sys.stderr)


def main(argv: list[str]) -> int:
    args = parse_args(argv)

    cwd = Path(args.cwd).resolve()
    if not cwd.exists():
        log(f"❌ precondition failed: --cwd does not exist: {{cwd}}")
        res = Result(
            ok=False,
            summary="precondition failed: cwd does not exist",
            changed=False,
            actions=[],
            artifacts=[],
            warnings=[],
            errors=[{{"message": "cwd does not exist", "code": "cwd_missing"}}],
            metadata={{"skill": "{req.name}"}},
        )
        if args.json:
            print(json.dumps(asdict(res), ensure_ascii=False))
        return 3

    actions: list[dict[str, Any]] = []
    if not args.apply:
        actions.append({{"kind": "info", "detail": "dry-run: no changes will be made"}})

    res = Result(
        ok=True,
        summary="TODO: implement skill script",
        changed=bool(args.apply),
        actions=actions,
        artifacts=[],
        warnings=[],
        errors=[],
        metadata={{"skill": "{req.name}", "cwd": str(cwd)}},
    )

    if args.json:
        print(json.dumps(asdict(res), ensure_ascii=False))
    else:
        print(res.summary)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
"""


def write_text(path: Path, content: str, executable: bool = False) -> None:
    """Write a file to disk and optionally set executable bits."""
    path.write_text(content, encoding="utf-8")
    if executable:
        try:
            mode = path.stat().st_mode
            path.chmod(mode | 0o111)
        except OSError:
            pass


def parse_tags(raw: str | None) -> list[str]:
    """Parse comma-separated tags."""
    if not raw:
        return []
    items = [item.strip() for item in raw.split(",")]
    return [item for item in items if item]


def interactive_missing(value: str | None, prompt: str) -> str:
    """Prompt for a value if missing."""
    if value and value.strip():
        return value.strip()
    return input(prompt).strip()


def log(message: str) -> None:
    """Write a message to stderr."""
    sys.stderr.write(f"{message}\n")


def resolve_inputs(ns: argparse.Namespace) -> tuple[str, str]:
    """Resolve name and description, prompting when allowed."""
    name = ns.name
    desc = ns.description
    if not ns.yes:
        name = interactive_missing(name, "Skill name (e.g. build-go): ")
        desc = interactive_missing(desc, "Description (what it does + when to use): ")
    if not name or not desc:
        msg = "❌ name and description are required. Use --yes only with both provided."
        raise ValueError(msg)
    return name, desc


def normalize_description(desc: str) -> str:
    """Validate and normalize the description."""
    normalized = single_line(desc)
    if not normalized:
        msg = "❌ description must be non-empty"
        raise ValueError(msg)
    if len(normalized) > MAX_DESCRIPTION_LENGTH:
        msg = "❌ description too long (>500 chars). Make it more specific and shorter."
        raise ValueError(msg)
    return normalized


def build_request(ns: argparse.Namespace, name: str, desc: str) -> CreateSkillRequest:
    """Build a CreateSkillRequest from CLI options."""
    tags = parse_tags(ns.tags)
    out_root = Path(ns.out_root)
    return CreateSkillRequest(
        name=name,
        description=desc,
        tier=ns.tier,
        run_type=ns.run_type,
        out_root=out_root,
        license_name=ns.license_name,
        author=ns.author,
        tags=tags,
    )


def ensure_output_dir(req: CreateSkillRequest) -> Path:
    """Compute and validate the skill output directory."""
    skill_dir = req.out_root / req.tier / req.name
    if skill_dir.exists():
        msg = f"❌ skill directory already exists: {skill_dir}"
        raise FileExistsError(msg)
    return skill_dir


def create_scaffold(skill_dir: Path, req: CreateSkillRequest) -> None:
    """Write scaffold files to disk."""
    (skill_dir / "references").mkdir(parents=True, exist_ok=False)
    (skill_dir / "assets").mkdir(parents=True, exist_ok=False)
    if req.run_type == "script":
        (skill_dir / "scripts").mkdir(parents=True, exist_ok=False)

    write_text(skill_dir / "SKILL.md", render_skill_md(req))
    write_text(
        skill_dir / "LICENSE.txt",
        "TODO: Add license text or reference your repository license.\n",
    )
    write_text(
        skill_dir / "references" / "README.md",
        "# References\n\nTODO: Add reference docs for this skill.\n",
    )
    write_text(
        skill_dir / "assets" / "README.md",
        (
            "# Assets\n\n"
            "TODO: Add templates or assets (not loaded into context by default).\n"
        ),
    )

    if req.run_type == "script":
        write_text(
            skill_dir / "scripts" / "run.py",
            render_script_stub(req),
            executable=True,
        )


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="Create a new skill scaffold (repo conventions + script contract).",
    )
    parser.add_argument(
        "name",
        nargs="?",
        help="Skill name (lowercase letters/digits/hyphens, 1-64 chars)",
    )
    parser.add_argument(
        "--description",
        help="One-line description: what it does AND when to use it",
    )
    parser.add_argument(
        "--tier",
        default=".experimental",
        choices=[".experimental", ".curated", ".system"],
    )
    parser.add_argument(
        "--out-root",
        default="skills",
        help="Root folder that contains tier folders (default: skills)",
    )
    parser.add_argument(
        "--run-type",
        default="instruction",
        choices=["instruction", "script"],
    )
    parser.add_argument(
        "--license",
        dest="license_name",
        default="MIT (TODO: confirm)",
        help="License string for frontmatter",
    )
    parser.add_argument("--author", default=None)
    parser.add_argument(
        "--tags",
        default=None,
        help="Comma-separated tags, e.g. build,git,go",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Non-interactive: fail if required fields are missing",
    )
    ns = parser.parse_args(argv)

    try:
        name, desc = resolve_inputs(ns)
        validate_skill_name(name)
        desc = normalize_description(desc)
        req = build_request(ns, name, desc)
        skill_dir = ensure_output_dir(req)
        create_scaffold(skill_dir, req)
    except ValueError as exc:
        log(str(exc))
        return 2
    except FileExistsError as exc:
        log(str(exc))
        return 3

    log(f"✅ Created skill scaffold: {skill_dir}")
    log("Next steps:")
    log(f"1) Edit {skill_dir / 'SKILL.md'} (fill TODOs, refine triggers/examples)")
    if req.run_type == "script":
        script_path = skill_dir / "scripts" / "run.py"
        log(f"2) Implement {script_path}")
        log("   following docs/script-contract.md")
    log("3) Run your lint/test workflow (ruff, etc.)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
