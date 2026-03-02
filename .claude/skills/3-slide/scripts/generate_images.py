#!/usr/bin/env python3
"""Generate slide images from YAML spec using NanoBanana models."""

from __future__ import annotations

import argparse
import base64
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

try:
    import yaml
except ImportError as exc:  # pragma: no cover - runtime guard
    raise SystemExit(
        "Missing dependency: pyyaml. Install with "
        "`pip install -r .claude/skills/3-slide/scripts/requirements.txt`."
    ) from exc

MODEL_PRESETS = {
    "nanobanana": "gemini-2.5-flash-image",
    "nanobanana-pro": "gemini-3-pro-image-preview",
}

ASPECT_RATIOS = (
    "1:1",
    "3:4",
    "4:3",
    "9:16",
    "16:9",
)

IMAGE_SIZES = (
    "1K",
    "2K",
    "4K",
)

OUTPUT_MIME_TYPES = (
    "image/png",
    "image/jpeg",
    "image/webp",
)


@dataclass
class SlidePrompt:
    name: str
    prompt: str
    aspect_ratio: str
    image_size: str | None


def load_google_genai_modules() -> tuple[object, object]:
    try:
        from google import genai
        from google.genai import types
    except ImportError as exc:  # pragma: no cover - runtime guard
        raise SystemExit(
            "Missing dependency: google-genai. Install with "
            "`pip install -r .claude/skills/3-slide/scripts/requirements.txt`."
        ) from exc
    return genai, types


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate images with NanoBanana/NanoBanana Pro from a YAML file. "
            "By default it looks for "
            "<job_dir>/image_assets/slide_image_prompts.yaml."
        )
    )
    parser.add_argument(
        "--spec",
        type=Path,
        help="Path to YAML prompt spec file.",
    )
    parser.add_argument(
        "--job-dir",
        type=Path,
        help="Article output directory. If --spec is omitted, spec path is inferred.",
    )
    parser.add_argument(
        "--assets-dir-name",
        default="image_assets",
        help="Assets directory name under --job-dir (default: image_assets).",
    )
    parser.add_argument(
        "--spec-name",
        default="slide_image_prompts.yaml",
        help="YAML filename under assets directory (default: slide_image_prompts.yaml).",
    )
    parser.add_argument(
        "--preset",
        choices=sorted(MODEL_PRESETS.keys()),
        help="Override model preset in YAML.",
    )
    parser.add_argument(
        "--model",
        help="Direct model name override (highest priority).",
    )
    parser.add_argument(
        "--default-aspect-ratio",
        choices=ASPECT_RATIOS,
        default="16:9",
        help="Fallback aspect ratio when not defined in YAML (default: 16:9).",
    )
    parser.add_argument(
        "--default-image-size",
        choices=IMAGE_SIZES,
        help="Fallback image size when not defined in YAML.",
    )
    parser.add_argument(
        "--output-mime-type",
        choices=OUTPUT_MIME_TYPES,
        help=(
            "Preferred output MIME type for generated images. "
            "Example: image/png."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate YAML and print planned outputs without API calls.",
    )
    return parser.parse_args()


def get_api_key() -> str | None:
    return os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")


def is_vertex_client(client: object) -> bool:
    api_client = getattr(client, "_api_client", None)
    return bool(getattr(api_client, "vertexai", False))


def sanitize_slug(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9_-]+", "-", value)
    value = re.sub(r"-{2,}", "-", value)
    return value.strip("-_")


def format_prompt_yaml(value: object, indent: int = 0) -> list[str]:
    prefix = "  " * indent
    lines: list[str] = []

    if isinstance(value, dict):
        for key, nested in value.items():
            label = str(key).replace("_", " ").strip()
            if isinstance(nested, (dict, list)):
                lines.append(f"{prefix}{label}:")
                lines.extend(format_prompt_yaml(nested, indent + 1))
            else:
                scalar = str(nested).strip()
                if scalar:
                    lines.append(f"{prefix}{label}: {scalar}")
        return lines

    if isinstance(value, list):
        for item in value:
            if isinstance(item, (dict, list)):
                lines.append(f"{prefix}-")
                lines.extend(format_prompt_yaml(item, indent + 1))
            else:
                scalar = str(item).strip()
                if scalar:
                    lines.append(f"{prefix}- {scalar}")
        return lines

    scalar = str(value).strip()
    if scalar:
        lines.append(f"{prefix}{scalar}")
    return lines


def parse_prompt_value(raw_prompt: object, slide_index: int) -> str:
    if isinstance(raw_prompt, str):
        prompt = raw_prompt.strip()
        if prompt:
            return prompt
        raise ValueError(f"`slides[{slide_index}].prompt` is empty.")

    if isinstance(raw_prompt, (dict, list)):
        lines = format_prompt_yaml(raw_prompt)
        prompt = "\n".join(line for line in lines if line.strip())
        if prompt:
            return prompt
        raise ValueError(f"`slides[{slide_index}].prompt` has no usable content.")

    raise ValueError(
        f"`slides[{slide_index}].prompt` must be string/list/mapping."
    )


def resolve_spec_path(args: argparse.Namespace) -> Path:
    if args.spec:
        return args.spec
    if not args.job_dir:
        raise ValueError("Specify either --spec or --job-dir.")
    return args.job_dir / args.assets_dir_name / args.spec_name


def read_spec(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"YAML spec file not found: {path}")
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"YAML root must be a mapping: {path}")
    return loaded


