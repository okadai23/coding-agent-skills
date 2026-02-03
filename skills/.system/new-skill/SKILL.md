---
name: new-skill
description: "Scaffold a new Agent Skill in this repository (SKILL.md + optional scripts) following the repo script contract. Use when adding a new skill or workflow."
metadata:
  short-description: "Create a new skill skeleton for this repo."
---

# new-skill

## Purpose

This skill helps you create a new Agent Skill in this repository using the same flow as Codex's skill creation guidance:
- clarify what the skill does
- clarify when it should trigger
- choose instruction-only vs script-backed
- generate a consistent folder scaffold

Codex relies heavily on the `description` as the trigger signal, so make it concrete: what it does **and** when to use it.

## Workflow

1. Decide:
   - Skill name (must follow the Agent Skills spec: lowercase/digits/hyphens, 1–64 chars, matches directory)
   - One-line description (what it does + when to use)
   - Tier: `.experimental` (default), `.curated`, or `.system`
   - Run type: `instruction` (default) or `script`

2. Create the scaffold by running (from repo root):

```bash
uv run python tools/new_skill.py <skill-name> --description "<what it does and when to use>" --tier .experimental --run-type instruction
```

For script-backed skills:

```bash
uv run python tools/new_skill.py <skill-name> --description "<...>" --tier .experimental --run-type script
```

3. Edit the generated SKILL.md:

- Fill the TODOs
- Add “When to use” triggers (keywords, file types, situations)
- Add 2–3 realistic examples

4. If script-backed:

- Implement scripts/run.py
- Follow docs/script-contract.md (dry-run default, --json output option, clear exit codes)

5. Validate quality:

- Run ruff / tests / build checks per repository standards

## Common pitfalls

- Vague descriptions ("help with builds") → poor triggering.
- Script writes to stdout while --json is enabled → breaks agent parsing.
- Scripts making changes without --apply → unsafe.
