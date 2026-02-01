---
name: detect-build-system
description: Detect build systems by file markers. Use when choosing build/test/lint skills for a repository.
compatibility: Requires Python only. Network not required.
metadata:
  owner: devtools
  kind: detect
---

# detect-build-system

## What this skill does
- Scans marker files to infer build systems
- Emits a JSON report listing detected systems

## Scripts
- Run: `uv run python scripts/run.py --cwd . --json --check`

## Troubleshooting
See [references/REFERENCE.md](references/REFERENCE.md).
