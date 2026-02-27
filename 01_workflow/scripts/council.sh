#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

WORK_DIR="${PROJECT_ROOT}"
OUTPUT_ROOT="${WORK_DIR}/05_draft"
PROMPT_DIR="${WORK_DIR}/01_workflow/prompts/strategy_council"
DEFAULT_SESSION="sp-council"

usage() {
  cat <<'EOF'
Usage:
  council.sh start <job> [session]
  council.sh attach [session]
  council.sh ls
  council.sh stop [session]
  council.sh send <session> <pane(0-3)> <message|file>
  council.sh capture <session> <pane(0-3)> <output_file> [lines]

Examples:
  council.sh start 20260220_ai_plan
  council.sh send sp-council 0 01_workflow/prompts/strategy_council/orchestrator.md
  council.sh capture sp-council 2 /tmp/codex.log 400

Environment:
  COUNCIL_NO_ATTACH=1   Start session without attaching
EOF
}

die() {
  echo "$*" >&2
  exit 1
}

require_cmd() {
  local cmd="${1}"
  command -v "${cmd}" >/dev/null 2>&1 || die "required command not found: ${cmd}"
}

session_exists() {
  local session="${1}"
  tmux has-session -t "${session}" 2>/dev/null
}

ensure_session_exists() {
  local session="${1}"
  session_exists "${session}" || die "tmux session not found: ${session}"
}

validate_pane() {
  local pane="${1}"
  [[ "${pane}" =~ ^[0-3]$ ]] || die "pane must be 0, 1, 2, or 3: ${pane}"
}

pane_target() {
  local session="${1}"
  local pane="${2}"
  printf '%s:0.%s' "${session}" "${pane}"
}

attach_session() {
  local session="${1}"
  if [[ -n "${TMUX:-}" ]]; then
    tmux switch-client -t "${session}"
  else
    tmux attach-session -t "${session}"
  fi
}

init_job_dir() {
  local job="${1}"
  local job_dir="${OUTPUT_ROOT}/${job}"
  local council_dir="${job_dir}/strategy_council"

  mkdir -p "${council_dir}"

  if [[ ! -f "${council_dir}/agenda.md" ]]; then
    cat > "${council_dir}/agenda.md" <<EOF
# Strategy Council Agenda (${job})

## Goal
- step1_research.md と step2_design.md を作るための意思決定を行う

## Inputs
- ${job_dir}/step0_memo.md
- 02_concept/persona.md
- 02_concept/tone_manner.md

## Timebox
- Kickoff 5m
- Round1 15m
- Round2 15m
- Round3 10m
- Write-back 15m
EOF
  fi

  if [[ ! -f "${council_dir}/round_log.md" ]]; then
    cat > "${council_dir}/round_log.md" <<EOF
# Round Log (${job})

## Round 1

## Round 2

## Round 3
EOF
  fi

  if [[ ! -f "${council_dir}/consensus.md" ]]; then
    cat > "${council_dir}/consensus.md" <<EOF
# Consensus (${job})

| Topic | Decision | Reason | Owner | Due |
| --- | --- | --- | --- | --- |
EOF
  fi
}

boot_panes() {
  local session="${1}"
  local job="${2}"

  tmux send-keys -t "$(pane_target "${session}" 0)" "cd \"${WORK_DIR}\" && clear && echo '[pane0] orchestrator: claude' && echo 'job: ${job}' && claude" C-m
  tmux send-keys -t "$(pane_target "${session}" 1)" "cd \"${WORK_DIR}\" && clear && echo '[pane1] content strategist: claude' && claude" C-m
  tmux send-keys -t "$(pane_target "${session}" 2)" "cd \"${WORK_DIR}\" && clear && echo '[pane2] execution/risk: codex' && codex" C-m
  tmux send-keys -t "$(pane_target "${session}" 3)" "cd \"${WORK_DIR}\" && clear && echo '[pane3] market/distribution: gemini' && gemini" C-m
}

