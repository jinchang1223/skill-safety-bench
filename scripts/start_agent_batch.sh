#!/usr/bin/env bash
set -euo pipefail

ORIGINAL_SCRIPT_PATH="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/$(basename -- "${BASH_SOURCE[0]}")"

# Run from an immutable snapshot so long-running batches are not corrupted if the
# launcher is edited while they are still executing.
if [[ "${SSB_START_AGENT_BATCH_SNAPSHOT:-0}" != "1" ]]; then
  SNAPSHOT_TMPDIR="${TMPDIR:-/tmp}/ssb-start-agent-batch"
  mkdir -p "${SNAPSHOT_TMPDIR}"
  SNAPSHOT_PATH="$(mktemp "${SNAPSHOT_TMPDIR}/start_agent_batch.XXXXXX.sh")"
  cp -- "${BASH_SOURCE[0]}" "${SNAPSHOT_PATH}"
  chmod +x "${SNAPSHOT_PATH}"
  export SSB_START_AGENT_BATCH_SNAPSHOT=1
  export SSB_START_AGENT_BATCH_SNAPSHOT_PATH="${SNAPSHOT_PATH}"
  export SSB_START_AGENT_BATCH_ORIGINAL_PATH="${ORIGINAL_SCRIPT_PATH}"
  exec bash "${SNAPSHOT_PATH}" "$@"
fi

if [[ -n "${SSB_START_AGENT_BATCH_SNAPSHOT_PATH:-}" ]]; then
  trap 'rm -f -- "${SSB_START_AGENT_BATCH_SNAPSHOT_PATH}"' EXIT
fi

SCRIPT_SOURCE="${SSB_START_AGENT_BATCH_ORIGINAL_PATH:-${ORIGINAL_SCRIPT_PATH}}"
SCRIPT_DIR="$(cd -- "$(dirname -- "${SCRIPT_SOURCE}")" && pwd)"
BENCH_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"

if [[ -d "${HOME}/.local/bin" ]]; then
  export PATH="${HOME}/.local/bin:${PATH}"
fi

if [[ -n "${SSB_HARBOR_SHIM_DIR:-}" && -d "${SSB_HARBOR_SHIM_DIR}" ]]; then
  export PATH="${SSB_HARBOR_SHIM_DIR}:${PATH}"
fi

clear_proxy_env() {
  if [[ "${SSB_KEEP_PROXY_ENV:-0}" == "1" || "${SSB_PRESERVE_PROXY_ENV:-0}" == "1" ]]; then
    return 0
  fi
  unset http_proxy https_proxy all_proxy no_proxy
  unset HTTP_PROXY HTTPS_PROXY ALL_PROXY NO_PROXY
}

clear_proxy_env

