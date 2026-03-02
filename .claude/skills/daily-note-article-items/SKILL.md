---
name: daily-note-article-items
description: プロジェクト外のデイリーノートディレクトリから記事素材を抽出する。記事化に使える「テーマ候補」「体験エピソード」「数字・事実」「伝えたいこと」を収集し、Step 0へ転記しやすい形式で出力する。デイリーノートから記事ネタを拾いたい、日報から記事の種を抽出したい、Step 0の素材を外部ノートから作りたい場合に使用。
argument-hint: <daily_note_dir> [days]
---

# Daily Note Article Items Skill

外部のデイリーノートを対象に、記事素材候補を抽出して Markdown ファイルに保存する。

## 引数

- 第1引数: デイリーノートのディレクトリ（絶対パス）
- 第2引数: 何日分を対象にするか（任意、デフォルト 14）

## 実行手順

### Phase 1: 入力確認

1. 第1引数からデイリーノートディレクトリを取得する
2. 第2引数が未指定なら `days=14` を採用する
3. 指定ディレクトリが存在しない場合は停止し、正しいパス入力を依頼する

### Phase 2: 出力先を準備

1. 出力ディレクトリを作成する: `03_writing/02_assets/daily_note_extracts/`
2. ファイル名を作成する: `YYYYMMDD_article_items.md`
3. 出力パスを組み立てる: `03_writing/02_assets/daily_note_extracts/YYYYMMDD_article_items.md`

### Phase 3: 抽出スクリプト実行

次のコマンドで抽出する:

```bash
python3 .claude/skills/daily-note-article-items/scripts/extract_article_items.py \
  --daily-dir "<daily_note_dir>" \
  --days "<days>" \
  --out "03_writing/02_assets/daily_note_extracts/YYYYMMDD_article_items.md"
```

### Phase 4: 抽出結果を整理

1. 出力ファイルを開き、候補を確認する
2. 記事化したい項目だけを選ぶ
3. `03_writing/01_draft/<job>/step0_memo.md` の各セクションへ転記する
4. 転記時は意味を変えず、事実を補完・創作しない

## 出力フォーマット（期待）

- テーマ候補
- 自分の体験・エピソード候補
- 数字・事実候補
- 伝えたいこと候補
- 出典（ファイルパスと行番号）
- Step 0 へ転記しやすいドラフト

## 注意事項

- 外部ディレクトリは読み取り専用で扱い、元ノートを編集しない
- ステップ0の制約を厳守し、抽出結果にない事実を追加しない
- 候補が多すぎる場合は `days` を短くして再抽出する
