#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import re
from dataclasses import dataclass
from pathlib import Path


THEME_KW = ("テーマ", "記事", "ネタ", "タイトル", "topic", "title")
EPISODE_KW = (
    "やって",
    "試し",
    "失敗",
    "成功",
    "困っ",
    "改善",
    "実験",
    "体験",
    "気づ",
    "学び",
    "振り返",
)
FACT_KW = ("件", "回", "%", "円", "分", "時間", "日", "週", "月", "年", "kpi", "pv", "cv")
MESSAGE_KW = ("伝えたい", "結論", "教訓", "ポイント", "本質", "要点", "主張")
HEADING_KW = (
    "メモ",
    "アイデア",
    "気づき",
    "学び",
    "振り返り",
    "ふりかえり",
    "ログ",
    "日報",
    "today",
    "journal",
)
NOISE_PREFIX = ("http://", "https://", "[[", "```")


@dataclass(frozen=True)
class Candidate:
    category: str
    text: str
    source: Path
    line_no: int
    score: int
    date: dt.date | None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract article-ready items from markdown daily notes."
    )
    parser.add_argument("--daily-dir", required=True, help="Daily note directory path.")
    parser.add_argument("--out", required=True, help="Output markdown file path.")
    parser.add_argument("--days", type=int, default=14, help="Lookback days. Default: 14.")
    parser.add_argument(
        "--max-per-section",
        type=int,
        default=15,
        help="Maximum output items per section. Default: 15.",
    )
    parser.add_argument(
        "--today",
        help="Override today's date (YYYY-MM-DD). Useful for reproducible runs.",
    )
    return parser.parse_args()


def parse_date_from_text(text: str) -> dt.date | None:
    patterns = [
        re.compile(r"(?<!\d)(20\d{2})[-_](\d{2})[-_](\d{2})(?!\d)"),
        re.compile(r"(?<!\d)(20\d{2})/(\d{2})/(\d{2})(?!\d)"),
        re.compile(r"(?<!\d)(20\d{2})(\d{2})(\d{2})(?!\d)"),
    ]
    for pat in patterns:
        m = pat.search(text)
        if not m:
            continue
        try:
            return dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            return None
    return None


def parse_date_from_path(file_path: Path) -> dt.date | None:
    for target in (file_path.stem, file_path.name, str(file_path)):
        parsed = parse_date_from_text(target)
        if parsed is not None:
            return parsed
    return None


def normalize_key(text: str) -> str:
    lowered = text.lower()
    lowered = re.sub(r"\[[^\]]+\]\([^)]+\)", "", lowered)
    lowered = re.sub(r"[^0-9a-zA-Zぁ-んァ-ヶ一-龠]+", "", lowered)
    return lowered


