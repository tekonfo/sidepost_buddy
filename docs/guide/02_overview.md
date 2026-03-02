# Chapter 2: 全体像を理解する

## 4 フェーズのライフサイクル

SidePost Buddy は以下の 4 フェーズで構成されています。

```
Strategy → Ideation → Writing → Analysis
   ↑                                   |
   └─────── フィードバック ─────────────┘
```

| フェーズ | 役割 | スラッシュコマンド |
|---------|------|-------------------|
| **Strategy** | 中期計画・KPI・カレンダーの策定 | `/strategy` |
| **Ideation** | テーマのネタ出し・評価・確定 | `/ideation`, `/interview` |
| **Writing** | 記事の作成（Step 0〜5） | `/article`, `/slide`, `/review` |
| **Analysis** | 公開後の振り返り・改善 | `/analysis` |

フェーズ横断で使えるコマンドもあります。

| コマンド | 用途 |
|---------|------|
| `/overview` | 全体マップの表示・進行中記事の検出 |
| `/persona` | ペルソナ会話シミュレーション |
| `/daily-note-article-items` | デイリーノートから記事素材を抽出 |

## ディレクトリ構成

```
402_side_post_buddy/
├── 00_config/          ← ブランド設定・トーン＆マナー
├── 01_strategy/        ← Strategy フェーズの成果物
│   ├── 01_calendar/    　  コンテンツカレンダー
│   ├── 02_goals/       　  KPI・戦略計画
│   ├── 03_target/      　  ペルソナ定義
│   └── 04_brand/       　  ブランドスクリプト
├── 02_ideation/        ← Ideation フェーズの成果物
│   ├── 01_ideas/       　  テーマ候補
│   └── 02_evaluation/  　  企画メモ（評価結果）
├── 03_writing/         ← Writing フェーズの作業場所
│   ├── 01_draft/       　  記事作業フォルダ
│   ├── 02_assets/      　  共有素材
│   └── 03_published/   　  公開済み記事
├── 04_analysis/        ← Analysis フェーズの振り返りデータ
├── docs/               ← ドキュメント（このガイド）
└── CLAUDE.md           ← AI への指示ファイル
```

## 記事作業フォルダの構造

`/article` コマンドで記事を作成すると、`03_writing/01_draft/` 配下に専用フォルダが生成されます。

```
03_writing/01_draft/20260302_副業の始め方/
├── progress.md                 ← 進捗チェックリスト
├── step0_memo.md               ← 素材メモ（ユーザー入力）
├── step1_research.md           ← リサーチ結果
├── step2_design.md             ← 記事設計
├── step3_writing.md            ← 本文
├── step4_review.md             ← ペルソナレビュー結果
├── step5_publish.md            ← 公開準備チェック
└── image_assets/               ← スライド画像関連
    └── slide_image_prompts.yaml
```

## Writing フェーズの 6 ステップ

記事作成は以下の流れで進みます。ステップ間に「ゲートチェック」があり、品質を担保します。

```
Step 0 → [Gate 1] → Step 1 → Step 2 → [Gate 2] → Step 3 → Step 4 → [Gate 3] → Step 4.5 → Step 5
```

| ステップ | 内容 | ポイント |
|---------|------|---------|
| Step 0 | 素材メモ | ユーザーが体験・事実を書く。**AI の捏造禁止** |
| Gate 1 | 素材チェック | テーマ + 1つ以上のエピソードがあるか確認 |
| Step 1 | リサーチ | 関連情報の調査・整理 |
| Step 2 | 記事設計 | 構成・見出し・不足情報の特定 |
| Gate 2 | 情報チェック | 必須情報がすべて揃っているか確認 |
| Step 3 | 本文執筆 | トーン＆マナーに沿って記事を書く |
| Step 4 | ペルソナレビュー | ペルソナ視点で 5 軸評価（最大 3 ラウンド） |
| Gate 3 | レビュー合格判定 | ×（要修正）= 0 かつ △ ≤ 2 |
| Step 4.5 | スライド画像 | （任意）記事用の画像生成 |
| Step 5 | 公開準備 | 最終チェックリスト |

## 現在の状態を確認する

いつでも `/overview` コマンドを実行すると、以下を確認できます。

- ライフサイクル全体マップ
- 進行中の記事とそのステップ
- 次にやるべきアクション

## 次のステップ

[Chapter 3: 初期セットアップ](./03_setup.md) で、記事を書く前に必要な準備を行いましょう。
