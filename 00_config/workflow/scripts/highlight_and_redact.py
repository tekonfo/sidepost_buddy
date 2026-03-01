#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from PIL import Image, ImageDraw, ImageFilter

Rect = Tuple[int, int, int, int]

DEFAULT_PATTERNS = [
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
    r"/Users/[^\s]+",
    r"AKIA[0-9A-Z]{16}",
    r"AIza[0-9A-Za-z\-_]{20,}",
    r"ghp_[A-Za-z0-9]{20,}",
    r"sk-[A-Za-z0-9]{16,}",
    r"(?i)\bpassword\b",
    r"(?i)\bapi[_-]?key\b",
    r"(?i)\bsecret\b",
    r"(?i)\btoken\b",
    r"(?i)\bbearer\b",
]

DEFAULT_KEYWORDS = [
    "password",
    "api key",
    "apikey",
    "secret",
    "token",
    "bearer",
    "private",
    "mail",
    "email",
    "phone",
    "address",
    "/users/",
]


def clamp(v: int, low: int, high: int) -> int:
    return max(low, min(v, high))


def parse_rect(value: str) -> Rect:
    parts = [p.strip() for p in value.split(",")]
    if len(parts) != 4:
        raise ValueError(f"Rect must have 4 values: {value}")
    x1, y1, x2, y2 = (int(p) for p in parts)
    return x1, y1, x2, y2


def parse_rect_obj(value: object) -> Rect:
    if isinstance(value, (list, tuple)) and len(value) == 4:
        x1, y1, x2, y2 = (int(v) for v in value)
        return x1, y1, x2, y2

    if isinstance(value, dict):
        if "rect" in value:
            return parse_rect_obj(value["rect"])
        keys = ("x1", "y1", "x2", "y2")
        if all(key in value for key in keys):
            return (
                int(value["x1"]),
                int(value["y1"]),
                int(value["x2"]),
                int(value["y2"]),
            )

    raise ValueError(f"Unsupported rect format: {value!r}")


def load_rects_from_json(path: Path) -> List[Rect]:
    data = json.loads(path.read_text(encoding="utf-8"))

    if isinstance(data, dict):
        if "sensitive_regions" in data:
            source = data["sensitive_regions"]
        elif "rects" in data:
            source = data["rects"]
        else:
            source = []
    elif isinstance(data, list):
        source = data
    else:
        source = []

    if not isinstance(source, list):
        raise ValueError("JSON root must be list, or dict.sensitive_regions / dict.rects must be list.")

    rects: List[Rect] = []
    for item in source:
        rects.append(parse_rect_obj(item))
    return rects


def clamp_rect(rect: Rect, width: int, height: int) -> Optional[Rect]:
    x1, y1, x2, y2 = rect
    x1 = clamp(x1, 0, width - 1)
    y1 = clamp(y1, 0, height - 1)
    x2 = clamp(x2, 1, width)
    y2 = clamp(y2, 1, height)
    if x1 >= x2 or y1 >= y2:
        return None
    return x1, y1, x2, y2


def expand_rect(rect: Rect, margin: int, width: int, height: int) -> Optional[Rect]:
    x1, y1, x2, y2 = rect
    return clamp_rect((x1 - margin, y1 - margin, x2 + margin, y2 + margin), width, height)


def rect_overlaps(a: Rect, b: Rect) -> bool:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    return not (ax2 < bx1 or bx2 < ax1 or ay2 < by1 or by2 < ay1)


def merge_rects(rects: Sequence[Rect]) -> List[Rect]:
    merged = list(rects)
    changed = True
    while changed:
        changed = False
        next_rects: List[Rect] = []
        while merged:
            base = merged.pop()
            i = 0
            while i < len(merged):
                other = merged[i]
                if rect_overlaps(base, other):
                    bx1, by1, bx2, by2 = base
                    ox1, oy1, ox2, oy2 = other
                    base = (min(bx1, ox1), min(by1, oy1), max(bx2, ox2), max(by2, oy2))
                    merged.pop(i)
                    changed = True
                else:
                    i += 1
            next_rects.append(base)
        merged = next_rects
    return merged


