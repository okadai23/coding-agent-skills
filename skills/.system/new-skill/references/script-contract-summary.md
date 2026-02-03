# Script Contract Summary (v1)

- Default: dry-run. Only modify files when `--apply` is provided.
- Must support: `--json`, `--apply`, `--cwd`, `--verbose`.
- With `--json`: write exactly one JSON object to STDOUT, nothing else.
- Human logs go to STDERR.
- Exit codes: 0 success, 2 usage, 3 precondition failed, 4 operation failed.
- Full contract: see `docs/script-contract.md`.
