#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

TIERS = [".curated", ".experimental", ".system"]


def iter_skill_dirs(skills_root: Path) -> list[Path]:
    """Return skill directories that include SKILL.md."""
    skill_dirs: list[Path] = []
    for skill_md in skills_root.rglob("SKILL.md"):
        if "__pycache__" in skill_md.parts:
            continue
        skill_dirs.append(skill_md.parent)
    return skill_dirs


def test_filename_for_skill(name: str) -> str:
    """Return the canonical test filename for a skill."""
    return f"test_{name.replace('-', '_')}.py"


def render_test(skill_name: str) -> str:
    """Render the pytest skeleton for a script-backed skill."""
    lines = [
        "from __future__ import annotations",
        "",
        "import json",
        "import subprocess",
        "import sys",
        "from pathlib import Path",
        "",
        "",
        "REPO_ROOT = Path(__file__).resolve().parents[2]",
        f'SKILL_NAME = "{skill_name}"',
        f"TIERS = {TIERS!r}",
        "",
        "",
        "def find_skill_dir() -> Path:",
        "    for tier in TIERS:",
        '        path = REPO_ROOT / "skills" / tier / SKILL_NAME',
        "        if path.exists():",
        "            return path",
        "    raise AssertionError(",
        '        f"Skill directory not found for {SKILL_NAME} under skills/{TIERS}"',
        "    )",
        "",
        "",
        "def run_script(*args: str) -> subprocess.CompletedProcess[str]:",
        "    skill_dir = find_skill_dir()",
        '    script = skill_dir / "scripts" / "run.py"',
        '    assert script.exists(), f"Missing entry script: {script}"',
        "    return subprocess.run(",
        "        [sys.executable, str(script), *args],",
        "        cwd=str(REPO_ROOT),",
        "        text=True,",
        "        capture_output=True,",
        "        check=False,",
        "    )",
        "",
        "",
        "def parse_json_stdout(proc: subprocess.CompletedProcess[str]) -> dict:",
        '    assert proc.stdout.strip(), "stdout is empty in --json mode"',
        "    obj = json.loads(proc.stdout)",
        '    assert isinstance(obj, dict), "JSON output must be an object"',
        '    for key in ("ok", "summary", "changed"):',
        '        assert key in obj, f"JSON missing required key: {key}"',
        '    assert isinstance(obj["ok"], bool)',
        '    assert isinstance(obj["summary"], str)',
        '    assert isinstance(obj["changed"], bool)',
        "    return obj",
        "",
        "",
        "def test_help_works():",
        '    proc = run_script("--help")',
        "    assert proc.returncode == 0, proc.stderr",
        "",
        "",
        "def test_json_contract_dry_run():",
        '    proc = run_script("--json", "--cwd", str(REPO_ROOT))',
        "    assert proc.returncode in (0, 3), (",
        '        f"unexpected exit={proc.returncode} stderr={proc.stderr}"',
        "    )",
        "    obj = parse_json_stdout(proc)",
        '    assert obj["changed"] is False',
        "",
        "    if proc.returncode == 0:",
        '        assert obj["ok"] is True',
        "    if proc.returncode == 3:",
        '        assert obj["ok"] is False',
        "",
        "",
        "def test_json_contract_invalid_cwd_is_precondition_failure():",
        '    bad = REPO_ROOT / ".tmp" / "does-not-exist"',
        '    proc = run_script("--json", "--cwd", str(bad))',
        "    assert proc.returncode == 3, (",
        '        f"expected exit=3, got {proc.returncode} stderr={proc.stderr}"',
        "    )",
        "    obj = parse_json_stdout(proc)",
        '    assert obj["ok"] is False',
        '    assert obj["changed"] is False',
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="Generate pytest skeleton tests for script-backed skills.",
    )
    parser.add_argument("--skills-root", default="skills")
    parser.add_argument("--tests-dir", default="tests/skills")
    parser.add_argument("--overwrite", action="store_true")
    ns = parser.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[1]
    skills_root = (repo_root / ns.skills_root).resolve()
    tests_dir = (repo_root / ns.tests_dir).resolve()

    if not skills_root.exists():
        sys.stderr.write(f"❌ skills root not found: {skills_root}\n")
        return 2

    tests_dir.mkdir(parents=True, exist_ok=True)

    created = 0
    skipped = 0

    for skill_dir in sorted(iter_skill_dirs(skills_root)):
        name = skill_dir.name
        entry = skill_dir / "scripts" / "run.py"
        if not entry.exists():
            continue

        test_path = tests_dir / test_filename_for_skill(name)
        if test_path.exists() and not ns.overwrite:
            skipped += 1
            continue

        test_path.write_text(render_test(name), encoding="utf-8")
        created += 1

    sys.stdout.write(f"✅ tests generated: {created}, skipped: {skipped}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
