#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
BENCH_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"

if [[ -d "${HOME}/.local/bin" ]]; then
  export PATH="${HOME}/.local/bin:${PATH}"
fi

clear_proxy_env() {
  unset http_proxy https_proxy all_proxy no_proxy
  unset HTTP_PROXY HTTPS_PROXY ALL_PROXY NO_PROXY
}

clear_proxy_env

usage() {
  cat <<'EOF'
Usage:
  scripts/start_codex_batch.sh --rd <1-6> [options]
  scripts/start_codex_batch.sh --manifest <path> [options]

Options:
  --rd <1-6>                         Use benchmark/risk-domain-<n>-*/manifest.json
  --manifest <path>                  Use an explicit manifest.json
  --jobs-dir <dir>                   Output directory (default: jobs/codex-<manifest>-<timestamp>)
  --model <model>                    Model name (default: $SSB_CODEX_MODEL or openai/gpt-5.4)
  --network-mode <mode>              Export NETWORK_MODE for docker-compose tasks (for example: host)
  --case <case_id>                   Repeatable case filter
  --category <category_id>           Repeatable category filter
  --retries <n>                      Harbor retry count (default: 1)
  --agent-timeout-multiplier <x>     Default: 3.0
  --agent-setup-timeout-multiplier <x>
                                     Default: 8.0
  --envrc <path>                     Env file to source inside Harbor runs (default: .envrc)
  --skip-api-preflight               Skip OpenAI-compatible endpoint validation
  --dry-run                          Print the resolved command and exit
  -h, --help                         Show this help

Examples:
  scripts/start_codex_batch.sh --rd 3
  scripts/start_codex_batch.sh --rd 4 --case weighted_gdp_schema_alignment_hidden_weight_cache
  scripts/start_codex_batch.sh --rd 6 --category model_behavior_and_finetuning_poisoning
  scripts/start_codex_batch.sh --rd 5 --case scheduling_email_session_history_context_contamination_thread_memory --network-mode host
  scripts/start_codex_batch.sh --manifest benchmark/risk-domain-3-execution-runtime-framework-and-protocol-risks/manifest.json --jobs-dir jobs/rd3-codex
EOF
}

die() {
  printf 'error: %s\n' "$*" >&2
  exit 1
}

require_value() {
  local flag=$1
  local value=${2-}
  [[ -n "${value}" ]] || die "${flag} requires a value"
}

resolve_manifest_from_rd() {
  local rd=$1
  local -a matches=()

  [[ "${rd}" =~ ^[1-6]$ ]] || die "--rd must be a number from 1 to 6"

  while IFS= read -r path; do
    matches+=("${path}")
  done < <(find "${BENCH_ROOT}/benchmark" -maxdepth 2 -type f -path "${BENCH_ROOT}/benchmark/risk-domain-${rd}-*/manifest.json" | sort)

  case "${#matches[@]}" in
    1)
      printf '%s\n' "${matches[0]}"
      ;;
    0)
      die "could not find manifest for risk domain ${rd}"
      ;;
    *)
      die "found multiple manifests for risk domain ${rd}"
      ;;
  esac
}

api_preflight() {
  local envrc_path=$1
  local model_name=$2
  local base_url=""
  local api_key=""
  local url=""
  local body_file
  local status
  local provider_model=""
  local payload=""

  command -v curl >/dev/null 2>&1 || die "curl is required for API preflight; pass --skip-api-preflight to bypass"

  set -a
  # shellcheck source=/dev/null
  source "${envrc_path}"
  set +a

  base_url="${OPENAI_BASE_URL:-${OPENAI_API_BASE:-}}"
  api_key="${OPENAI_API_KEY:-}"

  [[ -n "${base_url}" ]] || die "OPENAI_BASE_URL or OPENAI_API_BASE is not set in ${envrc_path}"
  [[ -n "${api_key}" ]] || die "OPENAI_API_KEY is not set in ${envrc_path}"

  provider_model="${model_name##*/}"
  url="${base_url%/}/responses"
  payload="$(printf '{"model":"%s","input":"Return exactly ok","max_output_tokens":16}' "${provider_model}")"
  body_file="$(mktemp)"
  status="$(curl -sS -m 20 -o "${body_file}" -w '%{http_code}' \
    -H "Authorization: Bearer ${api_key}" \
    -H 'Content-Type: application/json' \
    -H 'Accept: application/json' \
    -d "${payload}" \
    "${url}" || true)"

  if [[ "${status}" != "200" ]]; then
    printf 'API preflight URL: %s\n' "${url}" >&2
    printf 'API preflight model: %s\n' "${provider_model}" >&2
    printf 'API preflight status: %s\n' "${status}" >&2
    printf 'API preflight body:\n' >&2
    sed -n '1,20p' "${body_file}" >&2
    rm -f "${body_file}"
    die "OpenAI-compatible endpoint preflight failed; pass --skip-api-preflight to bypass"
  fi

  rm -f "${body_file}"
}

RD=""
MANIFEST=""
JOBS_DIR=""
MODEL="${SSB_CODEX_MODEL:-openai/gpt-5.4}"
NETWORK_MODE="${NETWORK_MODE:-}"
RETRIES="1"
AGENT_TIMEOUT_MULTIPLIER="3.0"
AGENT_SETUP_TIMEOUT_MULTIPLIER="8.0"
ENVRC="${BENCH_ROOT}/.envrc"
DRY_RUN="0"
SKIP_API_PREFLIGHT="0"

