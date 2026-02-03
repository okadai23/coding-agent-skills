"""Validate skill metadata, structure, scripts, and tests."""

from __future__ import annotations

import argparse
import importlib
import importlib.util
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Iterable

AGENT_SKILLS_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
EXIT_PRECONDITION = 3
MAX_DESCRIPTION_LENGTH = 500
MAX_NAME_LENGTH = 64


def validate_skill_name(name: str) -> str | None:
    """Validate the skill name against the Agent Skills standard."""
    if not (1 <= len(name) <= MAX_NAME_LENGTH):
        return "skill name must be 1-64 characters"
    if not AGENT_SKILLS_NAME_RE.match(name):
        return (
            "skill name must match ^[a-z0-9]+(?:-[a-z0-9]+)* (lowercase/digits/hyphens)"
        )
    if "--" in name:
        return "skill name must not contain consecutive hyphens ('--')"
    return None


def test_filename_for_skill(name: str) -> str:
    """Return the canonical test filename for a skill."""
    return f"test_{name.replace('-', '_')}.py"


@dataclass(frozen=True)
class Issue:
    """Issue found during validation."""

    level: str
    path: str
    message: str


@dataclass(frozen=True)
class SkillReport:
    """Validation report for a single skill."""

    skill_dir: str
    tier: str
    name: str | None
    description: str | None
    script_backed: bool
    issues: list[Issue]


def extract_frontmatter_text(lines: list[str]) -> tuple[str | None, str | None]:
    """Extract the YAML frontmatter block from SKILL.md lines."""
    if not lines or lines[0].strip() != "---":
        return None, "missing YAML frontmatter start line '---'"

    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        return None, "missing YAML frontmatter end line '---'"

    return "\n".join(lines[1:end_idx]), None


def parse_yaml_frontmatter(
    yaml_text: str,
) -> tuple[str | None, str | None, dict[str, Any] | None, str | None]:
    """Parse YAML frontmatter using PyYAML."""
    yaml_module = importlib.import_module("yaml")
    try:
        data = yaml_module.safe_load(yaml_text) or {}
    except Exception:
        return None, None, None, "frontmatter YAML could not be parsed"
    if not isinstance(data, dict):
        return None, None, None, "frontmatter YAML must be a mapping/object"
    name = data.get("name")
    desc = data.get("description")
    return (
        str(name) if name is not None else None,
        str(desc) if desc is not None else None,
        data,
        None,
    )


def parse_minimal_frontmatter(
    yaml_text: str,
) -> tuple[str | None, str | None, dict[str, Any] | None, str | None]:
    """Fallback parser for name/description without PyYAML."""
    name = None
    desc = None
    for raw in yaml_text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        val = value.strip().strip('"').strip("'")
        if key == "name":
            name = val
        elif key == "description":
            desc = val
    if name is None or desc is None:
        return name, desc, None, "failed to parse frontmatter (install PyYAML)"
    return name, desc, None, None


def parse_frontmatter_block(
    skill_md: Path,
) -> tuple[str | None, str | None, dict[str, Any] | None, str | None]:
    """Parse YAML frontmatter and return name/description with errors."""
    text = skill_md.read_text(encoding="utf-8")
    yaml_text, error = extract_frontmatter_text(text.splitlines())
    if error:
        return None, None, None, error
    if yaml_text is None:
        return None, None, None, "missing YAML frontmatter"
    if importlib.util.find_spec("yaml") is not None:
        return parse_yaml_frontmatter(yaml_text)
    return parse_minimal_frontmatter(yaml_text)


def iter_skill_dirs(skills_root: Path) -> Iterable[Path]:
    """Return skill directories that include SKILL.md."""
    for skill_md in skills_root.rglob("SKILL.md"):
        if "__pycache__" in skill_md.parts:
            continue
        yield skill_md.parent


def detect_tier(skills_root: Path, skill_dir: Path) -> str:
    """Detect the tier from the directory path."""
    rel = skill_dir.relative_to(skills_root)
    return rel.parts[0] if rel.parts else "unknown"


def find_entry_script(skill_dir: Path) -> Path | None:
    """Find the script-backed entry point if it exists."""
    script = skill_dir / "scripts" / "run.py"
    return script if script.exists() else None


def run_entry_script(
    script: Path,
    args: list[str],
    repo_root: Path,
) -> subprocess.CompletedProcess[str]:
    """Run a skill entry script from the repository root."""
    return subprocess.run(  # noqa: S603
        [sys.executable, str(script), *args],
        cwd=str(repo_root),
        text=True,
        capture_output=True,
        env={**os.environ},
        check=False,
    )