def compile_patterns(patterns: Iterable[str]) -> List[re.Pattern[str]]:
    compiled: List[re.Pattern[str]] = []
    for pattern in patterns:
        compiled.append(re.compile(pattern))
    return compiled


def is_sensitive(text: str, patterns: Sequence[re.Pattern[str]], keywords: Sequence[str]) -> bool:
    if not text:
        return False
    lowered = text.lower()
    if any(keyword in lowered for keyword in keywords):
        return True
    return any(pattern.search(text) for pattern in patterns)


def detect_sensitive_rects_with_ocr(
    image: Image.Image,
    ocr_lang: str,
    ocr_min_conf: float,
    patterns: Sequence[re.Pattern[str]],
    keywords: Sequence[str],
) -> Tuple[List[Rect], List[str], List[Dict[str, str]], Optional[str]]:
    try:
        import pytesseract
        from pytesseract import Output
    except ImportError:
        return [], [], [], "OCR skipped: pytesseract is not installed."

    try:
        data = pytesseract.image_to_data(image, lang=ocr_lang, output_type=Output.DICT)
    except Exception as exc:
        return [], [], [], f"OCR skipped: {exc}"

    line_map: Dict[Tuple[int, int, int], List[Dict[str, object]]] = {}
    rows_for_log: List[Dict[str, str]] = []
    token_count = len(data["text"])

    for i in range(token_count):
        raw_text = data["text"][i]
        text = raw_text.strip() if raw_text else ""
        if not text:
            continue

        conf_text = str(data["conf"][i])
        try:
            conf = float(conf_text)
        except ValueError:
            conf = -1.0
        if conf >= 0 and conf < ocr_min_conf:
            continue

        left = int(data["left"][i])
        top = int(data["top"][i])
        width = int(data["width"][i])
        height = int(data["height"][i])
        rect = (left, top, left + width, top + height)

        block = int(data["block_num"][i])
        paragraph = int(data["par_num"][i])
        line = int(data["line_num"][i])
        key = (block, paragraph, line)
        line_map.setdefault(key, []).append(
            {
                "text": text,
                "rect": rect,
                "conf": conf,
            }
        )

        rows_for_log.append(
            {
                "text": text,
                "conf": f"{conf:.2f}",
                "left": str(left),
                "top": str(top),
                "width": str(width),
                "height": str(height),
                "block": str(block),
                "paragraph": str(paragraph),
                "line": str(line),
            }
        )

    transcript_lines: List[str] = []
    sensitive_rects: List[Rect] = []

    for key in sorted(line_map.keys()):
        tokens = line_map[key]
        line_text = " ".join(str(token["text"]) for token in tokens)
        transcript_lines.append(line_text)

        token_sensitive = [token for token in tokens if is_sensitive(str(token["text"]), patterns, keywords)]
        line_sensitive = is_sensitive(line_text, patterns, keywords)

        if line_sensitive:
            rects = [token["rect"] for token in tokens]
            min_x1 = min(rect[0] for rect in rects)
            min_y1 = min(rect[1] for rect in rects)
            max_x2 = max(rect[2] for rect in rects)
            max_y2 = max(rect[3] for rect in rects)
            sensitive_rects.append((min_x1, min_y1, max_x2, max_y2))
            continue

        for token in token_sensitive:
            sensitive_rects.append(token["rect"])  # type: ignore[arg-type]

    return sensitive_rects, transcript_lines, rows_for_log, None


