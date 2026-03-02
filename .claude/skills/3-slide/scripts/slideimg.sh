#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../../.." && pwd)"
SKILL_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

WORK_DIR="${PROJECT_ROOT}"
OUTPUT_ROOT="${WORK_DIR}/04_writing/01_draft"
TEMPLATE_PATH="${SKILL_DIR}/prompt_templates/slide_image_prompts_00_rule_and_blank.yaml"
PY_SCRIPT="${SCRIPT_DIR}/generate_images.py"
REQ_FILE="${SCRIPT_DIR}/requirements.txt"
VENV_DIR="${WORK_DIR}/.venv"
PYTHON_BIN="${VENV_DIR}/bin/python"

usage() {
  cat <<'EOF'
Usage:
  slideimg init <job>
  slideimg dry  <job>
  slideimg run  <job>
  slideimg pro  <job>
  slideimg edit <job>
  slideimg path <job>

Examples:
  slideimg init 20260220_slide
  slideimg dry  20260220_slide
  slideimg run  20260220_slide
  slideimg pro  20260220_slide
EOF
}

job_dir_of() {
  local job="${1:-}"
  if [[ -z "${job}" ]]; then
    echo "job is required (example: 20260220_slide)" >&2
    exit 1
  fi
  printf '%s/%s' "${OUTPUT_ROOT}" "${job}"
}

spec_path_of() {
  local job_dir="${1}"
  printf '%s/image_assets/slide_image_prompts.yaml' "${job_dir}"
}

ensure_python() {
  if [[ -x "${PYTHON_BIN}" ]]; then
    return
  fi
  if ! command -v python3 >/dev/null 2>&1; then
    echo "python3 not found. Install Python 3 first." >&2
    exit 1
  fi
  python3 -m venv "${VENV_DIR}"
}

ensure_dependencies() {
  ensure_python
  if "${PYTHON_BIN}" - <<'PY' >/dev/null 2>&1
import yaml
from google import genai
PY
  then
    return
  fi
  "${PYTHON_BIN}" -m pip install -r "${REQ_FILE}"
}

ensure_api_key() {
  if [[ -n "${GEMINI_API_KEY:-}" || -n "${GOOGLE_API_KEY:-}" ]]; then
    return
  fi
  if ! command -v security >/dev/null 2>&1; then
    echo "Set GEMINI_API_KEY (or GOOGLE_API_KEY) before running." >&2
    exit 1
  fi
  local key
  if ! key="$(security find-generic-password -a "${USER}" -s GEMINI_API_KEY -w 2>/dev/null)"; then
    echo "API key not found in Keychain (service: GEMINI_API_KEY)." >&2
    echo "Either save it to Keychain or export GEMINI_API_KEY manually." >&2
    exit 1
  fi
  export GEMINI_API_KEY="${key}"
}

run_generator() {
  local job="${1}"
  shift
  ensure_dependencies
  "${PYTHON_BIN}" "${PY_SCRIPT}" --job-dir "$(job_dir_of "${job}")" "$@"
}

cmd_init() {
  local job="${1:-}"
  local job_dir
  job_dir="$(job_dir_of "${job}")"
  local spec_path
  spec_path="$(spec_path_of "${job_dir}")"

  mkdir -p "${job_dir}/image_assets"
  if [[ ! -f "${spec_path}" ]]; then
    cp "${TEMPLATE_PATH}" "${spec_path}"
  fi
  echo "${spec_path}"
}

cmd_edit() {
  local job="${1:-}"
  local spec_path
  spec_path="$(spec_path_of "$(job_dir_of "${job}")")"
  if [[ ! -f "${spec_path}" ]]; then
    echo "spec not found: ${spec_path}" >&2
    echo "Run: slideimg init ${job}" >&2
    exit 1
  fi
  "${EDITOR:-vi}" "${spec_path}"
}

cmd_path() {
  local job="${1:-}"
  job_dir_of "${job}"
}

main() {
  local cmd="${1:-help}"
  case "${cmd}" in
    init)
      shift
      cmd_init "${1:-}"
      ;;
    dry)
      shift
      run_generator "${1:-}" --dry-run
      ;;
    run)
      shift
      ensure_api_key
      run_generator "${1:-}"
      ;;
    pro)
      shift
      ensure_api_key
      run_generator "${1:-}" --preset nanobanana-pro --default-image-size 1K --output-mime-type image/png
      ;;
    edit)
      shift
      cmd_edit "${1:-}"
      ;;
    path)
      shift
      cmd_path "${1:-}"
      ;;
    help|-h|--help)
      usage
      ;;
    *)
      echo "unknown command: ${cmd}" >&2
      usage
      exit 1
      ;;
  esac
}

main "$@"