def resolve_model_name(spec: dict, args: argparse.Namespace) -> str:
    if args.model:
        return args.model
    if spec.get("model"):
        return str(spec["model"]).strip()
    preset = args.preset or str(spec.get("model_preset", "nanobanana")).strip()
    if preset not in MODEL_PRESETS:
        raise ValueError(
            f"Unsupported model_preset: {preset}. "
            f"Use one of: {', '.join(sorted(MODEL_PRESETS))}"
        )
    return MODEL_PRESETS[preset]


def validate_aspect_ratio(value: str) -> str:
    ratio = str(value).strip()
    if ratio not in ASPECT_RATIOS:
        raise ValueError(
            f"Unsupported aspect_ratio: {ratio}. "
            f"Use one of: {', '.join(ASPECT_RATIOS)}"
        )
    return ratio


def validate_image_size(value: str | None) -> str | None:
    if value is None:
        return None
    size = str(value).strip().upper()
    if size not in IMAGE_SIZES:
        raise ValueError(
            f"Unsupported image_size: {size}. "
            f"Use one of: {', '.join(IMAGE_SIZES)}"
        )
    return size


def validate_output_mime_type(value: str | None) -> str | None:
    if value is None:
        return None
    mime_type = str(value).strip().lower()
    if mime_type not in OUTPUT_MIME_TYPES:
        raise ValueError(
            f"Unsupported output_mime_type: {mime_type}. "
            f"Use one of: {', '.join(OUTPUT_MIME_TYPES)}"
        )
    return mime_type


def resolve_default_aspect_ratio(spec: dict, args: argparse.Namespace) -> str:
    raw = spec.get("default_aspect_ratio")
    if raw:
        return validate_aspect_ratio(str(raw))
    return args.default_aspect_ratio


def resolve_default_image_size(spec: dict, args: argparse.Namespace) -> str | None:
    if args.default_image_size:
        return args.default_image_size
    raw = spec.get("default_image_size")
    if raw in (None, "", "null"):
        return None
    return validate_image_size(str(raw))


def resolve_output_mime_type(spec: dict, args: argparse.Namespace) -> str | None:
    if args.output_mime_type:
        return validate_output_mime_type(args.output_mime_type)
    raw = spec.get("default_output_mime_type")
    if raw in (None, "", "null"):
        return None
    return validate_output_mime_type(str(raw))


def parse_slides(
    spec: dict,
    default_aspect_ratio: str,
    default_image_size: str | None,
) -> list[SlidePrompt]:
    raw_slides = spec.get("slides")
    if not isinstance(raw_slides, list) or not raw_slides:
        raise ValueError("YAML must contain non-empty `slides` list.")

    rows: list[SlidePrompt] = []
    for index, raw in enumerate(raw_slides, start=1):
        if not isinstance(raw, dict):
            raise ValueError(f"`slides[{index}]` must be a mapping.")

        raw_name = str(raw.get("name", f"slide-{index:02d}"))
        name = sanitize_slug(raw_name) or f"slide-{index:02d}"

        if "prompt" not in raw:
            raise ValueError(f"`slides[{index}].prompt` is required.")
        prompt = parse_prompt_value(raw.get("prompt"), slide_index=index)

        raw_aspect = raw.get("aspect_ratio")
        aspect_ratio = (
            validate_aspect_ratio(str(raw_aspect))
            if raw_aspect not in (None, "")
            else default_aspect_ratio
        )

        raw_size = raw.get("image_size")
        image_size = (
            validate_image_size(str(raw_size))
            if raw_size not in (None, "")
            else default_image_size
        )

        rows.append(
            SlidePrompt(
                name=name,
                prompt=prompt,
                aspect_ratio=aspect_ratio,
                image_size=image_size,
            )
        )
    return rows


