# SidePost Buddy

AIと協働して文章記事を作成するためのフレームワーク。

## 機能一覧
- **記事作成ワークフロー**: メモ→リサーチ→設計→執筆→レビュー→公開の6ステップ
- **AIインタビュー**: 漠然としたテーマから対話で素材を引き出す
- **ペルソナレビュー**: 定義したペルソナでsubagentレビューを実施
- **スライド画像生成**: YAML定義からGemini APIで画像を一括生成
- **スクリーンショット加工**: プライバシー保護（赤枠ハイライト＋機密ぼかし）
- **コンテンツ戦略管理**: Strategy → Ideation → Writing → Analysis の4フェーズ

## QuickStart

### 1. ブランド設定を記入する

`00_config/concept/` 配下のファイルを記入する:

```
00_config/concept/persona.md       ← ターゲットペルソナを定義
00_config/concept/brand_script.md   ← ブランドスクリプト（SB7）を記入
00_config/concept/tone_manner.md    ← トーン＆マナーを定義
```

### 2. 記事を作成する

```
# ワークフローを開いて手順に従う
00_config/workflow/01_article_creation.md
```

AI（Claude Code等）に以下のように指示:

> `00_config/workflow/01_article_creation.md` を読んで、記事作成ワークフローを開始してください。

### 3. スライド画像を生成する（オプション）

```bash
# 初回セットアップ
chmod +x 00_config/workflow/scripts/slideimg.sh
alias slideimg='00_config/workflow/scripts/slideimg.sh'

# 画像生成
slideimg init 20260301_my_article
slideimg edit 20260301_my_article   # YAMLを編集
slideimg run  20260301_my_article   # 画像生成
```

## コンテンツライフサイクル

```
Strategy → Ideation → Writing → Analysis
   ↑                                   |
   └─────── フィードバック ─────────────┘
```

| フェーズ | ディレクトリ | ワークフロー | 役割 |
|---------|-------------|-------------|------|
| Strategy | `01_strategy/` | `00_config/workflow/09_strategy.md` | 中期計画・KPI目標 |
| Ideation | `02_ideation/` | `00_config/workflow/07_planning.md` | ネタ出し・テーマ評価 |
| Writing | `03_writing/` | `00_config/workflow/01_article_creation.md` | 素材→執筆（Step 0-5） |
| Analysis | `04_analysis/` | `00_config/workflow/08_post_analysis.md` | 振り返り・分析 |

詳細は `00_config/workflow/00_overview.md` を参照。

## ディレクトリ構造

```
402_side_post_buddy/
├── CLAUDE.md                           # AI向けプロジェクト指示
├── README.md                           # 本ファイル
├── .gitignore
│
├── 00_config/                          # 基盤設定
│   ├── workflow/                       # ワークフロー定義
│   │   ├── 00_overview.md              # ライフサイクル全体マップ
│   │   ├── 01_article_creation.md      # Writing メインWF（Step 0-5）
│   │   ├── 02_ai_interview.md          # AIインタビュー
│   │   ├── 03_screenshot_privacy.md    # スクリーンショット加工
│   │   ├── 04_slide_generation.md      # スライド画像作成
│   │   ├── 05_persona_roleplay.md      # ペルソナロールプレイ
│   │   ├── 06_strategy_council.md      # マルチAI戦略会議（準備中）
│   │   ├── 07_planning.md              # Ideation WF
│   │   ├── 08_post_analysis.md         # Analysis WF
│   │   ├── 09_strategy.md              # Strategy WF
│   │   ├── scripts/                    # 自動化スクリプト
│   │   └── prompts/                    # プロンプト
│   ├── concept/                        # ブランド設定（ユーザーが記入）
│   │   ├── persona.md                  # ペルソナ定義
│   │   ├── brand_script.md             # ブランドスクリプト
│   │   └── tone_manner.md              # トンマナ定義
│   └── template/                       # テンプレート
│       ├── step0_memo.md 〜 step5_publish.md  # Writing Step 0-5
│       ├── planning_memo.md            # Ideation 企画メモ
│       ├── analysis_sheet.md           # Analysis 振り返りシート
│       ├── strategy_sheet.md           # Strategy 中期計画シート
│       ├── slide_image_prompts.yaml    # スライド画像プロンプト例
│       ├── brand/                      # ブランド関連テンプレート
│       └── prompt_templates/           # 図解パターン別YAMLテンプレート
│
├── 01_strategy/                        # Strategy: 中期計画
│   ├── 01_calendar/                    # コンテンツカレンダー
│   └── 02_goals/                       # KPI目標・方針
│
├── 02_ideation/                        # Ideation: 個別企画
│   ├── 01_ideas/                       # ネタ帳・テーマ候補
│   └── 02_evaluation/                  # テーマ評価・企画メモ
│
├── 03_writing/                         # Writing: 素材→執筆
│   ├── 01_draft/                       # 作業中の記事
│   ├── 02_assets/                      # 共有素材・画像
│   └── 03_published/                   # 公開済み記事
│
├── 04_analysis/                        # Analysis: 分析・振り返り
│   └── 01_data/                        # 振り返りシート・KPIデータ
│
├── 90_task/                            # 横断: タスク管理
└── 99_archive/                         # アーカイブ
```

## 必要要件

- **AI CLI**: Claude Code / Codex / Gemini CLI のいずれか
- **Python 3.10+**: スライド画像生成・スクリーンショット加工に必要
- **tmux**: マルチAI戦略会議に必要（オプション）
- **Gemini API Key**: スライド画像生成に必要（オプション）

## ライセンス

PolyForm Internal Use 1.0.0（商用利用可・再配布禁止）
詳細は [LICENSE](./LICENSE) を参照してください。
