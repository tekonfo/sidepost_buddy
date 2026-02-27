# マルチAI戦略会議（Strategy Council）

記事のリサーチ・設計フェーズ（Step 1-2）において、複数のAIエージェントを並列に活用して意思決定の質を高めるためのワークフロー。

---

## 概要

tmuxの4ペインレイアウトで、3人のAIアドバイザーとオーケストレーターが並列に議論する。

| ペイン | 役割 | 担当AI | プロンプト |
|--------|------|--------|-----------|
| pane0 | オーケストレーター | Claude | `orchestrator.md` |
| pane1 | コンテンツ戦略 | Claude | `content_strategist.md` |
| pane2 | 実行設計・リスク | Codex | `execution_risk.md` |
| pane3 | 市場性・配信 | Gemini | `market_distribution.md` |

## 進行フロー

```
Round 1: 各アドバイザーが独立に提案（3案まで）
  ↓
Round 2: 他の提案を相互レビュー（弱点指摘＋改善案）
  ↓
Round 3: 収束と意思決定（1案採用＋保留事項整理）
  ↓
Write-back: step1/step2 に転記
```

## 使い方

### 1. セッション開始

```bash
# council.sh にエイリアスを設定（初回のみ）
chmod +x 01_workflow/scripts/council.sh
alias council='01_workflow/scripts/council.sh'

# セッション開始
council start 20260220_ai_plan
```

### 2. プロンプト送信

```bash
# オーケストレーターにロールを送信
council send sp-council 0 01_workflow/prompts/strategy_council/orchestrator.md

# 各アドバイザーにロールを送信
council send sp-council 1 01_workflow/prompts/strategy_council/content_strategist.md
council send sp-council 2 01_workflow/prompts/strategy_council/execution_risk.md
council send sp-council 3 01_workflow/prompts/strategy_council/market_distribution.md

# Round 1: 独立提案
council send sp-council 1 01_workflow/prompts/strategy_council/round1_proposal.md
council send sp-council 2 01_workflow/prompts/strategy_council/round1_proposal.md
council send sp-council 3 01_workflow/prompts/strategy_council/round1_proposal.md
```

### 3. 出力キャプチャ

```bash
council capture sp-council 1 /tmp/strategist.log 400
council capture sp-council 2 /tmp/risk.log 400
```

### 4. セッション管理

```bash
council ls        # セッション一覧
council attach    # セッションに再接続
council stop      # セッション終了
```

## 前提条件

- `tmux` がインストールされていること
- `claude`, `codex`, `gemini` CLIが使用可能であること
- 記事の `step0_memo.md` が作成済みであること

## プロンプトファイル

すべて `01_workflow/prompts/strategy_council/` 配下に格納。

| ファイル | 用途 |
|----------|------|
| `orchestrator.md` | 会議進行・意思決定ルール |
| `content_strategist.md` | コンテンツ戦略提案 |
| `execution_risk.md` | 実行設計・リスク評価 |
| `market_distribution.md` | 市場性・配信チャネル評価 |
| `round1_proposal.md` | Round 1 独立提案指示 |
| `round2_critique.md` | Round 2 相互レビュー指示 |
| `round3_consensus.md` | Round 3 収束・意思決定指示 |

## 成果物

会議の成果物は `05_draft/<job>/strategy_council/` に保存される。

- `agenda.md` - 会議アジェンダ
- `round_log.md` - 各ラウンドの記録
- `consensus.md` - 最終合意事項