def validate_json_stdout(
    proc: subprocess.CompletedProcess[str],
) -> tuple[dict[str, Any] | None, str | None]:
    """Validate stdout from --json runs."""
    out = proc.stdout
    if out.strip() == "":
        return None, "empty stdout in --json mode (must output one JSON object)"
    try:
        obj = json.loads(out)
    except Exception as exc:
        return None, f"stdout is not valid JSON: {exc}"
    if not isinstance(obj, dict):
        return None, "JSON output must be an object"
    for key, typ in [("ok", bool), ("summary", str), ("changed", bool)]:
        if key not in obj:
            return None, f"JSON missing required key: {key}"
        if not isinstance(obj[key], typ):
            return None, f"JSON key {key} must be {typ.__name__}"
    return obj, None


def add_issue(issues: list[Issue], level: str, path: Path, message: str) -> None:
    """Append an issue to the list."""
    issues.append(Issue(level, str(path), message))


def validate_metadata(
    issues: list[Issue],
    skill_md: Path,
    skill_dir: Path,
    seen_names: dict[str, Path],
) -> tuple[str | None, str | None]:
    """Validate YAML frontmatter metadata."""
    name, desc, _raw, fm_err = parse_frontmatter_block(skill_md)
    if fm_err:
        add_issue(issues, "error", skill_md, fm_err)

    dir_name = skill_dir.name
    if name is None:
        add_issue(issues, "error", skill_md, "frontmatter must include 'name'")
    else:
        if name != dir_name:
            add_issue(
                issues,
                "error",
                skill_md,
                f"frontmatter name '{name}' must match directory '{dir_name}'",
            )
        msg = validate_skill_name(name)
        if msg:
            add_issue(issues, "error", skill_md, msg)
        if name in seen_names:
            add_issue(
                issues,
                "error",
                skill_md,
                f"duplicate skill name '{name}' also at {seen_names[name]}",
            )
        else:
            seen_names[name] = skill_dir

    if desc is None:
        add_issue(issues, "error", skill_md, "frontmatter must include 'description'")
    else:
        if desc.strip() == "":
            add_issue(issues, "error", skill_md, "description must be non-empty")
        if "\n" in desc:
            add_issue(
                issues,
                "warning",
                skill_md,
                "description should be single-line for better triggering",
            )
        if len(desc) > MAX_DESCRIPTION_LENGTH:
            add_issue(
                issues,
                "warning",
                skill_md,
                "description is very long (>500 chars); consider shortening",
            )
    return name, desc


def validate_directories(issues: list[Issue], skill_dir: Path) -> None:
    """Validate recommended directories."""
    refs_dir = skill_dir / "references"
    assets_dir = skill_dir / "assets"

    if not refs_dir.exists():
        add_issue(
            issues,
            "warning",
            skill_dir,
            "missing references/ directory (recommended)",
        )
    elif not any(refs_dir.iterdir()):
        add_issue(
            issues,
            "warning",
            refs_dir,
            "references/ is empty (add README.md at least)",
        )

    if assets_dir.exists() and not any(assets_dir.iterdir()):
        add_issue(
            issues,
            "warning",
            assets_dir,
            "assets/ is empty (ok, but usually include README.md)",
        )


def validate_tests(
    issues: list[Issue],
    repo_root: Path,
    tier: str,
    skill_dir: Path,
    entry: Path | None,
) -> None:
    """Validate pytest presence for script-backed skills."""
    if entry is None:
        return
    test_file = repo_root / "tests" / "skills" / test_filename_for_skill(skill_dir.name)
    if not test_file.exists():
        level = "error" if tier == ".curated" else "warning"
        add_issue(
            issues,
            level,
            test_file,
            f"missing test file for script-backed skill: {test_file.name}",
        )


def validate_exec_mode(
    issues: list[Issue],
    entry: Path,
    repo_root: Path,
) -> None:
    """Run script-backed entrypoints for contract checks."""
    proc_help = run_entry_script(entry, ["--help"], repo_root=repo_root)
    if proc_help.returncode != 0:
        add_issue(
            issues,
            "error",
            entry,
            (
                "--help failed "
                f"(exit={proc_help.returncode}). stderr="
                f"{proc_help.stderr.strip()[:400]}"
            ),
        )

    proc_json = run_entry_script(
        entry,
        ["--json", "--cwd", str(repo_root)],
        repo_root=repo_root,
    )
    obj, err = validate_json_stdout(proc_json)
    if err:
        add_issue(
            issues,
            "error",
            entry,
            f"--json validation failed: {err}. stderr={proc_json.stderr.strip()[:400]}",
        )
        return

    if obj is not None and obj.get("changed") is True:
        add_issue(
            issues,
            "error",
            entry,
            "dry-run (--apply not set) must not set changed=true",
        )

    if proc_json.returncode not in (0, EXIT_PRECONDITION):
        add_issue(
            issues,
            "error",
            entry,
            (
                "unexpected exit code in json run: "
                f"{proc_json.returncode} (expected 0 or {EXIT_PRECONDITION})"
            ),
        )
    if proc_json.returncode == 0 and obj is not None and obj.get("ok") is not True:
        add_issue(issues, "error", entry, "exit=0 but ok!=true")
    if (
        proc_json.returncode == EXIT_PRECONDITION
        and obj is not None
        and obj.get("ok") is not False
    ):
        add_issue(
            issues,
            "error",
            entry,
            f"exit={EXIT_PRECONDITION} but ok!=false",
        )


