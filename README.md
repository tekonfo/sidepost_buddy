# SidePost Buddy

AIと協働してnote記事を作成するためのフレームワーク。

## 機能一覧

- **記事作成ワークフロー**: メモ→リサーチ→設計→執筆→レビュー→公開の6ステップ
- **AIインタビュー**: 漠然としたテーマから対話で素材を引き出す
- **ペルソナレビュー**: 定義したペルソナでsubagentレビューを実施
- **スライド画像生成**: YAML定義からGemini APIで画像を一括生成
- **スクリーンショット加工**: プライバシー保護（赤枠ハイライト＋機密ぼかし）
- **マルチAI戦略会議**: Claude/Codex/Geminiの3エージェント並列議論

## QuickStart

### 1. ブランド設定を記入する

`02_concept/` 配下のテンプレートを記入する:

```
02_concept/persona.md       ← ターゲットペルソナを定義
02_concept/brand_script.md   ← ブランドスクリプト（SB7）を記入
02_concept/tone_manner.md    ← トーン＆マナーを定義
```

### 2. 記事を作成する

```
# ワークフローを開いて手順に従う
01_workflow/01_article_creation.md
```

AI（Claude Code等）に以下のように指示:

> `01_workflow/01_article_creation.md` を読んで、記事作成ワークフローを開始してください。

### 3. スライド画像を生成する（オプション）

```bash
# 初回セットアップ
chmod +x 01_workflow/scripts/slideimg.sh
alias slideimg='01_workflow/scripts/slideimg.sh'

# 画像生成
slideimg init 20260301_my_article
slideimg edit 20260301_my_article   # YAMLを編集
slideimg run  20260301_my_article   # 画像生成
```

## ディレクトリ構造

```
402_side_post_buddy/
├── CLAUDE.md                    # AI向けプロジェクト指示
├── README.md                    # 本ファイル
├── .gitignore
│
├── 01_workflow/                 # コアワークフロー
│   ├── 01_article_creation.md   # 記事作成ワークフロー
│   ├── 02_ai_interview.md       # AIインタビュー
│   ├── 03_screenshot_privacy.md # スクリーンショット加工
│   ├── 04_slide_generation.md   # スライド画像作成
│   ├── 05_persona_roleplay.md   # ペルソナロールプレイ
│   ├── 06_strategy_council.md   # マルチAI戦略会議
│   ├── scripts/                 # 自動化スクリプト
│   └── prompts/                 # 戦略会議用プロンプト
│
├── 02_concept/                  # ブランド設定（ユーザーが記入）
│   ├── persona.md               # ペルソナ定義
│   ├── brand_script.md          # ブランドスクリプト
│   └── tone_manner.md           # トンマナ定義
│
├── 03_target/                   # ターゲット分析
├── 04_task/                     # タスク管理
├── 05_draft/                    # 作業中の記事
├── 06_output/                   # 完成記事
├── 07_data/                     # データ
├── 80_asset/                    # アセット
├── 99_archive/                  # アーカイブ
│
└── template/                    # テンプレート
    ├── step0_memo.md            # Step 0: 素材メモ
    ├── step1_research.md        # Step 1: リサーチ
    ├── step2_design.md          # Step 2: 設計
    ├── step3_writing.md         # Step 3: 執筆
    ├── step4_review.md          # Step 4: レビュー
    ├── step5_publish.md         # Step 5: 公開準備
    ├── slide_image_prompts.yaml # スライド画像プロンプト例
    ├── brand/                   # ブランド関連テンプレート
    └── prompt_templates/        # 図解パターン別YAMLテンプレート
```

## 必要要件

- **AI CLI**: Claude Code / Codex / Gemini CLI のいずれか
- **Python 3.10+**: スライド画像生成・スクリーンショット加工に必要
- **tmux**: マルチAI戦略会議に必要（オプション）
- **Gemini API Key**: スライド画像生成に必要（オプション）

## ライセンス

MIT