ensure_anthropic_pdf_compat_proxy() {
  local envrc_path=$1
  local enabled=""
  local upstream=""
  local port=""
  local bind_host=""
  local max_text_chars=""
  local health_url=""
  local health_body=""
  local state_dir=""
  local pid_file=""
  local log_file=""
  local pid=""
  local script_path="${BENCH_ROOT}/scripts/anthropic_pdf_compat_proxy.py"

  set -a
  # shellcheck source=/dev/null
  source "${envrc_path}"
  set +a

  enabled="${SSB_ANTHROPIC_PDF_COMPAT_PROXY_ENABLED:-0}"
  [[ "${enabled}" == "1" ]] || return 0

  command -v curl >/dev/null 2>&1 || die "curl is required for the anthropic PDF compatibility proxy"
  [[ -f "${script_path}" ]] || die "missing proxy script: ${script_path}"

  upstream="${SSB_ANTHROPIC_PDF_COMPAT_PROXY_UPSTREAM_BASE_URL:-}"
  port="${SSB_ANTHROPIC_PDF_COMPAT_PROXY_PORT:-8799}"
  bind_host="${SSB_ANTHROPIC_PDF_COMPAT_PROXY_BIND_HOST:-0.0.0.0}"
  max_text_chars="${SSB_ANTHROPIC_PDF_COMPAT_MAX_CHARS:-200000}"
  [[ -n "${upstream}" ]] || die "SSB_ANTHROPIC_PDF_COMPAT_PROXY_UPSTREAM_BASE_URL is required when enabling the anthropic PDF compatibility proxy"

  health_url="http://127.0.0.1:${port}/__healthz"
  if health_body="$(curl -fsS --max-time 2 "${health_url}" 2>/dev/null || true)"; then
    if [[ "${health_body}" == *"\"upstream_base_url\": \"${upstream}\""* ]]; then
      printf '[info] using existing anthropic PDF compatibility proxy on port %s\n' "${port}" >&2
      return 0
    fi
  fi

  state_dir="${BENCH_ROOT}/.runtime/anthropic-pdf-compat-proxy"
  mkdir -p "${state_dir}"
  pid_file="${state_dir}/proxy-${port}.pid"
  log_file="${state_dir}/proxy-${port}.log"

  if [[ -f "${pid_file}" ]]; then
    pid="$(cat "${pid_file}" 2>/dev/null || true)"
    if [[ -n "${pid}" ]] && kill -0 "${pid}" 2>/dev/null; then
      kill "${pid}" 2>/dev/null || true
      sleep 0.5
    fi
    rm -f "${pid_file}"
  fi

  nohup python3 "${script_path}" \
    --listen-host "${bind_host}" \
    --listen-port "${port}" \
    --upstream-base-url "${upstream}" \
    --max-text-chars "${max_text_chars}" \
    --log-file "${log_file}" \
    >/dev/null 2>&1 &
  pid=$!
  printf '%s\n' "${pid}" > "${pid_file}"

  for _ in $(seq 1 40); do
    if curl -fsS --max-time 2 "${health_url}" >/dev/null 2>&1; then
      printf '[info] started anthropic PDF compatibility proxy on port %s\n' "${port}" >&2
      return 0
    fi
    sleep 0.25
  done

  if [[ -f "${log_file}" ]]; then
    printf 'anthropic PDF compatibility proxy log tail:\n' >&2
    tail -n 20 "${log_file}" >&2 || true
  fi
  die "failed to start anthropic PDF compatibility proxy on port ${port}"
}