def cleanup_text(text: str) -> str:
    cleaned = text.strip()
    cleaned = re.sub(r"\[[^\]]+\]\(([^)]+)\)", r"\1", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned


def detect_category(text: str, heading: str) -> str:
    merged = f"{heading} {text}".lower()
    if any(k in merged for k in THEME_KW):
        return "theme"
    if any(k in merged for k in MESSAGE_KW):
        return "message"
    if re.search(r"\d", text) or any(k in merged for k in FACT_KW):
        return "fact"
    if any(k in merged for k in EPISODE_KW):
        return "episode"
    return "episode"


def score_text(text: str, heading: str) -> int:
    score = 1
    merged = f"{heading} {text}".lower()

    if any(k in merged for k in EPISODE_KW):
        score += 2
    if re.search(r"\d", text):
        score += 1
    if any(k in merged for k in MESSAGE_KW):
        score += 1
    if any(k in heading.lower() for k in HEADING_KW):
        score += 1
    if len(text) >= 35:
        score += 1
    if len(text) < 10:
        score -= 1
    if text.lower().startswith(NOISE_PREFIX):
        score -= 3

    return score


def strip_frontmatter(lines: list[str]) -> list[str]:
    if len(lines) >= 3 and lines[0].strip() == "---":
        for idx in range(1, len(lines)):
            if lines[idx].strip() == "---":
                return lines[idx + 1 :]
    return lines


def select_files(daily_dir: Path, today: dt.date, days: int) -> tuple[list[Path], dt.date, dt.date]:
    start = today - dt.timedelta(days=max(days - 1, 0))
    all_md = sorted(daily_dir.rglob("*.md"))
    by_date: list[tuple[dt.date, Path]] = []
    undated: list[Path] = []

    for file_path in all_md:
        parsed = parse_date_from_path(file_path)
        if parsed is None:
            undated.append(file_path)
            continue
        if start <= parsed <= today:
            by_date.append((parsed, file_path))

    if by_date:
        selected = [p for _, p in sorted(by_date, key=lambda x: (x[0], x[1]), reverse=True)]
        return selected, start, today

    selected = sorted(undated, key=lambda p: p.stat().st_mtime, reverse=True)[: max(days * 2, 10)]
    return selected, start, today


def extract_candidates(file_path: Path) -> list[Candidate]:
    content = file_path.read_text(encoding="utf-8", errors="ignore")
    lines = strip_frontmatter(content.splitlines())

    heading = ""
    in_code_block = False
    date_hint = parse_date_from_path(file_path)
    candidates: list[Candidate] = []

    for idx, raw in enumerate(lines, start=1):
        line = raw.rstrip()
        stripped = line.strip()

        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block or not stripped:
            continue

        if stripped.startswith("#"):
            heading = stripped.lstrip("#").strip()
            continue

        bullet = re.match(r"^\s*(?:[-*+]|[0-9]+\.)\s+(.+)$", stripped)
        if bullet:
            text = cleanup_text(bullet.group(1))
        else:
            if len(stripped) < 15 or len(stripped) > 200:
                continue
            if not any(k in stripped.lower() for k in (THEME_KW + EPISODE_KW + FACT_KW + MESSAGE_KW)):
                continue
            text = cleanup_text(stripped)

        if not text or text.lower().startswith(NOISE_PREFIX):
            continue

        category = detect_category(text, heading)
        score = score_text(text, heading)
        if score <= 0:
            continue

        candidates.append(
            Candidate(
                category=category,
                text=text,
                source=file_path,
                line_no=idx,
                score=score,
                date=date_hint,
            )
        )

    return candidates


def dedupe_and_sort(candidates: list[Candidate]) -> list[Candidate]:
    unique: dict[str, Candidate] = {}
    for item in candidates:
        key = f"{item.category}:{normalize_key(item.text)}"
        prev = unique.get(key)
        if prev is None or (item.score, item.date or dt.date.min) > (prev.score, prev.date or dt.date.min):
            unique[key] = item

    return sorted(
        unique.values(),
        key=lambda x: (x.score, x.date or dt.date.min, str(x.source)),
        reverse=True,
    )


def section_title(category: str) -> str:
    return {
        "theme": "テーマ候補",
        "episode": "自分の体験・エピソード候補",
        "fact": "数字・事実候補",
        "message": "伝えたいこと候補",
    }[category]


def step0_title(category: str) -> str:
    return {
        "theme": "テーマ",
        "episode": "自分の体験・エピソード",
        "fact": "数字・事実",
        "message": "伝えたいこと",
    }[category]


def format_output(
    grouped: dict[str, list[Candidate]],
    out_path: Path,
    daily_dir: Path,
    start: dt.date,
    end: dt.date,
    file_count: int,
    max_per_section: int,
) -> str:
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    lines: list[str] = []

    lines.append("# 記事素材候補（デイリーノート抽出）")
    lines.append("")
    lines.append(f"- 生成日時: {now}")
    lines.append(f"- 対象ディレクトリ: {daily_dir}")
    lines.append(f"- 対象期間: {start.isoformat()} 〜 {end.isoformat()}")
    lines.append(f"- 読み込みファイル数: {file_count}")
    lines.append("")

    for category in ("theme", "episode", "fact", "message"):
        lines.append(f"## {section_title(category)}")
        items = grouped.get(category, [])[:max_per_section]
        if not items:
            lines.append("- 該当なし")
            lines.append("")
            continue
        for item in items:
            rel = item.source
            try:
                rel = item.source.relative_to(daily_dir)
            except ValueError:
                rel = item.source
            date_label = item.date.isoformat() if item.date else "unknown-date"
            lines.append(f"- {item.text}")
            lines.append(f"  - source: `{rel}:{item.line_no}` ({date_label}, score={item.score})")
        lines.append("")

    lines.append("## Step0転記用ドラフト")
    lines.append("以下は抽出結果をそのまま整理した下書き。必要項目のみ選んで step0 に転記する。")
    lines.append("")
    for category in ("theme", "episode", "fact", "message"):
        lines.append(f"### {step0_title(category)}")
        items = grouped.get(category, [])[:max_per_section]
        if not items:
            lines.append("- （該当なし）")
            lines.append("")
            continue
        for item in items:
            lines.append(f"- {item.text}")
        lines.append("")

    lines.append("## 注意")
    lines.append("- 元のデイリーノート内容を改変せず、事実のみを採用する。")
    lines.append("- 不確かな記述は step0 へ転記時に「未確認」と明記する。")
    lines.append("")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    text = "\n".join(lines).rstrip() + "\n"
    out_path.write_text(text, encoding="utf-8")
    return text


def main() -> int:
    args = parse_args()

    daily_dir = Path(args.daily_dir).expanduser().resolve()
    if not daily_dir.exists() or not daily_dir.is_dir():
        raise SystemExit(f"daily-dir not found or not a directory: {daily_dir}")

    out_path = Path(args.out).expanduser().resolve()
    today = dt.date.fromisoformat(args.today) if args.today else dt.date.today()
    selected_files, start, end = select_files(daily_dir, today, args.days)
    if not selected_files:
        raise SystemExit("No markdown files found under the given daily-dir.")

    all_candidates: list[Candidate] = []
    for file_path in selected_files:
        all_candidates.extend(extract_candidates(file_path))

    sorted_candidates = dedupe_and_sort(all_candidates)
    grouped: dict[str, list[Candidate]] = {"theme": [], "episode": [], "fact": [], "message": []}
    for item in sorted_candidates:
        grouped[item.category].append(item)

    format_output(
        grouped=grouped,
        out_path=out_path,
        daily_dir=daily_dir,
        start=start,
        end=end,
        file_count=len(selected_files),
        max_per_section=max(args.max_per_section, 1),
    )

    print(f"Wrote: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
