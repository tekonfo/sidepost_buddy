---
name: slide
description: "[Phase 3] 記事用スライド画像の生成。YAML編集→構文チェック→画像生成を実行する"
argument-hint: "[ジョブフォルダ名]"
---

# スライド画像作成ワークフロー

記事用のスライド画像を YAML ベースで生成する。

## いつ使うか

- `/article` の Step 4.5 でスライド画像を作成するとき
- 既存記事のスライドを更新・追加するとき

---

## 起動時の処理

1. 引数からジョブフォルダ名を取得（例: `20260220_coding_agent`）
2. 作業フォルダのパスを特定: `03_writing/01_draft/{ジョブ名}/`
3. **Read** `image_assets/slide_image_prompts.yaml` + 記事本文（`step3_writing.md`）

---

## ワークフロー

### Step 1: YAML 編集

1. **Read** 記事本文と既存の YAML
2. **Edit** tool で YAML の各プロンプトを記事内容に合わせて更新
   - 各スライド（cover / problem / solution / closing 等）の `prompt` を記事の各セクションに対応した内容に書き換え
   - step2 の「画像の配置計画」がある場合はそれに従う

### Step 2: 構文チェック

```bash
.claude/skills/3-slide/scripts/slideimg.sh dry {ジョブ名}
```

### Step 3: 画像生成

```bash
.claude/skills/3-slide/scripts/slideimg.sh run {ジョブ名}
```

### Step 4: 確認

1. **Read** 生成画像を確認（Claude Code の画像読み取り機能）
2. ユーザーに報告
3. 必要に応じて YAML を調整して再生成

### オプション: 高品質版

```bash
.claude/skills/3-slide/scripts/slideimg.sh pro {ジョブ名}
```

---

## コマンド一覧

| コマンド | 用途 |
|---------|------|
| `slideimg.sh init {ジョブ名}` | YAML 雛形を作る |
| `slideimg.sh edit {ジョブ名}` | YAML を開く |
| `slideimg.sh dry {ジョブ名}` | 構文チェック（APIなし） |
| `slideimg.sh run {ジョブ名}` | 標準生成 |
| `slideimg.sh pro {ジョブ名}` | Pro 生成（PNG, 1K） |

※ スクリプトパス: `.claude/skills/3-slide/scripts/slideimg.sh`

---

## 仕様

- `.venv` がなければ自動作成（`python3 -m venv`）
- 依存がなければ自動インストール（`requirements.txt`）
- API キーが未設定なら Keychain（service: `GEMINI_API_KEY`）から自動読み込み
- 実行対象: `03_writing/01_draft/{ジョブ名}/image_assets/slide_image_prompts.yaml`

## YAML 最小ルール

- `slides[].name` が出力ファイル名
- `slides[].prompt` は map/list 形式
- `default_aspect_ratio` 未指定時は `16:9`

## プロンプトテンプレート

`prompt_templates/` 配下に5パターンの雛形:

| ファイル | パターン |
|---------|---------|
| `slide_image_prompts_00_rule_and_blank.yaml` | ルール＋ブランク（デフォルト） |
| `slide_image_prompts_01_flow.yaml` | フロー図 |
| `slide_image_prompts_02_comparison.yaml` | 比較表 |
| `slide_image_prompts_03_timeline.yaml` | タイムライン |
| `slide_image_prompts_04_funnel.yaml` | ファネル図 |

---

## 関連スキル

- `/article` — Step 4.5 から連携
