# Agent Skills Catalog

多言語ビルド支援・Git/推奨ツール実行の支援を目的とした「スキルカタログ」リポジトリです。
スキル本体は標準フォーマット（`SKILL.md` + `scripts/` + `references/`）を維持し、共通ランタイムと共通I/Fで品質を揃えます。

## 目的

- スキルのフォーマットを標準準拠に寄せる
- Pythonスクリプトを共通I/Fと共通ユーティリティで統一する
- 追加・検証・配布の導線を自動化する

## ディレクトリ構成

```
skills/
  .curated/        # 安定版
  .experimental/   # 検証中
  .system/         # リポジトリ運用用
src/skillkit/      # 共通Pythonライブラリ
tools/             # 生成・検証・配布・索引生成
docs/              # 執筆/スクリプトI/Fガイド
tests/             # ユニット/統合テスト
fixtures/          # テスト用サンプルプロジェクト
```

## クイックスタート

```bash
# 依存インストール
uv sync --extra dev

# スキル雛形の生成
uv run python tools/new_skill.py --name build-go --description "Go build/test helper"

# スキル検証
uv run python tools/validate_skills.py

# カタログ索引生成
uv run python tools/build_index.py

# スキル配布（~/.codex/skills と ~/.claude/skills へ symlink）
uv run python tools/install.py --mode symlink
```

## スクリプトI/F

共通I/Fの詳細は `docs/script-contract.md` を参照してください。
`skills/**/scripts/run.py` は以下の最低限のフラグを実装します。

- `--cwd PATH`
- `--json`
- `--check` / `--apply`（デフォルトは `--check`）
- `--timeout SEC`

## 参考資料

- `docs/authoring.md`: スキル設計/記述のガイド
- `docs/script-contract.md`: スクリプトI/FとJSONスキーマ

