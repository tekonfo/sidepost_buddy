# CLAUDE.md - SidePost Buddy

AI記事作成フレームワーク「SidePost Buddy」のプロジェクト固有指示。

## 概要

note記事をAIと協働で作成するためのワークフロー・テンプレート・スクリプト集。
Step 0（素材）→ Step 5（公開準備）の6ステップで記事を完成させる。

## ワークフロー起点

記事作成を開始する場合は、まず以下のワークフローを参照する:

| ワークフロー | ファイル | 用途 |
|-------------|---------|------|
| 記事作成 | `01_workflow/01_article_creation.md` | メインワークフロー（Step 0-5） |
| AIインタビュー | `01_workflow/02_ai_interview.md` | テーマが漠然としている場合の前段プロセス |
| スクリーンショット加工 | `01_workflow/03_screenshot_privacy.md` | 画像のプライバシー保護 |
| スライド画像作成 | `01_workflow/04_slide_generation.md` | 記事用スライド画像の生成 |
| ペルソナ会話 | `01_workflow/05_persona_roleplay.md` | ペルソナロールプレイでコンテンツ検証 |
| 戦略会議 | `01_workflow/06_strategy_council.md` | マルチAI戦略会議 |

## テンプレート

記事の各ステップのテンプレートは `template/` 配下に格納:

- `template/step0_memo.md` 〜 `template/step5_publish.md`
- `template/prompt_templates/` - スライド画像生成用YAMLテンプレート
- `template/brand/` - ブランドスクリプトテンプレート

## ブランド設定

ユーザー固有のブランド設定は `02_concept/` に記入する:

- `02_concept/persona.md` - ターゲットペルソナ定義
- `02_concept/brand_script.md` - StoryBrand SB7ブランドスクリプト
- `02_concept/tone_manner.md` - トーン＆マナー定義

## AI制約（重要）

- **Step 0は捏造禁止**: `step0_memo.md` はユーザー本人のメモ・体験・事実のみ。AIが内容を補完・推測・創作してはならない
- 以降のステップ（Step 1-5）では、Step 0に書かれた情報のみを記事の根拠として使用する
- 外部事実の引用は「仮説」「未確認」と明示する

## 作業フォルダ

記事の作業は `05_draft/` 配下にジョブフォルダを作成して行う:

```
05_draft/YYYYMMDD_{テーマ短縮}/
├── step0_memo.md
├── step1_research.md
├── ...
├── progress.md
└── image_assets/
    └── slide_image_prompts.yaml
```
