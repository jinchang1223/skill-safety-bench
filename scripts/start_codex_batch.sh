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

Behavior:
  Runs the selected cases one by one. After each case finishes, replay
  eval/verify_attack.py for that case and refresh jobs_dir summaries.

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

json_array() {
  python3 - "$@" <<'PY'
import json
import sys
print(json.dumps(sys.argv[1:], ensure_ascii=False))
PY
}

CASE_FILTERS_JSON="$(json_array "${CASE_FILTERS[@]}")"
CATEGORY_FILTERS_JSON="$(json_array "${CATEGORY_FILTERS[@]}")"

write_selection_metadata() {
  python3 - "${MANIFEST}" "${JOBS_DIR}" "${ENVRC}" "${MODEL}" "${RETRIES}" "${AGENT_TIMEOUT_MULTIPLIER}" "${AGENT_SETUP_TIMEOUT_MULTIPLIER}" "${CASE_FILTERS_JSON}" "${CATEGORY_FILTERS_JSON}" <<'PY'
import json
import sys
from pathlib import Path

manifest_path = Path(sys.argv[1]).resolve()
jobs_dir = Path(sys.argv[2]).resolve()
envrc_path = Path(sys.argv[3]).resolve()
model = sys.argv[4]
retries = int(sys.argv[5])
agent_timeout_multiplier = float(sys.argv[6])
agent_setup_timeout_multiplier = float(sys.argv[7])
case_filters = json.loads(sys.argv[8])
category_filters = json.loads(sys.argv[9])

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
    "model": model,
    "retries": retries,
    "agent_timeout_multiplier": agent_timeout_multiplier,
    "agent_setup_timeout_multiplier": agent_setup_timeout_multiplier,
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

import run_manifest_oracle_batch as oracle

selected_path = jobs_dir / "selected_cases.json"
if not selected_path.exists():
    raise SystemExit(f"selected cases file missing: {selected_path}")

selected = json.loads(selected_path.read_text(encoding="utf-8"))
selected_by_id = {entry["case_id"]: entry for entry in selected}
if case_id not in selected_by_id:
    raise SystemExit(f"case not found in selected set: {case_id}")

case_entry = selected_by_id[case_id]
case_job_dir = jobs_dir / case_id
case_job_dir.mkdir(parents=True, exist_ok=True)
trial_dir = oracle.latest_trial_dir(case_job_dir) if case_job_dir.exists() else None

result = oracle.load_job_result(case_job_dir)
if not result and trial_dir is not None:
    result = oracle.load_trial_result(trial_dir)

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

if trial_dir is not None:
    case_dir = oracle.resolve_bench_path(case_entry["case_path"])
    attack_success, verify_status, verify_bucket, verify_exit_code, verify_stdout, verify_stderr = oracle.run_custom_verify(
        case_dir,
        trial_dir,
    )
    (trial_dir / "custom_verify_stdout.txt").write_text(verify_stdout, encoding="utf-8")
    (trial_dir / "custom_verify_stderr.txt").write_text(verify_stderr, encoding="utf-8")
    (trial_dir / "custom_verify_result.json").write_text(
        json.dumps(
            {
                "attack_success": attack_success,
                "verify_status": verify_status,
                "verify_bucket": verify_bucket,
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

label = f"{jobs_dir.name} Codex"
oracle.summarize(results, jobs_dir, label)

verify_bucket_counts = Counter(row.get("verify_bucket") for row in results if row.get("verify_bucket"))
verify_status_counts = Counter(row.get("verify_status") for row in results if row.get("verify_status"))
attack_payload = {
    "selected_case_count": len(selected),
    "processed_case_count": len(results),
    "attack_success_count": sum(1 for row in results if row.get("attack_success") is True),
    "attack_not_observed_count": verify_bucket_counts.get("attack_not_observed", 0),
    "task_output_missing_count": verify_bucket_counts.get("task_output_missing", 0),
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
        f"- `{row['case_id']}`: verify_status=`{row.get('verify_status')}`, verify_bucket=`{row.get('verify_bucket')}`, attack_success=`{row.get('attack_success')}`"
    )

(jobs_dir / "attack_results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"[verify] {case_id}: verify_status={verify_status} verify_bucket={verify_bucket} attack_success={attack_success}")
PY
}

mapfile -t SELECTED_CASES < <(write_selection_metadata)
[[ "${#SELECTED_CASES[@]}" -gt 0 ]] || die "no cases selected"

printf 'manifest: %s\n' "${MANIFEST}"
printf 'jobs_dir: %s\n' "${JOBS_DIR}"
printf 'model: %s\n' "${MODEL}"
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
  api_preflight "${ENVRC}" "${MODEL}"
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
    "${BENCH_ROOT}/scripts/run_manifest_codex_batch.py"
    --manifest "${MANIFEST}"
    --jobs-dir "${JOBS_DIR}"
    --envrc "${ENVRC}"
    --model "${MODEL}"
    --retries "${RETRIES}"
    --agent-timeout-multiplier "${AGENT_TIMEOUT_MULTIPLIER}"
    --agent-setup-timeout-multiplier "${AGENT_SETUP_TIMEOUT_MULTIPLIER}"
    --case-filter "${case_id}"
  )

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
exit "${overall_rc}"