cmd_start() {
  local job="${1:-}"
  local session="${2:-${DEFAULT_SESSION}}"
  [[ -n "${job}" ]] || die "job is required (example: 20260220_ai_plan)"

  require_cmd tmux
  require_cmd claude
  require_cmd codex
  require_cmd gemini

  if session_exists "${session}"; then
    die "tmux session already exists: ${session}"
  fi

  init_job_dir "${job}"

  tmux new-session -d -s "${session}" -n "council" -c "${WORK_DIR}"
  tmux split-window -h -t "${session}:0" -c "${WORK_DIR}"
  tmux split-window -v -t "${session}:0.0" -c "${WORK_DIR}"
  tmux split-window -v -t "${session}:0.1" -c "${WORK_DIR}"
  tmux select-layout -t "${session}:0" tiled

  tmux select-pane -t "$(pane_target "${session}" 0)" -T "orchestrator"
  tmux select-pane -t "$(pane_target "${session}" 1)" -T "content-strategist"
  tmux select-pane -t "$(pane_target "${session}" 2)" -T "execution-risk"
  tmux select-pane -t "$(pane_target "${session}" 3)" -T "market-distribution"

  boot_panes "${session}" "${job}"

  echo "session: ${session}"
  echo "job: ${job}"
  echo "prompt dir: ${PROMPT_DIR}"
  echo "next command:"
  echo "  $(basename "$0") send ${session} 0 ${PROMPT_DIR}/orchestrator.md"

  if [[ "${COUNCIL_NO_ATTACH:-0}" == "1" ]]; then
    return
  fi
  attach_session "${session}"
}

cmd_attach() {
  local session="${1:-${DEFAULT_SESSION}}"
  ensure_session_exists "${session}"
  attach_session "${session}"
}

cmd_ls() {
  tmux list-sessions 2>/dev/null || true
}

cmd_stop() {
  local session="${1:-${DEFAULT_SESSION}}"
  ensure_session_exists "${session}"
  tmux kill-session -t "${session}"
}

cmd_send() {
  local session="${1:-}"
  local pane="${2:-}"
  shift 2 || true

  [[ -n "${session}" ]] || die "session is required"
  [[ -n "${pane}" ]] || die "pane is required"
  validate_pane "${pane}"
  ensure_session_exists "${session}"
  [[ "$#" -gt 0 ]] || die "message or file is required"

  local payload
  if [[ "$#" -eq 1 && -f "$1" ]]; then
    payload="$(cat "$1")"
  else
    payload="$*"
  fi

  printf '%s' "${payload}" | tmux load-buffer -
  tmux paste-buffer -t "$(pane_target "${session}" "${pane}")"
  tmux send-keys -t "$(pane_target "${session}" "${pane}")" C-m
}

cmd_capture() {
  local session="${1:-}"
  local pane="${2:-}"
  local output_file="${3:-}"
  local lines="${4:-300}"

  [[ -n "${session}" ]] || die "session is required"
  [[ -n "${pane}" ]] || die "pane is required"
  [[ -n "${output_file}" ]] || die "output_file is required"
  validate_pane "${pane}"
  ensure_session_exists "${session}"
  [[ "${lines}" =~ ^[0-9]+$ ]] || die "lines must be numeric: ${lines}"

  mkdir -p "$(dirname "${output_file}")"
  tmux capture-pane -p -S "-${lines}" -t "$(pane_target "${session}" "${pane}")" > "${output_file}"
  echo "saved: ${output_file}"
}

main() {
  local cmd="${1:-help}"
  case "${cmd}" in
    start)
      shift
      cmd_start "${1:-}" "${2:-}"
      ;;
    attach)
      shift
      cmd_attach "${1:-}"
      ;;
    ls)
      cmd_ls
      ;;
    stop)
      shift
      cmd_stop "${1:-}"
      ;;
    send)
      shift
      cmd_send "$@"
      ;;
    capture)
      shift
      cmd_capture "$@"
      ;;
    help|-h|--help)
      usage
      ;;
    *)
      die "unknown command: ${cmd}"
      ;;
  esac
}

main "$@"
