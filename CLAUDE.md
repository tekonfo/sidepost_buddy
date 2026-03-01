# CLAUDE.md - SidePost Buddy

AI記事作成フレームワーク「SidePost Buddy」のプロジェクト固有指示。

## 概要

note記事をAIと協働で作成するためのワークフロー・テンプレート・スクリプト集。
4つのフェーズ（Strategy → Ideation → Writing → Analysis）でコンテンツ活動全体を管理する。

## フェーズ構成

```
Strategy → Ideation → Writing → Analysis
   ↑                                   |
   └─────── フィードバック ─────────────┘
```

| フェーズ | ディレクトリ | 役割 |
|---------|-------------|------|
| Strategy | `01_strategy/` | 中期計画・コンテンツカレンダー・KPI目標 |
| Ideation | `02_ideation/` | 個別記事のネタ出し・テーマ評価・確定 |
| Writing | `03_writing/` | 素材収集 → 執筆（既存Step 0-5） |
| Analysis | `04_analysis/` | 公開後の振り返り・パフォーマンス分析 |

ライフサイクル全体は `00_config/workflow/00_overview.md` を参照。

## ワークフロー起点

作業を開始する場合は、まず以下のワークフローを参照する:

| ワークフロー | ファイル | 用途 |
|-------------|---------|------|
| ライフサイクル全体 | `00_config/workflow/00_overview.md` | フェーズ全体マップ |
| 記事作成 | `00_config/workflow/01_article_creation.md` | Writing メインワークフロー（Step 0-5） |
| AIインタビュー | `00_config/workflow/02_ai_interview.md` | テーマが漠然としている場合の前段プロセス |
| スクリーンショット加工 | `00_config/workflow/03_screenshot_privacy.md` | 画像のプライバシー保護 |
| スライド画像作成 | `00_config/workflow/04_slide_generation.md` | 記事用スライド画像の生成 |
| ペルソナ会話 | `00_config/workflow/05_persona_roleplay.md` | ペルソナロールプレイでコンテンツ検証 |
| 戦略会議 | `00_config/workflow/06_strategy_council.md` | マルチAI戦略会議（準備中） |
| 個別企画 | `00_config/workflow/07_planning.md` | Ideation テーマ評価ワークフロー |
| 公開後分析 | `00_config/workflow/08_post_analysis.md` | Analysis 振り返りワークフロー |
| 中期計画 | `00_config/workflow/09_strategy.md` | Strategy 計画策定ワークフロー |

## テンプレート

テンプレートは `00_config/template/` 配下に格納:

- `00_config/template/step0_memo.md` 〜 `00_config/template/step5_publish.md` — Writing 各ステップ
- `00_config/template/planning_memo.md` — Ideation 企画メモ
- `00_config/template/analysis_sheet.md` — Analysis 振り返りシート
- `00_config/template/strategy_sheet.md` — Strategy 中期計画シート
- `00_config/template/prompt_templates/` — スライド画像生成用YAMLテンプレート
- `00_config/template/brand/` — ブランドスクリプトテンプレート

## ブランド設定

ユーザー固有のブランド設定は `00_config/concept/` に記入する:

- `00_config/concept/persona.md` — ターゲットペルソナ定義
- `00_config/concept/brand_script.md` — StoryBrand SB7ブランドスクリプト
- `00_config/concept/tone_manner.md` — トーン＆マナー定義

## AI制約（重要）

- **Step 0は捏造禁止**: `step0_memo.md` はユーザー本人のメモ・体験・事実のみ。AIが内容を補完・推測・創作してはならない
- 以降のステップ（Step 1-5）では、Step 0に書かれた情報のみを記事の根拠として使用する
- 外部事実の引用は「仮説」「未確認」と明示する

## 作業フォルダ

記事の作業は `03_writing/01_draft/` 配下にジョブフォルダを作成して行う:

```
03_writing/01_draft/YYYYMMDD_{テーマ短縮}/
├── step0_memo.md
├── step1_research.md
├── ...
├── progress.md
└── image_assets/
    └── slide_image_prompts.yaml
```
