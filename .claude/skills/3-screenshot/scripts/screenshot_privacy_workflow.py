#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

Rect = Tuple[int, int, int, int]


def to_int(value: Any) -> int:
    if isinstance(value, (int, float)):
        return int(round(float(value)))
    if isinstance(value, str):
        return int(round(float(value.strip())))
    raise ValueError(f"Cannot convert value to int: {value!r}")


def parse_rect(value: Any) -> Rect:
    if isinstance(value, (list, tuple)) and len(value) == 4:
        return (to_int(value[0]), to_int(value[1]), to_int(value[2]), to_int(value[3]))

    if isinstance(value, dict):
        if "rect" in value:
            return parse_rect(value["rect"])
        if "bbox" in value:
            return parse_rect(value["bbox"])
        if "box" in value:
            return parse_rect(value["box"])
        if "coords" in value:
            return parse_rect(value["coords"])

        if all(key in value for key in ("x1", "y1", "x2", "y2")):
            return (
                to_int(value["x1"]),
                to_int(value["y1"]),
                to_int(value["x2"]),
                to_int(value["y2"]),
            )
        if all(key in value for key in ("left", "top", "right", "bottom")):
            return (
                to_int(value["left"]),
                to_int(value["top"]),
                to_int(value["right"]),
                to_int(value["bottom"]),
            )
        if all(key in value for key in ("x", "y", "width", "height")):
            x = to_int(value["x"])
            y = to_int(value["y"])
            width = to_int(value["width"])
            height = to_int(value["height"])
            return (x, y, x + width, y + height)
        if all(key in value for key in ("x", "y", "w", "h")):
            x = to_int(value["x"])
            y = to_int(value["y"])
            width = to_int(value["w"])
            height = to_int(value["h"])
            return (x, y, x + width, y + height)

    raise ValueError(f"Unsupported rect format: {value!r}")


def extract_json_payload(text: str) -> Any:
    text = text.strip()
    if not text:
        raise ValueError("Input text is empty.")

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    fenced_blocks = re.findall(r"```(?:json)?\s*([\s\S]*?)\s*```", text, flags=re.IGNORECASE)
    for block in fenced_blocks:
        candidate = block.strip()
        if not candidate:
            continue
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue

    decoder = json.JSONDecoder()
    for match in re.finditer(r"[\{\[]", text):
        snippet = text[match.start() :]
        try:
            parsed, _ = decoder.raw_decode(snippet)
            return parsed
        except json.JSONDecodeError:
            continue

    raise ValueError("Could not parse JSON payload from AI response.")


def transcript_from_payload(payload: Any) -> List[str]:
    if isinstance(payload, dict):
        if isinstance(payload.get("transcript_lines"), list):
            return [str(line) for line in payload["transcript_lines"] if str(line).strip()]
        if isinstance(payload.get("transcript"), str):
            return [line for line in payload["transcript"].splitlines() if line.strip()]
        if isinstance(payload.get("ocr_text"), str):
            return [line for line in payload["ocr_text"].splitlines() if line.strip()]
    return []


def region_candidates(payload: Any) -> Sequence[Any]:
    if isinstance(payload, dict):
        for key in ("sensitive_regions", "regions", "rects", "redactions"):
            value = payload.get(key)
            if isinstance(value, list):
                return value
    if isinstance(payload, list):
        return payload
    return []


def normalize_payload(payload: Any) -> Dict[str, Any]:
    transcript_lines = transcript_from_payload(payload)
    candidates = region_candidates(payload)

    regions: List[Dict[str, Any]] = []
    seen: set[Rect] = set()

    for item in candidates:
        try:
            rect = parse_rect(item)
        except ValueError:
            if isinstance(item, dict) and "rect" in item:
                rect = parse_rect(item["rect"])
            else:
                continue

        if rect in seen:
            continue
        seen.add(rect)

        reason = ""
        text = ""
        if isinstance(item, dict):
            reason = str(item.get("reason", "")).strip()
            text = str(item.get("text", "")).strip()

        regions.append(
            {
                "reason": reason,
                "text": text,
                "rect": [rect[0], rect[1], rect[2], rect[3]],
            }
        )

    return {
        "transcript_lines": transcript_lines,
        "sensitive_regions": regions,
    }


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def write_transcript(path: Path, lines: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Normalize AI vision output and optionally render highlight+redaction image."
    )
    parser.add_argument("--ai-response-in", required=True, help="Path to raw AI response text/markdown/json.")
    parser.add_argument("--normalized-json-out", required=True, help="Path to normalized sensitive_regions.json.")
    parser.add_argument("--transcript-out", help="Optional transcript text path.")

    parser.add_argument("--input-image", help="Input image path for render step.")
    parser.add_argument("--output-image", help="Output image path for render step.")
    parser.add_argument("--focus", help="Focus rect x1,y1,x2,y2 for render step.")
    parser.add_argument("--manual-redact", action="append", default=[], help="Extra rect x1,y1,x2,y2.")

    parser.add_argument("--normal-blur-radius", type=float, default=2.0)
    parser.add_argument("--redact-blur-radius", type=float, default=14.0)
    parser.add_argument("--redact-darken", type=float, default=0.35)
    parser.add_argument("--redact-margin", type=int, default=8)
    parser.add_argument("--border-width", type=int, default=5)

    parser.add_argument(
        "--renderer-script",
        default=str(Path(__file__).with_name("highlight_and_redact.py")),
        help="Path to highlight_and_redact.py",
    )
    return parser.parse_args()


def build_render_command(args: argparse.Namespace) -> List[str]:
    command = [
        sys.executable,
        str(args.renderer_script),
        "--input",
        str(args.input_image),
        "--output",
        str(args.output_image),
        "--focus",
        str(args.focus),
        "--disable-ocr",
        "--manual-redact-file",
        str(args.normalized_json_out),
        "--normal-blur-radius",
        str(args.normal_blur_radius),
        "--redact-blur-radius",
        str(args.redact_blur_radius),
        "--redact-darken",
        str(args.redact_darken),
        "--redact-margin",
        str(args.redact_margin),
        "--border-width",
        str(args.border_width),
    ]
    for rect in args.manual_redact:
        command.extend(["--manual-redact", rect])
    return command


def should_run_render(args: argparse.Namespace) -> bool:
    values = [args.input_image, args.output_image, args.focus]
    present = [value is not None for value in values]
    if any(present) and not all(present):
        raise ValueError("--input-image, --output-image, --focus must be provided together.")
    return all(present)


def main() -> None:
    args = parse_args()

    source_path = Path(args.ai_response_in)
    raw_text = source_path.read_text(encoding="utf-8")
    payload = extract_json_payload(raw_text)
    normalized = normalize_payload(payload)

    normalized_path = Path(args.normalized_json_out)
    write_json(normalized_path, normalized)
    print(f"normalized_json: {normalized_path}")
    print(f"regions: {len(normalized['sensitive_regions'])}")

    if args.transcript_out:
        transcript_path = Path(args.transcript_out)
        write_transcript(transcript_path, normalized["transcript_lines"])
        print(f"transcript: {transcript_path}")

    if should_run_render(args):
        command = build_render_command(args)
        subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
