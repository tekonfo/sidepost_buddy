# SidePost Buddy

AIと協働して文章記事を作成するためのフレームワーク。

## 機能一覧
- **記事作成ワークフロー**: メモ→リサーチ→設計→執筆→レビュー→公開の6ステップ
- **AIインタビュー**: 漠然としたテーマから対話で素材を引き出す
- **ペルソナレビュー**: 定義したペルソナでsubagentレビューを実施
- **スライド画像生成**: YAML定義からGemini APIで画像を一括生成
- **スクリーンショット加工**: プライバシー保護（赤枠ハイライト＋機密ぼかし）
- **コンテンツ戦略管理**: Strategy → Planning → Prep → Writing → Management の5フェーズ

## QuickStart

### 1. ブランド設定を記入する

以下のファイルにブランド設定を記入する:

```
01_strategy/03_target/persona.md    ← ターゲットペルソナを定義
01_strategy/04_brand/brand_script.md ← ブランドスクリプト（SB7）を記入
00_config/concept/tone_manner.md     ← トーン＆マナーを定義
```

### 2. 記事を作成する

Claude Code で以下のスラッシュコマンドを実行:

```
/article テーマ名
```

または全体マップを確認:

```
/overview
```

### 3. スライド画像を生成する（オプション）

```bash
# 初回セットアップ
chmod +x .claude/skills/3-slide/scripts/slideimg.sh
alias slideimg='.claude/skills/3-slide/scripts/slideimg.sh'

# 画像生成
slideimg init 20260301_my_article
slideimg edit 20260301_my_article   # YAMLを編集
slideimg run  20260301_my_article   # 画像生成
```

## コンテンツライフサイクル

```
Strategy → Planning → Prep → Writing → Management
   ↑                                              |
   └─────────────── フィードバック ───────────────┘
```

| フェーズ | ディレクトリ | スキル | 役割 |
|---------|-------------|--------|------|
| Strategy | `01_strategy/` | `/strategy` | 中期計画・KPI目標 |
| Planning | `02_planning/` | `/ideation`, `/interview` | ネタ出し・テーマ評価・企画確定 |
| Prep | `03_prep/` | `/daily-note-article-items` | 調査・検証メモ・素材蓄積 |
| Writing | `04_writing/` | `/article` | 素材→執筆（Step 0-5） |
| Management | `05_management/` | `/analysis` | 進捗管理・振り返り・改善 |

詳細は `/overview` スキルで確認。

## スキル一覧（スラッシュコマンド）

| コマンド | 用途 |
|---------|------|
| `/overview` | ライフサイクル全体マップ・セッション再開 |
| `/strategy` | 中期計画策定 |
| `/ideation` | テーマ企画・評価 |
| `/interview` | AIインタビューで素材引き出し |
| `/article` | 記事作成（Step 0-5） |
| `/slide` | スライド画像生成 |
| `/screenshot` | スクリーンショット加工 |
| `/review` | ペルソナレビュー単体実行 |
| `/analysis` | 公開後振り返り |
| `/persona` | ペルソナ会話シミュレーション |
| `/daily-note-article-items` | デイリーノートから記事素材抽出 |

## ディレクトリ構造

```
402_side_post_buddy/
├── CLAUDE.md                           # AI向けプロジェクト指示
├── README.md                           # 本ファイル
├── .gitignore
│
├── .claude/skills/                     # Claude Code スキル定義
│   ├── 0-overview/                     # /overview
│   ├── 1-strategy/                     # /strategy
│   ├── 2-ideation/                     # /ideation
│   ├── 2-interview/                    # /interview
│   ├── 3-article/                      # /article（メインWF + テンプレート）
│   ├── 3-slide/                        # /slide（スクリプト + YAMLテンプレート）
│   ├── 3-screenshot/                   # /screenshot（加工スクリプト）
│   ├── 3-review/                       # /review
│   ├── 4-analysis/                     # /analysis
│   ├── x-persona/                      # /persona
│   └── daily-note-article-items/       # /daily-note-article-items
│
├── 00_config/                          # 基盤設定
│   ├── concept/                        # ブランド設定
│   │   └── tone_manner.md              # トンマナ定義
│   └── template/
│       └── brand/                      # ブランド関連テンプレート
│
├── 01_strategy/                        # Strategy: 中期計画
│   ├── 01_calendar/                    # コンテンツカレンダー
│   ├── 02_goals/                       # KPI目標・方針
│   ├── 03_target/                      # ペルソナ定義
│   └── 04_brand/                       # ブランドスクリプト
│
├── 02_planning/                        # Planning: 個別企画
│   ├── 01_ideas/                       # ネタ帳・テーマ候補
│   └── 02_evaluation/                  # テーマ評価・企画メモ
│
├── 03_prep/                            # Prep: 仕込み（調査・検証）
│   ├── 01_research/                    # 調査メモ
│   └── notes/                          # 試行・体験ログ
│
├── 04_writing/                         # Writing: 素材→執筆
│   ├── 01_draft/                       # 作業中の記事
│   ├── 02_assets/                      # 共有素材・画像
│   └── 03_published/                   # 公開済み記事
│
├── 05_management/                      # Management: 進捗管理・分析・振り返り
│   ├── 01_progress/                    # article_progress.csv と運用手順
│   ├── 02_analysis/                    # 振り返りシート・KPIデータ
│   └── scripts/                        # 進捗同期スクリプト
│
├── 90_task/                            # 横断: タスク管理
├── 99_archive/                         # アーカイブ
└── LICENSE                             # PolyForm Internal Use 1.0.0
```

## 必要要件

- **AI CLI**: Claude Code（推奨）
- **Python 3.10+**: スライド画像生成・スクリーンショット加工に必要
- **Gemini API Key**: スライド画像生成に必要（オプション）

## ライセンス

PolyForm Internal Use 1.0.0（商用利用可・再配布禁止）
詳細は [LICENSE](./LICENSE) を参照してください。
