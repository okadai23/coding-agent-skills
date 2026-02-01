# detect-build-system reference

## 使い方

```bash
uv run python scripts/run.py --cwd /path/to/repo --json --check
```

## マーカー一覧

`go.mod`, `package.json`, `Cargo.toml`, `pom.xml`, `build.gradle`,
`pyproject.toml`, `CMakeLists.txt`, `Makefile` などを検出します。