def build_report_path(skill_dir: Path, repo_root: Path) -> Path:
    """Build a report path relative to repo root when possible."""
    return (
        skill_dir.relative_to(repo_root)
        if skill_dir.is_relative_to(repo_root)
        else skill_dir
    )


def validate_skill_dir(
    skill_dir: Path,
    repo_root: Path,
    skills_root: Path,
    mode: str,
    seen_names: dict[str, Path],
) -> SkillReport:
    """Validate a single skill directory."""
    skill_md = skill_dir / "SKILL.md"
    tier = detect_tier(skills_root, skill_dir)
    issues: list[Issue] = []

    name, desc = validate_metadata(issues, skill_md, skill_dir, seen_names)
    validate_directories(issues, skill_dir)

    scripts_dir = skill_dir / "scripts"
    entry = find_entry_script(skill_dir)
    if scripts_dir.exists() and entry is None:
        add_issue(
            issues,
            "error",
            scripts_dir,
            "scripts/ exists but scripts/run.py is missing",
        )

    validate_tests(issues, repo_root, tier, skill_dir, entry)

    if mode == "exec" and entry is not None:
        validate_exec_mode(issues, entry, repo_root)

    return SkillReport(
        skill_dir=str(build_report_path(skill_dir, repo_root)),
        tier=tier,
        name=name,
        description=desc,
        script_backed=entry is not None,
        issues=issues,
    )


def count_issues(reports: list[SkillReport]) -> tuple[int, int]:
    """Count errors and warnings in reports."""
    total_errors = 0
    total_warnings = 0
    for report in reports:
        for item in report.issues:
            if item.level == "error":
                total_errors += 1
            else:
                total_warnings += 1
    return total_errors, total_warnings


def emit_report(
    reports: list[SkillReport],
    summary: dict[str, Any],
    json_out: bool,
) -> None:
    """Emit output for CLI."""
    if json_out:
        payload = {"summary": summary, "reports": [asdict(r) for r in reports]}
        sys.stdout.write(f"{json.dumps(payload, ensure_ascii=False, indent=2)}\n")
        return

    sys.stderr.write(f"Skills checked: {summary['skills_checked']}\n")
    sys.stderr.write(
        f"Errors: {summary['errors']}, Warnings: {summary['warnings']}\n",
    )
    for report in reports:
        if not report.issues:
            continue
        sys.stderr.write(f"\n- {report.skill_dir} ({report.tier})\n")
        for item in report.issues:
            sys.stderr.write(f"  [{item.level}] {item.path}: {item.message}\n")


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="Validate skill directories (SKILL.md + scripts + tests).",
    )
    parser.add_argument(
        "--skills-root",
        default="skills",
        help="Root directory that contains tiers and skills.",
    )
    parser.add_argument(
        "--mode",
        default="fast",
        choices=["fast", "exec"],
        help="fast=static checks; exec=also run scripts.",
    )
    parser.add_argument(
        "--json",
        dest="json_out",
        action="store_true",
        help="Emit machine-readable report to stdout.",
    )
    parser.add_argument(
        "--fail-on-warn",
        action="store_true",
        help="Treat warnings as errors.",
    )
    ns = parser.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[1]
    skills_root = (repo_root / ns.skills_root).resolve()

    if not skills_root.exists():
        sys.stderr.write(f"❌ skills root not found: {skills_root}\n")
        return 2

    seen_names: dict[str, Path] = {}

    reports = [
        validate_skill_dir(
            skill_dir,
            repo_root=repo_root,
            skills_root=skills_root,
            mode=ns.mode,
            seen_names=seen_names,
        )
        for skill_dir in sorted(iter_skill_dirs(skills_root))
    ]

    total_errors, total_warnings = count_issues(reports)
    summary = {
        "ok": total_errors == 0 and (not ns.fail_on_warn or total_warnings == 0),
        "skills_checked": len(reports),
        "errors": total_errors,
        "warnings": total_warnings,
        "mode": ns.mode,
    }

    emit_report(reports, summary, ns.json_out)

    if total_errors > 0:
        return 1
    if ns.fail_on_warn and total_warnings > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
