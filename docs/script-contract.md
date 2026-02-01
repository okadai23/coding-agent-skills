# Scripts Contract

## CLI 規約

すべての `skills/**/scripts/run.py` は以下のI/Fを実装します。

```
--cwd PATH      : 対象プロジェクトのルート（指定なしは .）
--json          : JSONをstdoutに出力（人間向けログはstderr）
--check         : 破壊的変更を行わない（デフォルト）
--apply         : 破壊的変更を許可
--timeout SEC   : 外部コマンドの上限（秒）
```

## exit code

| code | 意味 |
| ---- | ---- |
| 0 | success |
| 2 | 実行したが条件未達（例: lint失敗, dirty） |
| 3 | 前提不足（必要コマンドがない等） |
| 4 | 想定外エラー |

## JSON スキーマ（最低限）

```json
{
  "ok": true,
  "summary": "go test ./... passed",
  "actions": [
    {"cmd": "go test ./...", "cwd": "/repo", "exit_code": 0}
  ],
  "diagnostics": [],
  "artifacts": []
}
```

## スクリプト実装の推奨

- `skillkit.cli` で引数解析を統一
- `skillkit.report` でJSON整形を統一
- `skillkit.proc` で外部コマンド実行を統一

