# スキル作成ガイド（短縮版）

## 目的

スキルは **「発見されやすい description」** と **「小さく薄い scripts」** が重要です。
詳細は `references/` に逃がし、`SKILL.md` は短く保ちます。

## フロントマターの要点

```yaml
---
name: build-go
description: Build and test Go projects. Use when go.mod is present, or when the user mentions Go build/test.
compatibility: Requires go, git, uv. Network optional for module downloads.
metadata:
  owner: devtools
  kind: build
  language: go
---
```

- `name` は小文字英数とハイフンのみ、最大64文字、ディレクトリ名と一致
- `description` は「いつ使うか」を含め、検索しやすいキーワードを入れる
- 詳細は `references/REFERENCE.md` へ

## 推奨構成

```
skills/.curated/<name>/
  SKILL.md
  scripts/
    run.py
  references/
    REFERENCE.md
```

## 推奨キーワード

- 言語: Go / Node.js / Rust / Java / Python / .NET
- 操作: build / test / lint / format / dependency / git
- 条件: go.mod / package.json / Cargo.toml

