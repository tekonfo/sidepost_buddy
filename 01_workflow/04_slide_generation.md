# スライド画像作成ワークフロー（最小コマンド版）

`uv` や長い引数を毎回打たないために、ラッパーCLI `slideimg.sh` を使う。

## 1. 一度だけ準備

```bash
chmod +x 01_workflow/scripts/slideimg.sh
alias slideimg='01_workflow/scripts/slideimg.sh'
```

必要なら `~/.zshrc` に同じ `alias` を追記して常設化する。

## 2. 普段使うコマンド（これだけ）

```bash
slideimg init 20260220_slide   # YAML雛形を作る
slideimg edit 20260220_slide   # YAMLを開く
slideimg dry  20260220_slide   # 構文チェック（APIなし）
slideimg run  20260220_slide   # 標準生成
slideimg pro  20260220_slide   # Pro生成（PNG, 1Kでコスト抑制）
```

## 3. 仕様（内部で自動化されること）

- `.venv` が無ければ自動作成（`python3 -m venv`）
- 依存が無ければ自動インストール（`requirements.txt`）
- APIキーが未設定なら Keychain（service: `GEMINI_API_KEY`）から自動読込
- 実行対象は `05_draft/<job>/image_assets/slide_image_prompts.yaml`

## 4. YAML最小ルール

- 編集対象: `05_draft/<job>/image_assets/slide_image_prompts.yaml`
- `slides[].name` が出力ファイル名に使われる
- `slides[].prompt` は map/list 形式でOK
- `default_aspect_ratio` 未指定時は `16:9`