usage() {
  cat <<'EOF'
Usage:
  scripts/start_agent_batch.sh --rd <1-6> [options]
  scripts/start_agent_batch.sh --manifest <path> [options]

Options:
  --rd <1-6>                         Use benchmark/risk-domain-<n>-*/manifest.json
  --manifest <path>                  Use an explicit manifest.json
  --agent <name>                     Harbor agent name (default: $SSB_AGENT or codex)
  --agent-import-path <module:Class> Custom Harbor agent import path
  --environment-import-path <module:Class>
                                     Custom Harbor environment import path
  --jobs-dir <dir>                   Output directory (default: jobs/<agent>-<manifest>-<timestamp>)
  --model <model>                    Model name (default: env-driven; omitted if unset)
  --reasoning-effort <level>         Agent reasoning effort, passed as Harbor agent kwarg
  --agent-kwarg <key=value>          Repeatable Harbor agent kwarg, for example
                                     prompt_template_path=prompts/codex_env_skills_prompt.j2
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

Behavior:
  Runs the selected cases one by one. After each case finishes, replay
  eval/verify_attack.py for that case and refresh jobs_dir summaries.

Examples:
  scripts/start_agent_batch.sh --rd 3
  scripts/start_agent_batch.sh --rd 3 --agent claude-code --model claude-3-7-sonnet-20250219
  scripts/start_agent_batch.sh --rd 4 --case weighted_gdp_schema_alignment_hidden_weight_cache
  scripts/start_agent_batch.sh --rd 6 --category category3-model_behavior_and_finetuning_poisoning
  scripts/start_agent_batch.sh --rd 5 --case scheduling_email_session_history_context_contamination_thread_memory --network-mode host
  scripts/start_agent_batch.sh --manifest benchmark/risk-domain-3-execution-runtime-framework-and-protocol-risks/manifest.json --jobs-dir jobs/rd3-agent
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

openai_preflight() {
  local envrc_path=$1
  local model_name=$2
  local base_url=""
  local api_key=""
  local codex_auth_json="${HOME}/.codex/auth.json"
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

  if [[ -z "${api_key}" ]]; then
    if [[ -f "${codex_auth_json}" ]] && grep -q '"auth_mode"[[:space:]]*:[[:space:]]*"chatgpt"' "${codex_auth_json}"; then
      if [[ -n "${base_url}" ]]; then
        die "OPENAI_API_KEY is not set in ${envrc_path}; ChatGPT Codex login cannot authenticate a custom OPENAI_BASE_URL"
      fi
      printf '[info] using local Codex ChatGPT login for OpenAI auth\n' >&2
    else
      die "OPENAI_API_KEY is not set in ${envrc_path}, and local Codex ChatGPT login was not found"
    fi
  fi

  provider_model="${model_name##*/}"
  if [[ -z "${provider_model}" ]]; then
    provider_model="${OPENAI_MODEL:-}"
  fi
  if [[ -z "${base_url}" ]]; then
    printf '[info] skipping codex API request preflight because no OPENAI_BASE_URL/OPENAI_API_BASE is set; auth looks present\n' >&2
    return 0
  fi
  if [[ -z "${provider_model}" ]]; then
    printf '[info] skipping codex API request preflight because no model was provided; auth/base URL look present\n' >&2
    return 0
  fi

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

claude_code_preflight() {
  local envrc_path=$1
  local auth_token=""
  local bedrock_token=""
  local use_bedrock=""

  set -a
  # shellcheck source=/dev/null
  source "${envrc_path}"
  set +a

  auth_token="${ANTHROPIC_API_KEY:-${ANTHROPIC_AUTH_TOKEN:-${CLAUDE_CODE_OAUTH_TOKEN:-}}}"
  bedrock_token="${AWS_BEARER_TOKEN_BEDROCK:-}"
  use_bedrock="${CLAUDE_CODE_USE_BEDROCK:-}"

  if [[ -n "${auth_token}" || -n "${bedrock_token}" || "${use_bedrock}" == "1" ]]; then
    return 0
  fi

  die "Claude Code preflight failed; set ANTHROPIC_API_KEY, ANTHROPIC_AUTH_TOKEN, CLAUDE_CODE_OAUTH_TOKEN, or Bedrock auth in ${envrc_path}"
}

agent_preflight() {
  local agent_name=$1
  local envrc_path=$2
  local model_name=$3

  case "${agent_name}" in
    codex)
      openai_preflight "${envrc_path}" "${model_name}"
      ;;
    claude-code)
      claude_code_preflight "${envrc_path}"
      ;;
    *)
      printf '[info] no agent-specific preflight implemented for %s; skipping\n' "${agent_name}" >&2
      ;;
  esac
}

RD=""
MANIFEST=""
JOBS_DIR=""
AGENT="${SSB_AGENT:-codex}"
AGENT_IMPORT_PATH="${SSB_AGENT_IMPORT_PATH:-}"
ENVIRONMENT_IMPORT_PATH="${SSB_ENVIRONMENT_IMPORT_PATH:-}"
MODEL="${SSB_MODEL:-}"
REASONING_EFFORT="${SSB_REASONING_EFFORT:-}"
NETWORK_MODE="${NETWORK_MODE:-}"
RETRIES="1"
AGENT_TIMEOUT_MULTIPLIER="3.0"
AGENT_SETUP_TIMEOUT_MULTIPLIER="8.0"
ENVRC="${BENCH_ROOT}/.envrc"
DRY_RUN="0"
SKIP_API_PREFLIGHT="0"

declare -a CASE_FILTERS=()
declare -a CATEGORY_FILTERS=()
declare -a AGENT_KWARGS=()

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
    --agent)
      require_value "$1" "${2-}"
      AGENT="$2"
      shift 2
      ;;
    --agent-import-path)
      require_value "$1" "${2-}"
      AGENT_IMPORT_PATH="$2"
      shift 2
      ;;
    --environment-import-path)
      require_value "$1" "${2-}"
      ENVIRONMENT_IMPORT_PATH="$2"
      shift 2
      ;;
    --model)
      require_value "$1" "${2-}"
      MODEL="$2"
      shift 2
      ;;
    --reasoning-effort)
      require_value "$1" "${2-}"
      REASONING_EFFORT="$2"
      shift 2
      ;;
    --agent-kwarg|--ak)
      require_value "$1" "${2-}"
      AGENT_KWARGS+=("$2")
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

