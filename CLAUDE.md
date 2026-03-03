# CLAUDE.md - SidePost Buddy

AI記事作成フレームワーク「SidePost Buddy」のプロジェクト固有指示。

## 概要

note記事をAIと協働で作成するためのワークフロー・テンプレート・スクリプト集。
5つのフェーズ（Strategy → Planning → Prep → Writing → Management）でコンテンツ活動全体を管理する。

## フェーズ構成

```
Strategy → Planning → Prep → Writing → Management
   ↑                                              |
   └─────────────── フィードバック ───────────────┘
```

| フェーズ | ディレクトリ | 役割 |
|---------|-------------|------|
| Strategy | `01_strategy/` | 中期計画・コンテンツカレンダー・KPI目標 |
| Planning | `02_planning/` | 個別記事のネタ出し・テーマ評価・確定 |
| Prep | `03_prep/` | 調査・検証メモ・体験ログの蓄積 |
| Writing | `04_writing/` | 素材収集 → 執筆（Step 0-5） |
| Management | `05_management/` | 進捗管理・公開後の振り返り・改善 |

ライフサイクル全体は `/overview` スキルで確認。

## スキル（スラッシュコマンド）

作業を開始する場合は、対応するスキルを実行する:

| コマンド | フェーズ | 用途 |
|---------|---------|------|
| `/overview` | - | ライフサイクル全体マップ・セッション再開 |
| `/strategy` | Strategy | 中期計画策定 |
| `/ideation` | Planning | テーマ企画・評価 |
| `/interview` | Planning | AIインタビューで素材引き出し |
| `/article` | Writing | 記事作成（Step 0-5） |
| `/slide` | Writing | スライド画像生成 |
| `/screenshot` | Writing | スクリーンショット加工 |
| `/review` | Writing | ペルソナレビュー単体実行 |
| `/analysis` | Management | 公開後振り返り |
| `/persona` | Cross | ペルソナ会話シミュレーション |
| `/daily-note-article-items` | Prep | デイリーノートから記事素材抽出 |

各スキルの詳細は `.claude/skills/` 配下の SKILL.md を参照。

## ブランド設定

| ファイル | パス | 用途 |
|---------|------|------|
| ペルソナ定義 | `01_strategy/03_target/persona.md` | ターゲット読者の定義 |
| ブランドスクリプト | `01_strategy/04_brand/brand_script.md` | StoryBrand SB7 |
| トーン＆マナー | `00_config/concept/tone_manner.md` | 文体・表現ルール |
| ブランドスクリプトテンプレート | `01_strategy/04_brand/brand_script_template.md` | ブランドスクリプトの型 |

## AI制約（重要）

- **Step 0は捏造禁止**: `step0_memo.md` はユーザー本人のメモ・体験・事実のみ。AIが内容を補完・推測・創作してはならない
- 以降のステップ（Step 1-5）では、Step 0に書かれた情報のみを記事の根拠として使用する
- 外部事実の引用は「仮説」「未確認」と明示する

## 作業フォルダ

記事の作業は `04_writing/01_draft/` 配下にジョブフォルダを作成して行う:

```
04_writing/01_draft/YYYYMMDD_{テーマ短縮}/
├── step0_memo.md
├── step1_research.md
├── ...
├── progress.md
└── image_assets/
    └── slide_image_prompts.yaml
```

## Claude Code ツール利用ガイドライン

### ファイル操作パターン
- テンプレートは各スキルディレクトリ内の `.md` ファイルを **Read** → 作業フォルダに **Write** でコピー
- 独立したファイルの読み込みは**並列 Read** で効率化
- 記事の修正は **Edit** tool で差分のみ更新

### 進行管理パターン
- セッション内: **TaskCreate** / **TaskUpdate** で各ステップを追跡
- セッション永続化: 各ステップ完了時に `progress.md` を **Write** で更新
- 途中再開: **Glob** `04_writing/01_draft/*/progress.md` → **Read** で状態復元

### ペルソナ処理パターン
- ペルソナレビュー（Step 4）: **Agent tool** (subagent_type: general-purpose) でサブエージェント実行
- ペルソナ会話（`/persona`）: **Agent tool** でロールプレイ実行
- プロンプトテンプレートは各スキルディレクトリ内の `*_prompt.md` を参照

### 並列実行パターン
- 複数のファイル Read は可能な限り並列で実行
- WebSearch も独立したクエリは並列で実行
- Agent tool の並列起動は複数ペルソナの比較時に使用