def save_text_file(path: Path, lines: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def save_tsv(path: Path, rows: Sequence[Dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = ["text", "conf", "left", "top", "width", "height", "block", "paragraph", "line"]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Highlight one area and redact sensitive text with strong blur.")
    parser.add_argument("--input", required=True, help="Input image path")
    parser.add_argument("--output", required=True, help="Output image path")
    parser.add_argument("--focus", required=True, help="Focus rect: x1,y1,x2,y2")
    parser.add_argument("--normal-blur-radius", type=float, default=2.0)
    parser.add_argument("--border-width", type=int, default=4)
    parser.add_argument("--redact-blur-radius", type=float, default=14.0)
    parser.add_argument("--redact-darken", type=float, default=0.35)
    parser.add_argument("--redact-margin", type=int, default=8)

    parser.add_argument("--disable-ocr", action="store_true")
    parser.add_argument("--ocr-lang", default="jpn+eng")
    parser.add_argument("--ocr-min-conf", type=float, default=35.0)
    parser.add_argument("--ocr-text-out", help="Optional OCR transcript output path")
    parser.add_argument("--ocr-tsv-out", help="Optional OCR token TSV output path")

    parser.add_argument("--manual-redact", action="append", default=[], help="Extra redaction rect x1,y1,x2,y2")
    parser.add_argument(
        "--manual-redact-file",
        action="append",
        default=[],
        help="JSON file containing redaction rects (supports keys: sensitive_regions or rects).",
    )
    parser.add_argument("--sensitive-pattern", action="append", default=[])
    parser.add_argument("--sensitive-keyword", action="append", default=[])
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    image = Image.open(args.input).convert("RGB")
    width, height = image.size

    focus_rect = clamp_rect(parse_rect(args.focus), width, height)
    if not focus_rect:
        raise ValueError(f"Invalid focus rect: {args.focus}")

    patterns = compile_patterns([*DEFAULT_PATTERNS, *args.sensitive_pattern])
    keywords = [keyword.lower() for keyword in [*DEFAULT_KEYWORDS, *args.sensitive_keyword]]

    redaction_rects: List[Rect] = []
    transcript_lines: List[str] = []
    tsv_rows: List[Dict[str, str]] = []
    ocr_warning: Optional[str] = None

    if not args.disable_ocr:
        detected_rects, transcript_lines, tsv_rows, ocr_warning = detect_sensitive_rects_with_ocr(
            image=image,
            ocr_lang=args.ocr_lang,
            ocr_min_conf=args.ocr_min_conf,
            patterns=patterns,
            keywords=keywords,
        )
        redaction_rects.extend(detected_rects)

    for value in args.manual_redact:
        rect = clamp_rect(parse_rect(value), width, height)
        if rect:
            redaction_rects.append(rect)

    for file_path in args.manual_redact_file:
        rects = load_rects_from_json(Path(file_path))
        for rect_value in rects:
            rect = clamp_rect(rect_value, width, height)
            if rect:
                redaction_rects.append(rect)

    expanded_rects: List[Rect] = []
    for rect in redaction_rects:
        expanded = expand_rect(rect, args.redact_margin, width, height)
        if expanded:
            expanded_rects.append(expanded)

    merged_rects = merge_rects(expanded_rects)

    normal_blur = image.filter(ImageFilter.GaussianBlur(radius=args.normal_blur_radius))
    result = normal_blur.copy()

    fx1, fy1, fx2, fy2 = focus_rect
    result.paste(image.crop((fx1, fy1, fx2, fy2)), (fx1, fy1))

    darken = max(0.0, min(args.redact_darken, 1.0))
    for x1, y1, x2, y2 in merged_rects:
        region = image.crop((x1, y1, x2, y2))
        strong = region.filter(ImageFilter.GaussianBlur(radius=args.redact_blur_radius))
        if darken > 0:
            mask = Image.new("RGB", strong.size, (0, 0, 0))
            strong = Image.blend(strong, mask, darken)
        result.paste(strong, (x1, y1))

    draw = ImageDraw.Draw(result)
    draw.rectangle((fx1, fy1, fx2, fy2), outline=(255, 0, 0), width=args.border_width)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.save(output_path)

    if args.ocr_text_out:
        save_text_file(Path(args.ocr_text_out), transcript_lines)
    if args.ocr_tsv_out:
        save_tsv(Path(args.ocr_tsv_out), tsv_rows)

    print(f"saved: {output_path}")
    print(f"focus_rect: {focus_rect}")
    print(f"redacted_rects: {len(merged_rects)}")
    if ocr_warning:
        print(ocr_warning)


if __name__ == "__main__":
    main()