if [[ "${DRY_RUN}" != "1" ]]; then
  ensure_anthropic_pdf_compat_proxy "${ENVRC}"
fi

if [[ -z "${MODEL}" ]]; then
  if [[ -n "${SSB_MODEL:-}" ]]; then
    MODEL="${SSB_MODEL}"
  elif [[ "${AGENT}" == "codex" && -n "${SSB_CODEX_MODEL:-}" ]]; then
    MODEL="${SSB_CODEX_MODEL}"
  elif [[ "${AGENT}" == "claude-code" && -n "${SSB_CLAUDE_MODEL:-}" ]]; then
    MODEL="${SSB_CLAUDE_MODEL}"
  elif [[ "${AGENT}" == "claude-code" && -n "${ANTHROPIC_MODEL:-}" ]]; then
    MODEL="${ANTHROPIC_MODEL}"
  fi
fi

if [[ -z "${JOBS_DIR}" ]]; then
  stamp="$(date +%Y%m%d-%H%M%S)"
  manifest_label="$(basename -- "$(dirname -- "${MANIFEST}")")"
  JOBS_DIR="${BENCH_ROOT}/jobs/${AGENT}-${manifest_label}-${stamp}"
elif [[ "${JOBS_DIR}" != /* ]]; then
  JOBS_DIR="${BENCH_ROOT}/${JOBS_DIR}"
fi

mkdir -p "${JOBS_DIR}"

json_array() {
  python3 - "$@" <<'PY'
import json
import sys
print(json.dumps(sys.argv[1:], ensure_ascii=False))
PY
}

CASE_FILTERS_JSON="$(json_array "${CASE_FILTERS[@]}")"
CATEGORY_FILTERS_JSON="$(json_array "${CATEGORY_FILTERS[@]}")"
AGENT_KWARGS_JSON="$(json_array "${AGENT_KWARGS[@]}")"

write_selection_metadata() {
  python3 - "${MANIFEST}" "${JOBS_DIR}" "${ENVRC}" "${AGENT}" "${MODEL}" "${REASONING_EFFORT}" "${RETRIES}" "${AGENT_TIMEOUT_MULTIPLIER}" "${AGENT_SETUP_TIMEOUT_MULTIPLIER}" "${CASE_FILTERS_JSON}" "${CATEGORY_FILTERS_JSON}" "${AGENT_KWARGS_JSON}" "${AGENT_IMPORT_PATH}" "${ENVIRONMENT_IMPORT_PATH}" <<'PY'
import json
import sys
from pathlib import Path

manifest_path = Path(sys.argv[1]).resolve()
jobs_dir = Path(sys.argv[2]).resolve()
envrc_path = Path(sys.argv[3]).resolve()
agent = sys.argv[4]
model = sys.argv[5]
reasoning_effort = sys.argv[6]
retries = int(sys.argv[7])
agent_timeout_multiplier = float(sys.argv[8])
agent_setup_timeout_multiplier = float(sys.argv[9])
case_filters = json.loads(sys.argv[10])
category_filters = json.loads(sys.argv[11])
agent_kwargs = json.loads(sys.argv[12])
agent_import_path = sys.argv[13]
environment_import_path = sys.argv[14]

manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
selected = manifest["cases"]

if category_filters:
    wanted_categories = set(category_filters)
    selected = [case for case in selected if case.get("category") in wanted_categories]

if case_filters:
    order = {case_id: idx for idx, case_id in enumerate(case_filters)}
    selected = [case for case in selected if case["case_id"] in order]
    selected.sort(key=lambda case: order[case["case_id"]])

(jobs_dir / "selected_cases.json").write_text(
    json.dumps(selected, indent=2, ensure_ascii=False) + "\n",
    encoding="utf-8",
)

batch_config = {
    "manifest": str(manifest_path),
    "envrc": str(envrc_path),
    "agent": agent,
    "model": model,
    "reasoning_effort": reasoning_effort,
    "retries": retries,
    "agent_timeout_multiplier": agent_timeout_multiplier,
    "agent_setup_timeout_multiplier": agent_setup_timeout_multiplier,
    "agent_import_path": agent_import_path,
    "environment_import_path": environment_import_path,
    "agent_kwargs": agent_kwargs,
    "case_filter": [case["case_id"] for case in selected],
    "category_filter": category_filters,
}
(jobs_dir / "batch_config.json").write_text(
    json.dumps(batch_config, indent=2, ensure_ascii=False) + "\n",
    encoding="utf-8",
)

for case in selected:
    print(case["case_id"])
PY
}

verify_case_and_refresh_summary() {
  local case_id=$1
  python3 - "${BENCH_ROOT}" "${JOBS_DIR}" "${case_id}" <<'PY'
import csv
import json
import sys
from collections import Counter
from pathlib import Path

bench_root = Path(sys.argv[1]).resolve()
jobs_dir = Path(sys.argv[2]).resolve()
case_id = sys.argv[3]
sys.path.insert(0, str(bench_root / "scripts"))

import verify_replay as replay

selected_path = jobs_dir / "selected_cases.json"
if not selected_path.exists():
    raise SystemExit(f"selected cases file missing: {selected_path}")

batch_config_path = jobs_dir / "batch_config.json"
batch_config = {}
if batch_config_path.exists():
    batch_config = json.loads(batch_config_path.read_text(encoding="utf-8"))
agent_name = batch_config.get("agent", "codex")
agent_label = " ".join(part.capitalize() for part in agent_name.replace("_", "-").split("-"))

selected = json.loads(selected_path.read_text(encoding="utf-8"))
selected_by_id = {entry["case_id"]: entry for entry in selected}
if case_id not in selected_by_id:
    raise SystemExit(f"case not found in selected set: {case_id}")

case_entry = selected_by_id[case_id]
case_job_dir = jobs_dir / case_id
case_job_dir.mkdir(parents=True, exist_ok=True)
trial_dir = replay.latest_trial_dir(case_job_dir) if case_job_dir.exists() else None

result = replay.load_job_result(case_job_dir)
if not result and trial_dir is not None:
    result = replay.load_trial_result(trial_dir)

reward = None
exception_type = None
exception_message = None
if result:
    rewards = result.get("verifier_result", {}).get("rewards", {})
    reward = rewards.get("reward", result.get("reward"))
    exc = result.get("exception") or result.get("exception_info")
    if isinstance(exc, dict):
        exception_type = exc.get("type") or exc.get("exception_type")
        exception_message = exc.get("message") or exc.get("exception_message")

attack_success = None
verify_status = "missing_trial_dir"
verify_bucket = "execution_error"
verify_exit_code = None
verify_stdout = ""
verify_stderr = ""
task_output_missing_observed = False
skill_adherence = "unknown"
skill_adherence_source = "missing_trial_dir"
available_skill_names = []
used_skill_names = []

if trial_dir is not None:
    case_dir = replay.resolve_bench_path(case_entry["case_path"])
    attack_success, verify_status, verify_bucket, verify_exit_code, verify_stdout, verify_stderr = replay.run_verify_replay(
        case_dir,
        trial_dir,
    )
    adherence = replay.skill_adherence(case_dir, trial_dir)
    skill_adherence = adherence.get("skill_adherence", "unknown")
    skill_adherence_source = adherence.get("skill_adherence_source")
    available_skill_names = adherence.get("available_skill_names") or []
    used_skill_names = adherence.get("used_skill_names") or []
    task_output_missing_observed = replay.has_task_output_missing(verify_stdout)
    (trial_dir / "custom_verify_stdout.txt").write_text(verify_stdout, encoding="utf-8")
    (trial_dir / "custom_verify_stderr.txt").write_text(verify_stderr, encoding="utf-8")
    (trial_dir / "custom_verify_result.json").write_text(
        json.dumps(
            {
                "attack_success": attack_success,
                "verify_status": verify_status,
                "verify_bucket": verify_bucket,
                "task_output_missing_observed": task_output_missing_observed,
                "verify_exit_code": verify_exit_code,
                "verify_stdout": verify_stdout,
                "verify_stderr": verify_stderr,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

case_result = {
    "case_id": case_entry["case_id"],
    "category": case_entry["category"],
    "class": case_entry["class"],
    "original_task_id": case_entry["original_task_id"],
    "job_dir": str(case_job_dir),
    "trial_dir": str(trial_dir) if trial_dir else None,
    "harbor_return_code": None if not result else result.get("harbor_return_code"),
    "reward": reward,
    "exception_type": exception_type,
    "exception_message": exception_message,
    "attack_success": attack_success,
    "verify_status": verify_status,
    "verify_bucket": verify_bucket,
    "task_output_missing_observed": task_output_missing_observed,
    "skill_adherence": skill_adherence,
    "skill_adherence_source": skill_adherence_source,
    "available_skill_names": available_skill_names,
    "used_skill_names": used_skill_names,
    "verify_exit_code": verify_exit_code,
    "verify_stdout": verify_stdout,
    "verify_stderr": verify_stderr,
}
(case_job_dir / "case_result.json").write_text(
    json.dumps(case_result, indent=2, ensure_ascii=False) + "\n",
    encoding="utf-8",
)

results = []
for entry in selected:
    result_path = jobs_dir / entry["case_id"] / "case_result.json"
    if result_path.exists():
        results.append(json.loads(result_path.read_text(encoding="utf-8")))

label = f"{jobs_dir.name} {agent_label}"
replay.summarize(results, jobs_dir, label)

verify_bucket_counts = Counter(row.get("verify_bucket") for row in results if row.get("verify_bucket"))
verify_status_counts = Counter(row.get("verify_status") for row in results if row.get("verify_status"))
task_output_missing_count = sum(1 for row in results if row.get("task_output_missing_observed") is True)
attack_payload = {
    "selected_case_count": len(selected),
    "processed_case_count": len(results),
    "attack_success_count": sum(1 for row in results if row.get("attack_success") is True),
    "attack_not_observed_count": verify_bucket_counts.get("attack_not_observed", 0),
    "task_output_missing_count": task_output_missing_count,
    "evaluator_error_count": verify_bucket_counts.get("evaluator_error", 0),
    "verify_bucket_counts": dict(verify_bucket_counts),
    "verify_status_counts": dict(verify_status_counts),
    "results": results,
}

(jobs_dir / "attack_results.json").write_text(
    json.dumps(attack_payload, indent=2, ensure_ascii=False) + "\n",
    encoding="utf-8",
)

with (jobs_dir / "attack_results.csv").open("w", encoding="utf-8", newline="") as handle:
    writer = csv.DictWriter(
        handle,
        fieldnames=[
            "case_id",
            "category",
            "class",
            "original_task_id",
            "attack_success",
            "verify_status",
            "verify_bucket",
            "task_output_missing_observed",
            "verify_exit_code",
            "reward",
            "exception_type",
            "trial_dir",
        ],
    )
    writer.writeheader()
    for row in results:
        writer.writerow({key: row.get(key) for key in writer.fieldnames})

lines = [
    f"# {jobs_dir.name} Attack Results",
    "",
    f"- Selected cases: `{len(selected)}`",
    f"- Processed cases: `{len(results)}`",
    f"- `attack_success`: `{attack_payload['attack_success_count']}`",
    f"- `attack_not_observed`: `{attack_payload['attack_not_observed_count']}`",
    f"- `task_output_missing`: `{attack_payload['task_output_missing_count']}`",
    f"- `evaluator_error`: `{attack_payload['evaluator_error_count']}`",
    "",
    "## Per Case",
    "",
]
for row in results:
    lines.append(
        f"- `{row['case_id']}`: verify_status=`{row.get('verify_status')}`, verify_bucket=`{row.get('verify_bucket')}`, task_output_missing=`{row.get('task_output_missing_observed')}`, attack_success=`{row.get('attack_success')}`"
    )

(jobs_dir / "attack_results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"[verify] {case_id}: verify_status={verify_status} verify_bucket={verify_bucket} attack_success={attack_success}")
PY
}

mapfile -t SELECTED_CASES < <(write_selection_metadata)
[[ "${#SELECTED_CASES[@]}" -gt 0 ]] || die "no cases selected"

printf 'manifest: %s\n' "${MANIFEST}"
printf 'jobs_dir: %s\n' "${JOBS_DIR}"
printf 'agent: %s\n' "${AGENT}"
if [[ -n "${MODEL}" ]]; then
  printf 'model: %s\n' "${MODEL}"
else
  printf 'model: <agent default>\n'
fi
if [[ -n "${REASONING_EFFORT}" ]]; then
  printf 'reasoning_effort: %s\n' "${REASONING_EFFORT}"
fi
if [[ -n "${AGENT_IMPORT_PATH}" ]]; then
  printf 'agent_import_path: %s\n' "${AGENT_IMPORT_PATH}"
fi
if [[ -n "${ENVIRONMENT_IMPORT_PATH}" ]]; then
  printf 'environment_import_path: %s\n' "${ENVIRONMENT_IMPORT_PATH}"
fi
if [[ -n "${NETWORK_MODE}" ]]; then
  printf 'network_mode: %s\n' "${NETWORK_MODE}"
fi
printf 'selected_cases: %s\n' "${#SELECTED_CASES[@]}"
printf 'run_mode: per-case harbor run + per-case verify replay\n'

if [[ "${DRY_RUN}" == "1" ]]; then
  for case_id in "${SELECTED_CASES[@]}"; do
    printf 'case: %s\n' "${case_id}"
  done
  exit 0
fi

if [[ "${SKIP_API_PREFLIGHT}" != "1" ]]; then
  agent_preflight "${AGENT}" "${ENVRC}" "${MODEL}"
fi

command -v harbor >/dev/null 2>&1 || die "harbor is required"

if [[ -n "${NETWORK_MODE}" ]]; then
  export NETWORK_MODE
fi

overall_rc=0
total_cases="${#SELECTED_CASES[@]}"

for idx in "${!SELECTED_CASES[@]}"; do
  case_id="${SELECTED_CASES[$idx]}"
  printf '[%d/%d] run %s\n' "$((idx + 1))" "${total_cases}" "${case_id}"

  case_cmd=(
    python3
    "${BENCH_ROOT}/scripts/run_manifest_agent_batch.py"
    --manifest "${MANIFEST}"
    --jobs-dir "${JOBS_DIR}"
    --envrc "${ENVRC}"
    --agent "${AGENT}"
    --retries "${RETRIES}"
    --agent-timeout-multiplier "${AGENT_TIMEOUT_MULTIPLIER}"
    --agent-setup-timeout-multiplier "${AGENT_SETUP_TIMEOUT_MULTIPLIER}"
    --case-filter "${case_id}"
  )
  if [[ -n "${MODEL}" ]]; then
    case_cmd+=(--model "${MODEL}")
  fi
  if [[ -n "${REASONING_EFFORT}" ]]; then
    case_cmd+=(--reasoning-effort "${REASONING_EFFORT}")
  fi
  if [[ -n "${AGENT_IMPORT_PATH}" ]]; then
    case_cmd+=(--agent-import-path "${AGENT_IMPORT_PATH}")
  fi
  if [[ -n "${ENVIRONMENT_IMPORT_PATH}" ]]; then
    case_cmd+=(--environment-import-path "${ENVIRONMENT_IMPORT_PATH}")
  fi
  for agent_kwarg in "${AGENT_KWARGS[@]}"; do
    case_cmd+=(--agent-kwarg "${agent_kwarg}")
  done

  set +e
  "${case_cmd[@]}"
  case_rc=$?
  set -e
  if [[ "${case_rc}" -ne 0 ]]; then
    printf '[warn] harbor runner returned non-zero for %s: %s\n' "${case_id}" "${case_rc}" >&2
    overall_rc="${case_rc}"
  fi

  write_selection_metadata >/dev/null

  printf '[%d/%d] verify %s\n' "$((idx + 1))" "${total_cases}" "${case_id}"
  set +e
  verify_case_and_refresh_summary "${case_id}"
  verify_rc=$?
  set -e
  if [[ "${verify_rc}" -ne 0 ]]; then
    printf '[warn] verifier replay failed for %s: %s\n' "${case_id}" "${verify_rc}" >&2
    overall_rc="${verify_rc}"
  fi
done

printf 'attack_results: %s\n' "${JOBS_DIR}/attack_results.json"
printf 'summary: %s\n' "${JOBS_DIR}/summary.json"
printf 'reward_summary: %s\n' "${JOBS_DIR}/reward_summary.json"
printf 'skill_adherence_summary: %s\n' "${JOBS_DIR}/skill_adherence_summary.json"
exit "${overall_rc}"
