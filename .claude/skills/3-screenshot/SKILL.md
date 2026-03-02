---
name: screenshot
description: "[Phase 3] スクリーンショットのプライバシー保護加工。注目範囲ハイライト＋機密情報ぼかし処理を実行"
argument-hint: "[画像パス]"
---

# スクリーンショット加工ワークフロー

スクリーンショットの注目範囲を赤枠でハイライトし、個人情報・機密情報を強ぼかしで不可読化する。

## いつ使うか

- 記事にスクリーンショットを使うとき
- 画面キャプチャのプライバシー保護が必要なとき

---

## 固定仕様

- 注目範囲（矩形）は通常ぼかししない
- 範囲外のみ `GaussianBlur` を適用（弱め）
- 赤枠色: `#FF0000`
- 通常ぼかし初期値: `normal_blur_radius=2.0`
- 機密強ぼかし初期値: `redact_blur_radius=14.0`
- 枠線初期値: `border_width=4`
- 座標: `left, top, right, bottom`（左上と右下）

---

## ワークフロー

### Step 1: AI で文字起こし＋機密領域抽出

1. **Read** 入力画像（Claude Code の画像読み取り機能で解析）
2. 文字起こし + 個人情報・機密情報の特定
3. **Write** 文字起こし: `screen_shot/ocr_transcript.md`
4. **Write** 機密領域JSON: `screen_shot/sensitive_regions.json`

JSON フォーマット:
```json
{
  "sensitive_regions": [
    {
      "reason": "why sensitive",
      "text": "detected text",
      "rect": [x1, y1, x2, y2]
    }
  ]
}
```

### Step 2: PIL で最終画像を生成

```bash
python3 .claude/skills/3-screenshot/scripts/highlight_and_redact.py \
  --input {入力画像パス} \
  --output {出力画像パス} \
  --focus {left},{top},{right},{bottom} \
  --disable-ocr \
  --manual-redact-file {sensitive_regions.json パス} \
  --normal-blur-radius 2.0 \
  --redact-blur-radius 14.0 \
  --redact-darken 0.35 \
  --redact-margin 8 \
  --border-width 5
```

または汎用ランナーで一括実行:

```bash
python3 .claude/skills/3-screenshot/scripts/screenshot_privacy_workflow.py \
  --ai-response-in {ai_response.md パス} \
  --normalized-json-out {sensitive_regions.json パス} \
  --transcript-out {ocr_transcript.md パス} \
  --input-image {入力画像パス} \
  --output-image {出力画像パス} \
  --focus {left},{top},{right},{bottom}
```

### Step 3: 漏れ確認

1. **Read** 出力画像を確認
2. 漏れがあれば `--manual-redact` で追加領域を指定して再実行

---

## 調整パラメータ

| パラメータ | デフォルト | 調整方法 |
|-----------|----------|---------|
| `--normal-blur-radius` | 2.0 | 外側ぼかしの強弱 |
| `--redact-blur-radius` | 14.0 | 機密ぼかしの強弱 |
| `--redact-darken` | 0.35 | 機密領域の暗さ |
| `--redact-margin` | 8 | 機密ぼかしの余白 |
| `--border-width` | 5 | 赤枠の太さ |

---

## 品質チェック

- 注目範囲は鮮明で赤枠が明確
- 注目範囲の外側は軽くぼけている
- 個人情報や機密情報が強ぼかしで読めない
- 画像解像度が変わっていない

---

## 関連スキル

- `/article` — 記事内でスクリーンショットを使う場合
