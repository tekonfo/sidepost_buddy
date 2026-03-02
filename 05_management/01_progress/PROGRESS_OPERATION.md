# 進捗CSV運用（ClaudeCode）

このCSVは **進捗管理専用**。  
KPI（PV・スキ等）は `05_management/02_analysis` で管理し、ここには入れない。

## 対象ファイル

- `05_management/01_progress/article_progress.csv`
- `05_management/scripts/sync_article_progress.py`

## 列（最小）

- `article_id`: 作業フォルダ名（例: `20260301_theme`）
- `title`: 記事タイトル（未定なら空で可）
- `status`: `not_started | drafting | reviewing | publish_prep | done`
- `current_step`: `0 | 1 | 2 | 3 | 4 | 4a | 4b | 4.5 | 5 | done`
- `updated_date`: 作業フォルダの最終更新日
- `next_action`: 次の1アクション（AI更新）
- `blocker`: 停滞理由（AI更新）
- `draft_dir`: 作業フォルダパス
- `progress_file`: `progress.md` のパス

## 更新フロー（推奨）

1. 機械同期（事実情報）  
   `python3 05_management/scripts/sync_article_progress.py`
2. ClaudeCode更新（判断情報）  
   `next_action` と `blocker` だけ更新する

## ClaudeCodeプロンプト例

```text
05_management/01_progress/article_progress.csv を開いて、
next_action と blocker の2列だけ更新してください。

参照元は各行の draft_dir / progress_file 配下のファイルに限定。
status, current_step, updated_date, draft_dir, progress_file は変更しない。
推測で埋めず、不明なら「要確認」と書く。
```