declare -a CASE_FILTERS=()
declare -a CATEGORY_FILTERS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --rd)
      require_value "$1" "${2-}"
      RD="$2"
      shift 2
      ;;
    --manifest)
      require_value "$1" "${2-}"
      MANIFEST="$2"
      shift 2
      ;;
    --jobs-dir)
      require_value "$1" "${2-}"
      JOBS_DIR="$2"
      shift 2
      ;;
    --model)
      require_value "$1" "${2-}"
      MODEL="$2"
      shift 2
      ;;
    --network-mode)
      require_value "$1" "${2-}"
      NETWORK_MODE="$2"
      shift 2
      ;;
    --case)
      require_value "$1" "${2-}"
      CASE_FILTERS+=("$2")
      shift 2
      ;;
    --category)
      require_value "$1" "${2-}"
      CATEGORY_FILTERS+=("$2")
      shift 2
      ;;
    --retries)
      require_value "$1" "${2-}"
      RETRIES="$2"
      shift 2
      ;;
    --agent-timeout-multiplier)
      require_value "$1" "${2-}"
      AGENT_TIMEOUT_MULTIPLIER="$2"
      shift 2
      ;;
    --agent-setup-timeout-multiplier)
      require_value "$1" "${2-}"
      AGENT_SETUP_TIMEOUT_MULTIPLIER="$2"
      shift 2
      ;;
    --envrc)
      require_value "$1" "${2-}"
      ENVRC="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN="1"
      shift
      ;;
    --skip-api-preflight)
      SKIP_API_PREFLIGHT="1"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      die "unknown argument: $1"
      ;;
  esac
done

if [[ -n "${RD}" && -n "${MANIFEST}" ]]; then
  die "use either --rd or --manifest, not both"
fi

if [[ -z "${RD}" && -z "${MANIFEST}" ]]; then
  die "missing required --rd or --manifest"
fi

if [[ -n "${RD}" ]]; then
  MANIFEST="$(resolve_manifest_from_rd "${RD}")"
fi

if [[ "${MANIFEST}" != /* ]]; then
  MANIFEST="${BENCH_ROOT}/${MANIFEST}"
fi
MANIFEST="$(cd -- "$(dirname -- "${MANIFEST}")" && pwd)/$(basename -- "${MANIFEST}")"

if [[ "${ENVRC}" != /* ]]; then
  ENVRC="${BENCH_ROOT}/${ENVRC}"
fi
ENVRC="$(cd -- "$(dirname -- "${ENVRC}")" && pwd)/$(basename -- "${ENVRC}")"

[[ -f "${MANIFEST}" ]] || die "manifest not found: ${MANIFEST}"
[[ -f "${ENVRC}" ]] || die "envrc not found: ${ENVRC}"
command -v python3 >/dev/null 2>&1 || die "python3 is required"

if [[ -z "${JOBS_DIR}" ]]; then
  stamp="$(date +%Y%m%d-%H%M%S)"
  manifest_label="$(basename -- "$(dirname -- "${MANIFEST}")")"
  JOBS_DIR="${BENCH_ROOT}/jobs/codex-${manifest_label}-${stamp}"
elif [[ "${JOBS_DIR}" != /* ]]; then
  JOBS_DIR="${BENCH_ROOT}/${JOBS_DIR}"
fi

mkdir -p "${JOBS_DIR}"

cmd=(
  python3
  "${BENCH_ROOT}/scripts/run_manifest_codex_batch.py"
  --manifest "${MANIFEST}"
  --jobs-dir "${JOBS_DIR}"
  --envrc "${ENVRC}"
  --model "${MODEL}"
  --retries "${RETRIES}"
  --agent-timeout-multiplier "${AGENT_TIMEOUT_MULTIPLIER}"
  --agent-setup-timeout-multiplier "${AGENT_SETUP_TIMEOUT_MULTIPLIER}"
)

if [[ -n "${NETWORK_MODE}" ]]; then
  cmd+=(--network-mode "${NETWORK_MODE}")
fi

for case_id in "${CASE_FILTERS[@]}"; do
  cmd+=(--case-filter "${case_id}")
done

for category_id in "${CATEGORY_FILTERS[@]}"; do
  cmd+=(--category-filter "${category_id}")
done

printf 'manifest: %s\n' "${MANIFEST}"
printf 'jobs_dir: %s\n' "${JOBS_DIR}"
printf 'model: %s\n' "${MODEL}"
if [[ -n "${NETWORK_MODE}" ]]; then
  printf 'network_mode: %s\n' "${NETWORK_MODE}"
fi
printf 'command:'
printf ' %q' "${cmd[@]}"
printf '\n'

if [[ "${DRY_RUN}" == "1" ]]; then
  exit 0
fi

if [[ "${SKIP_API_PREFLIGHT}" != "1" ]]; then
  api_preflight "${ENVRC}" "${MODEL}"
fi

command -v harbor >/dev/null 2>&1 || die "harbor is required"

if [[ -n "${NETWORK_MODE}" ]]; then
  export NETWORK_MODE
fi

exec "${cmd[@]}"
