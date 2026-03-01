# スクリーンショット注目範囲ハイライト手順（PIL）

特定範囲を赤枠で囲み、それ以外を軽くぼかしつつ、個人情報や機密情報は強ぼかしで不可読化するための手順書。

この手順書では「OCR」を次の意味で使う。
- 第一選択: Gemini CLI / Codex / Claude Code の画像読取（VLM）
- 補助選択: `pytesseract` + `tesseract` のローカルOCR

## 1. ゴールと固定仕様

- 入力: 1枚のスクリーンショット画像（PNG/JPG）
- 出力: 注目範囲に赤枠、範囲外に軽ぼかし、機密箇所に強ぼかしを適用した画像
- 固定仕様:
  - 注目範囲（矩形）は通常ぼかししない
  - 範囲外のみ `GaussianBlur` を適用（弱め）
  - 赤枠色は `#FF0000`
  - 通常ぼかし初期値は `normal_blur_radius=2.0`
  - 機密強ぼかし初期値は `redact_blur_radius=14.0`
  - 枠線初期値は `border_width=4`

座標は `left, top, right, bottom`（左上と右下）で指定する。

## 2. 使うスクリプト

- `00_config/workflow/scripts/highlight_and_redact.py`
- `00_config/workflow/scripts/screenshot_privacy_workflow.py`（汎用ランナー）

このスクリプトで次を一括実行する。
- 注目範囲外の軽ぼかし
- 注目範囲の赤枠
- 機密領域の強ぼかし不可読化
- （任意）ローカルOCRによる自動検出

`screenshot_privacy_workflow.py` は次を1コマンドで実行できる。
- AI応答（JSON/Markdown）のパース
- `sensitive_regions.json` への正規化
- 文字起こしファイル出力
- `highlight_and_redact.py` を呼び出して最終画像生成

## 3. 標準フロー（AI画像読取ベース）

### Step 1: AIで文字起こし＋機密領域抽出

入力画像を Gemini CLI / Codex / Claude Code に渡し、下記フォーマットで出力させる。

#### AIへの指示テンプレート

```text
添付画像を読み取り、以下を実施してください。

1) 文字起こし（画面上の読める文字を行単位で）
2) 個人情報・機密情報・外部漏えいNG情報を抽出
3) それぞれの対象について、元画像ピクセル座標で矩形を返す

出力は必ずJSONで、以下の形式にしてください。
{
  "transcript_lines": ["..."],
  "sensitive_regions": [
    {
      "reason": "why sensitive",
      "text": "detected text",
      "rect": [x1, y1, x2, y2]
    }
  ]
}

注意:
- rect座標は必ず元画像のピクセル座標
- 分からない場合は推定でよいが、漏れ防止のため少し広めに取る
- JSON以外の文章は出さない
```

#### 保存先（規定）

- 文字起こし: `03_writing/01_draft/<job>/screen_shot/ocr_transcript.md`
- 機密領域JSON: `03_writing/01_draft/<job>/screen_shot/sensitive_regions.json`

`ocr_transcript.md` は `transcript_lines` を1行ずつ展開して保存する。

### Step 2: PILで最終画像を生成

AIが作った `sensitive_regions.json` を読み込み、機密領域を強ぼかしする。

```bash
python3 00_config/workflow/scripts/highlight_and_redact.py \
  --input 03_writing/01_draft/<job>/screen_shot/sample.png \
  --output 03_writing/01_draft/<job>/screen_shot/sample_highlight_redacted.png \
  --focus 1600,610,2990,1680 \
  --disable-ocr \
  --manual-redact-file 03_writing/01_draft/<job>/screen_shot/sensitive_regions.json \
  --normal-blur-radius 2.0 \
  --redact-blur-radius 14.0 \
  --redact-darken 0.35 \
  --redact-margin 8 \
  --border-width 5
```

または、汎用ランナーで Step1 + Step2 を一括実行してもよい。

```bash
python3 00_config/workflow/scripts/screenshot_privacy_workflow.py \
  --ai-response-in 03_writing/01_draft/<job>/screen_shot/ai_response.md \
  --normalized-json-out 03_writing/01_draft/<job>/screen_shot/sensitive_regions.json \
  --transcript-out 03_writing/01_draft/<job>/screen_shot/ocr_transcript.md \
  --input-image 03_writing/01_draft/<job>/screen_shot/sample.png \
  --output-image 03_writing/01_draft/<job>/screen_shot/sample_highlight_redacted.png \
  --focus 1600,610,2990,1680
```

### Step 3: 漏れ確認と再実行

漏れがあれば `--manual-redact` を追加して再実行する。

```bash
python3 00_config/workflow/scripts/highlight_and_redact.py \
  --input 03_writing/01_draft/<job>/screen_shot/sample.png \
  --output 03_writing/01_draft/<job>/screen_shot/sample_highlight_redacted_v2.png \
  --focus 1600,610,2990,1680 \
  --disable-ocr \
  --manual-redact-file 03_writing/01_draft/<job>/screen_shot/sensitive_regions.json \
  --manual-redact 2480,1525,2995,1660
```

## 4. JSONフォーマット仕様

`--manual-redact-file` は以下のいずれかを受け付ける。

- `{"sensitive_regions":[{"rect":[x1,y1,x2,y2]}, ...]}`
- `{"rects":[[x1,y1,x2,y2], ...]}`
- `[[x1,y1,x2,y2], ...]`

## 5. 補助フロー（ローカルOCRを使う場合）

AI画像読取が使えない場合だけ、`--disable-ocr` を外してローカルOCRを使う。

```bash
python3 00_config/workflow/scripts/highlight_and_redact.py \
  --input 03_writing/01_draft/<job>/screen_shot/sample.png \
  --output 03_writing/01_draft/<job>/screen_shot/sample_highlight_redacted_ocr.png \
  --focus 1600,610,2990,1680 \
  --ocr-lang jpn+eng \
  --ocr-text-out 03_writing/01_draft/<job>/screen_shot/ocr_transcript.txt \
  --ocr-tsv-out 03_writing/01_draft/<job>/screen_shot/ocr_tokens.tsv
```

## 6. 品質チェック

- 注目範囲は鮮明で赤枠が明確
- 注目範囲の外側は軽くぼけている
- 個人情報や機密情報が強ぼかしで読めない
- 画像解像度が変わっていない
- 出力ファイルが指定パスに保存されている

## 7. 調整ルール

- 外側ぼかしが強すぎる: `--normal-blur-radius` を下げる（例: `1.2`）
- 外側ぼかしが弱すぎる: `--normal-blur-radius` を上げる（例: `2.8`）
- 機密箇所がまだ読める: `--redact-blur-radius` を上げる（例: `18`）
- 機密箇所の縁が読める: `--redact-margin` を上げる（例: `12`）
- 注目範囲がズレる: `--focus` を再指定する
