---
name: strategy
description: "[Phase 1] 中期コンテンツ計画の策定・見直し。KPI目標・コンテンツカレンダーを作成する"
argument-hint: "[new|update]"
---

# Strategy ワークフロー（中期計画策定）

中期的なコンテンツ方針を策定し、コンテンツカレンダーとKPI目標を管理する。

## いつ使うか

- コンテンツ活動を始める前に方向性を定めたいとき
- 四半期・月次でコンテンツ方針を見直すとき
- Analysis の結果を受けて戦略を調整するとき

## フロー位置

```
/analysis → /strategy → /ideation → /article → /analysis（循環）
```

---

## 成果物

| 成果物 | 保存先 | テンプレート |
|--------|--------|-------------|
| 中期計画シート | `01_strategy/02_goals/` | [strategy_sheet.md](strategy_sheet.md) |
| コンテンツカレンダー | `01_strategy/01_calendar/` | 自由形式 |

---

## ワークフロー

### Step 1: 現状把握

以下を**並列で実行**:
- **Glob** + **Read**: `05_management/02_analysis/*.md`（過去の振り返りシート）
- **Read**: `01_strategy/03_target/persona.md`（ペルソナ定義）
- **Glob** + **Read**: `01_strategy/02_goals/*.md`（前期の計画）
- **WebSearch**: コンテンツ領域のトレンド調査（オプション）

### Step 2: 方針策定

1. **Read** [strategy_sheet.md](strategy_sheet.md)（テンプレート）
2. ユーザーとの対話で以下を策定:
   - コンテンツの目的・ゴール
   - ターゲット読者の優先順位
   - 注力テーマ（カテゴリ）
   - KPI目標（月間投稿数、PV、スキ数など）
   - 差別化ポイント
3. **Write** `01_strategy/02_goals/YYYYMMDD_strategy.md`

### Step 3: カレンダー作成

1. 方針に基づいてコンテンツカレンダーを作成
2. **Write** `01_strategy/01_calendar/YYYYMMDD_calendar.md`
3. 月ごと・週ごとのテーマ配分を決める

### Step 4: レビュー＆承認

1. 計画をユーザーと確認
2. オプション: `/persona` スキルでテーマの妥当性を検証

---

## 更新サイクル

| タイミング | やること |
|-----------|---------|
| 四半期ごと | 中期計画シートの全面見直し |
| 月次 | コンテンツカレンダーの更新、KPI進捗確認 |
| 記事公開後 | Analysis からのフィードバックを確認 |

---

## 引数による分岐

- `new`: 新規計画を一から策定
- `update`: 既存計画をベースに更新（最新の計画を Glob で検索して Read）
- 引数なし: **AskUserQuestion** で新規/更新を確認

---

## AI制約

- Strategy はユーザーの意思決定を支援するフェーズ。AIはデータ整理・提案を行うが、最終決定はユーザーが行う
- KPI目標の数値はユーザーが設定する。AIが勝手に目標値を決めない

---

## 関連スキル

- `/analysis` — 振り返りデータのフィードバック元
- `/ideation` — 計画に基づくテーマ企画
- `/persona` — テーマ方針のペルソナ検証
