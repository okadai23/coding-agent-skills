---
name: git-status
description: Show git status and diff summary. Use when the user asks about git cleanliness or before running tools.
compatibility: Requires git. Network not required.
metadata:
  owner: devtools
  kind: git
---

# git-status

## What this skill does
- Checks if the working tree is clean
- Emits a JSON report of git status and diff summary

## Scripts
- Run: `uv run python scripts/run.py --cwd . --json --check`

## Troubleshooting
See [references/REFERENCE.md](references/REFERENCE.md).