def build_config(
    types_module: object,
    aspect_ratio: str,
    image_size: str | None,
    output_mime_type: str | None,
) -> object:
    image_config_kwargs: dict[str, object] = {"aspect_ratio": aspect_ratio}
    if image_size:
        image_config_kwargs["image_size"] = image_size
    if output_mime_type:
        image_config_kwargs["output_mime_type"] = output_mime_type
    return types_module.GenerateContentConfig(
        response_modalities=["IMAGE"],
        image_config=types_module.ImageConfig(**image_config_kwargs),
    )


def get_parts(response: object) -> Iterable[object]:
    parts = getattr(response, "parts", None)
    if parts:
        return parts
    candidates = getattr(response, "candidates", None) or []
    if not candidates:
        return []
    content = getattr(candidates[0], "content", None)
    if not content:
        return []
    return getattr(content, "parts", None) or []


def extension_for_mime_type(mime_type: str) -> str:
    mapping = {
        "image/png": ".png",
        "image/jpeg": ".jpg",
        "image/webp": ".webp",
    }
    return mapping.get(mime_type.lower(), ".bin")


def extract_image_bytes(part: object) -> tuple[bytes, str] | None:
    inline_data = getattr(part, "inline_data", None)
    if not inline_data:
        return None
    mime_type = (getattr(inline_data, "mime_type", None) or "image/png").lower()
    data = getattr(inline_data, "data", None)
    if not data:
        return None
    if isinstance(data, str):
        return base64.b64decode(data), mime_type
    return data, mime_type


def reserve_output_path(out_dir: Path, base_name: str, ext: str) -> Path:
    candidate = out_dir / f"{base_name}{ext}"
    if not candidate.exists():
        return candidate

    for suffix in range(2, 10_000):
        renamed = out_dir / f"{base_name}_{suffix:02d}{ext}"
        if not renamed.exists():
            return renamed

    raise RuntimeError(
        "Could not reserve unique output filename after many attempts: "
        f"{base_name}{ext}"
    )


def save_images(response: object, out_dir: Path, base_prefix: str) -> list[Path]:
    saved_paths: list[Path] = []
    for index, part in enumerate(get_parts(response), start=1):
        image_result = extract_image_bytes(part)
        if not image_result:
            continue
        raw_bytes, mime_type = image_result
        ext = extension_for_mime_type(mime_type)
        out_base = f"{base_prefix}_{index:02d}"
        out_path = reserve_output_path(out_dir, out_base, ext)
        out_path.write_bytes(raw_bytes)
        saved_paths.append(out_path)
    return saved_paths


def main() -> int:
    args = parse_args()
    spec_path = resolve_spec_path(args)
    spec = read_spec(spec_path)

    model_name = resolve_model_name(spec, args)
    default_aspect_ratio = resolve_default_aspect_ratio(spec, args)
    default_image_size = resolve_default_image_size(spec, args)
    output_mime_type = resolve_output_mime_type(spec, args)
    slides = parse_slides(spec, default_aspect_ratio, default_image_size)

    assets_dir = spec_path.parent
    assets_dir.mkdir(parents=True, exist_ok=True)

    if args.dry_run:
        print(f"spec: {spec_path}")
        print(f"model: {model_name}")
        print(f"assets_dir: {assets_dir}")
        print(f"output_mime_type: {output_mime_type or 'model default'}")
        for index, slide in enumerate(slides, start=1):
            print(
                f"- [{index:02d}] name={slide.name} "
                f"aspect_ratio={slide.aspect_ratio} image_size={slide.image_size or 'default'}"
            )
        return 0

    genai, types_module = load_google_genai_modules()

    api_key = get_api_key()
    if not api_key:
        print(
            "API key not found. Set GEMINI_API_KEY or GOOGLE_API_KEY before running.",
            file=sys.stderr,
        )
        return 1

    client = genai.Client(api_key=api_key)
    effective_output_mime_type = output_mime_type
    if output_mime_type and not is_vertex_client(client):
        print(
            "warning: output_mime_type is not supported in Gemini API; "
            f"ignoring value ({output_mime_type}).",
            file=sys.stderr,
        )
        effective_output_mime_type = None

    total_saved = 0
    for index, slide in enumerate(slides, start=1):
        file_prefix = f"{index:02d}_{slide.name}"
        print(f"[{index}/{len(slides)}] generating: {file_prefix}")
        response = client.models.generate_content(
            model=model_name,
            contents=slide.prompt,
            config=build_config(
                types_module=types_module,
                aspect_ratio=slide.aspect_ratio,
                image_size=slide.image_size,
                output_mime_type=effective_output_mime_type,
            ),
        )
        saved_paths = save_images(response, assets_dir, file_prefix)
        if not saved_paths:
            print(f"  no image returned for: {file_prefix}", file=sys.stderr)
            continue
        for path in saved_paths:
            print(f"  saved: {path}")
        total_saved += len(saved_paths)

    print(f"done. total images saved: {total_saved}")
    return 0 if total_saved > 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
