# Script Contract (v1)

This document defines the contract for Python scripts invoked by skills in this repository.

Goals:
- Predictable CLI and exit codes
- Safe-by-default behavior (no destructive changes unless explicitly requested)
- Machine-readable output option (JSON) for agents
- Works under `uv run python ...` (preferred) and plain `python ...`

## 0. Definitions

- **Script**: a Python file under a skill's `scripts/` directory.
- **Dry-run**: default mode; does not modify user files or repo state.
- **Apply**: explicit mode; allowed to modify files.

Normative words: MUST, SHOULD, MAY.

## 1. Invocation

Scripts MUST be executable with:

- `uv run python <script_path> ...` (preferred)
- `python <script_path> ...` (fallback)

Scripts MUST NOT require interactive input (no `input()` prompts). If parameters are missing, exit with a usage error.

## 2. Standard CLI flags

All scripts MUST implement these flags:

- `--json`  
  If set, the script MUST write exactly **one** JSON object to STDOUT and MUST NOT write any other text to STDOUT.

- `--apply`  
  If set, the script MAY write/modify files. If not set, it MUST operate in dry-run mode.

- `--cwd <path>`  
  If set, the script MUST treat it as the working directory for all relative paths.
  If omitted, use current working directory.

- `--verbose`  
  If set, emit more diagnostic logs to STDERR.

Recommended (optional) flags:
- `--timeout-seconds <int>` for long operations
- `--allow-network` if network access is ever needed (default: no network)

## 3. Output rules

### 3.1 Human output
- Human-readable logs MUST go to **STDERR** (not STDOUT).
- In non-JSON mode, the script MAY print a concise human summary to STDOUT.

### 3.2 JSON output
When `--json` is set, output MUST be a single JSON object shaped like:

```json
{
  "ok": true,
  "summary": "One-line summary",
  "changed": false,
  "actions": [
    { "kind": "command", "detail": "go test ./...", "cwd": "." }
  ],
  "artifacts": [
    { "path": "reports/build.json", "description": "Build report" }
  ],
  "warnings": [],
  "errors": [],
  "metadata": { "script_version": "0.1.0" }
}
```

Field meanings:

ok (bool, required): overall success

summary (string, required): one-line summary

changed (bool, required): whether the script actually changed files (true only with --apply)

actions (list, optional): what the script ran or intends to run

artifacts (list, optional): files created/updated (paths relative to --cwd)

warnings (list of strings, optional)

errors (list of objects, optional): each should include at least message

metadata (object, optional): free-form

## 4. Exit codes

Scripts MUST use:

0 success

2 usage / invalid arguments

3 precondition failed (missing tool, missing file, unsupported project layout)

4 operation failed (command error, unexpected exception)

## 5. Safety & determinism

Default MUST be dry-run (--apply required for changes).

Scripts SHOULD avoid network access by default.

Scripts SHOULD validate required external tools early and report clear errors.

Scripts SHOULD be idempotent when possible.

## 6. Agent friendliness

Scripts SHOULD include enough detail in actions for an agent to explain what happened.

If a script runs subprocess commands, it SHOULD capture stdout/stderr and include key info in JSON (but avoid dumping huge logs).

## 7. Repository conventions

Keep dependencies minimal. Prefer Python stdlib.

If third-party deps are needed, they MUST be declared in the repository’s pyproject.toml and kept stable.

Code style: ruff-compatible, type hints recommended.
