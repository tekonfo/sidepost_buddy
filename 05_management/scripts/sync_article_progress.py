#!/usr/bin/env python3
"""Sync minimal progress tracker CSV from 04_writing/01_draft."""

from __future__ import annotations

import csv
import datetime as dt
import re
from pathlib import Path


COLUMNS = [
    "article_id",
    "title",
    "status",
    "current_step",
    "updated_date",
    "next_action",
    "blocker",
    "draft_dir",
    "progress_file",
]

MANUAL_FIELDS = {"title", "next_action", "blocker"}

STEP_ORDER = ["0", "1", "2", "3", "4", "4a", "4b", "4.5", "5"]
REQUIRED_ORDER = ["0", "1", "2", "3", "4", "4.5", "5"]


def repo_root() -> Path:
    # /repo/05_management/scripts/sync_article_progress.py -> /repo
    return Path(__file__).resolve().parents[2]


def normalize_status_cell(raw: str) -> str:
    text = raw.strip()
    if not text:
        return "unknown"
    text = text.replace("**", "").replace("`", "").strip()
    if text.startswith("✅"):
        return "complete"
    if text.startswith("🔵"):
        return "in_progress"
    if text.startswith("⬜"):
        return "not_started"
    present = [name for icon, name in [("✅", "complete"), ("🔵", "in_progress"), ("⬜", "not_started")] if icon in text]
    if len(present) == 1:
        return present[0]
    return "unknown"


def parse_progress_table(progress_path: Path) -> dict[str, str]:
    states: dict[str, str] = {}
    if not progress_path.exists():
        return states

    for line in progress_path.read_text(encoding="utf-8").splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 5:
            continue
        code = cells[0]
        if code in {"#", "---"} or code.startswith("---"):
            continue
        if code not in {"0", "G1", "1", "2", "G2", "3", "4", "4a", "4b", "G3", "4.5", "5"}:
            continue
        states[code] = normalize_status_cell(cells[2])
    return states


def updated_date_from_job(job_dir: Path) -> str:
    file_times = [p.stat().st_mtime for p in job_dir.rglob("*") if p.is_file()]
    if file_times:
        return dt.date.fromtimestamp(max(file_times)).isoformat()
    return dt.date.fromtimestamp(job_dir.stat().st_mtime).isoformat()


def extract_title(job_dir: Path) -> str:
    step5 = job_dir / "step5_publish.md"
    if step5.exists():
        for line in step5.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^\|\s*タイトル\s*\|\s*(.*?)\s*\|$", line)
            if m:
                value = m.group(1).strip()
                if value and "<!--" not in value:
                    return value

    for candidate in [job_dir / "step3_writing.md", job_dir / "step2_design.md"]:
        if not candidate.exists():
            continue
        for line in candidate.read_text(encoding="utf-8").splitlines():
            if not line.startswith("# "):
                continue
            heading = line[2:].strip()
            if not heading or heading.startswith("Step "):
                continue
            if "<!--" in heading:
                continue
            return heading
    return ""


def derive_current_step(states: dict[str, str]) -> str:
    for step in STEP_ORDER:
        if states.get(step) == "in_progress":
            return step
    for step in REQUIRED_ORDER:
        if states.get(step) != "complete":
            return step
    return "done"


def derive_status(states: dict[str, str], current_step: str, has_progress: bool, has_any_step_file: bool) -> str:
    if not has_progress and not has_any_step_file:
        return "not_started"

    meaningful = any(state in {"in_progress", "complete"} for state in states.values())
    if has_progress and not meaningful:
        return "not_started"

    if current_step == "done":
        return "done"
    if current_step in {"0", "1", "2", "3"}:
        return "drafting"
    if current_step in {"4", "4a", "4b"}:
        return "reviewing"
    if current_step in {"4.5", "5"}:
        return "publish_prep"
    return "drafting"


def load_existing_rows(csv_path: Path) -> dict[str, dict[str, str]]:
    if not csv_path.exists():
        return {}
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        out: dict[str, dict[str, str]] = {}
        for row in reader:
            article_id = (row.get("article_id") or "").strip()
            if article_id:
                out[article_id] = row
        return out


def collect_rows(root: Path, existing: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    draft_root = root / "04_writing" / "01_draft"
    rows: list[dict[str, str]] = []

    if not draft_root.exists():
        return rows

    for job_dir in sorted([p for p in draft_root.iterdir() if p.is_dir() and not p.name.startswith(".")], key=lambda p: p.name, reverse=True):
        progress = job_dir / "progress.md"
        states = parse_progress_table(progress)
        current = derive_current_step(states) if states else ""

        has_any_step_file = any((job_dir / f"step{i}_memo.md").exists() for i in ["0"]) or any(
            (job_dir / name).exists()
            for name in [
                "step1_research.md",
                "step2_design.md",
                "step3_writing.md",
                "step4_review.md",
                "step4_review_round2.md",
                "step4_review_round3.md",
                "step5_publish.md",
            ]
        )

        status = derive_status(states, current, progress.exists(), has_any_step_file)
        existing_row = existing.get(job_dir.name, {})
        inferred_title = extract_title(job_dir)

        row = {col: "" for col in COLUMNS}
        row["article_id"] = job_dir.name
        row["title"] = existing_row.get("title", "").strip() or inferred_title
        row["status"] = status
        row["current_step"] = current
        row["updated_date"] = updated_date_from_job(job_dir)
        row["draft_dir"] = f"04_writing/01_draft/{job_dir.name}"
        row["progress_file"] = str(progress.relative_to(root)) if progress.exists() else ""

        for field in MANUAL_FIELDS:
            if field != "title":
                row[field] = existing_row.get(field, "").strip()

        rows.append(row)
    return rows


def write_rows(csv_path: Path, rows: list[dict[str, str]]) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({col: row.get(col, "") for col in COLUMNS})


def main() -> int:
    root = repo_root()
    csv_path = root / "05_management" / "01_progress" / "article_progress.csv"
    existing = load_existing_rows(csv_path)
    rows = collect_rows(root, existing)
    write_rows(csv_path, rows)
    print(f"Synced {len(rows)} rows -> {csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
