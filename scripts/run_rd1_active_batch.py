#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

REPO = Path("/home/jinchang/Documents/skillsbench")
BENCH = REPO / "skill-safety-bench"
RD1 = BENCH / "benchmark" / "risk-domain-1-context-trust-and-prompt-manipulation-risks"
MANIFEST = RD1 / "manifest.json"
ENVRC = BENCH / ".envrc"


def load_manifest() -> dict[str, Any]:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def ensure_google_auth_placeholder(jobs_dir: Path) -> Path:
    runtime = jobs_dir / "_runtime_placeholders"
    runtime.mkdir(parents=True, exist_ok=True)
    placeholder = runtime / "google-auth-placeholder.json"
    if not placeholder.exists():
        placeholder.write_text("{}", encoding="utf-8")
    return placeholder


def parse_output_artifacts(verify_path: Path) -> list[str]:
    text = verify_path.read_text(encoding="utf-8")
    artifacts = []
    for match in re.findall(r"""['"](/[^'"]+)['"]""", text):
        artifacts.append(match)
    seen = set()
    ordered = []
    for item in artifacts:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered


def build_local_verify_script(verify_script: Path, artifacts_dir: Path) -> str:
    text = verify_script.read_text(encoding="utf-8")
    mapping: dict[str, Path] = {}
    for original in parse_output_artifacts(verify_script):
        mapping[original] = artifacts_dir / Path(original).name

    for original, local in sorted(mapping.items(), key=lambda item: len(item[0]), reverse=True):
        text = text.replace(repr(original), repr(str(local)))
        text = text.replace(f'"{original}"', repr(str(local)))

    return text


def run_command(cmd: str, cwd: Path, stdout_path: Path, stderr_path: Path) -> int:
    with stdout_path.open("w", encoding="utf-8") as out, stderr_path.open("w", encoding="utf-8") as err:
        proc = subprocess.run(["bash", "-lc", cmd], cwd=str(cwd), stdout=out, stderr=err)
    return proc.returncode


def latest_trial_dir(case_job_dir: Path) -> Path | None:
    candidates = [p for p in case_job_dir.iterdir() if p.is_dir() and "__" in p.name]
    if not candidates:
        nested = [p for p in case_job_dir.glob("*__*") if p.is_dir()]
        candidates = nested
    if not candidates:
        return None
    return sorted(candidates, key=lambda p: p.stat().st_mtime, reverse=True)[0]


def run_custom_verify(case_dir: Path, trial_dir: Path) -> tuple[bool | None, str, int | None, str, str]:
    verify_script = case_dir / "eval" / "verify_attack.py"
    artifacts_dir = trial_dir / "artifacts"
    if not verify_script.exists():
        return None, "missing_verify", None, "", "verify script missing"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO)
    replay_script = trial_dir / "custom_verify_replay.py"
    replay_script.write_text(build_local_verify_script(verify_script, artifacts_dir), encoding="utf-8")
    proc = subprocess.run(
        ["python3", str(replay_script)],
        cwd=str(trial_dir),
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out = proc.stdout.strip()
    err = proc.stderr.strip()
    status = out.splitlines()[-1].strip() if out else "evaluator_error"
    if status == "attack_success":
        return True, status, proc.returncode, out, err
    if status in {"attack_not_observed", "task_output_missing"}:
        return False, status, proc.returncode, out, err
    return None, "evaluator_error", proc.returncode, out, err


def load_trial_result(trial_dir: Path) -> dict[str, Any]:
    p = trial_dir / "result.json"
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def load_job_result(case_job_dir: Path) -> dict[str, Any]:
    p = case_job_dir / "result.json"
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def build_harbor_command(
    case_name: str,
    task_path: Path,
    jobs_dir: Path,
    artifacts: list[str],
    timeout_mult: float,
    setup_timeout_mult: float | None,
) -> str:
    placeholder = ensure_google_auth_placeholder(jobs_dir)
    parts = [
        f"set -a; source {ENVRC}; set +a",
        "export CLAUDE_CODE_USE_VERTEX=${CLAUDE_CODE_USE_VERTEX:-0}",
        "export CLOUD_ML_REGION=${CLOUD_ML_REGION:-us-central1}",
        "export ANTHROPIC_VERTEX_PROJECT_ID=${ANTHROPIC_VERTEX_PROJECT_ID:-placeholder-project}",
        f"export GOOGLE_AUTH_PATH=${{GOOGLE_AUTH_PATH:-{placeholder}}}",
        "harbor run -q -r 1",
        f"--agent-timeout-multiplier {timeout_mult}",
        *([f"--agent-setup-timeout-multiplier {setup_timeout_mult}"] if setup_timeout_mult is not None else []),
        f"-p {task_path}",
        "-a codex",
        "-m openai/gpt-5.4",
        f"-o {jobs_dir}",
        f"--job-name {case_name}",
    ]
    for art in artifacts:
        parts.append(f"--artifact {art}")
    setup = "; ".join(parts[:5])
    harbor = " ".join(parts[5:])
    return f"{setup}; {harbor}"


def summarize(results: list[dict[str, Any]], jobs_dir: Path) -> None:
    summary_json = jobs_dir / "summary.json"
    summary_csv = jobs_dir / "summary.csv"
    summary_md = jobs_dir / "summary.md"

    summary_payload = {
        "case_count": len(results),
        "attack_success_count": sum(1 for r in results if r.get("attack_success") is True),
        "attack_not_observed_count": sum(1 for r in results if r.get("verify_status") == "attack_not_observed"),
        "task_output_missing_count": sum(1 for r in results if r.get("verify_status") == "task_output_missing"),
        "evaluator_error_count": sum(1 for r in results if r.get("verify_status") == "evaluator_error"),
        "exception_type_counts": dict(Counter(r.get("exception_type") for r in results if r.get("exception_type"))),
        "results": results,
    }
    summary_json.write_text(json.dumps(summary_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    fieldnames = [
        "case_id",
        "category",
        "class",
        "original_task_id",
        "harbor_return_code",
        "reward",
        "exception_type",
        "exception_message",
        "attack_success",
        "verify_status",
        "verify_exit_code",
        "trial_dir",
    ]
    with summary_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow({k: row.get(k) for k in fieldnames})

    total = len(results)
    success = sum(1 for r in results if r.get("attack_success") is True)
    lines = [
        "# RD1 Active Rerun Summary",
        "",
        f"- Total cases: `{total}`",
        f"- `attack_success`: `{success}`",
        f"- ASR: `{(success / total * 100):.1f}%`" if total else "- ASR: `n/a`",
        f"- `attack_not_observed`: `{sum(1 for r in results if r.get('verify_status') == 'attack_not_observed')}`",
        f"- `task_output_missing`: `{sum(1 for r in results if r.get('verify_status') == 'task_output_missing')}`",
        f"- `evaluator_error`: `{sum(1 for r in results if r.get('verify_status') == 'evaluator_error')}`",
        "",
        "## Per Case",
        "",
    ]
    for row in results:
        lines.append(
            f"- `{row['case_id']}`: reward=`{row.get('reward')}`, verify_status=`{row.get('verify_status')}`, attack_success=`{row.get('attack_success')}`, exception_type=`{row.get('exception_type')}`"
        )
    summary_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_case(
    case_entry: dict[str, Any],
    jobs_dir: Path,
    timeout_mult: float,
    setup_timeout_mult: float | None,
) -> dict[str, Any]:
    case_dir = REPO / case_entry["case_path"]
    task_path = case_dir / "attacked_task"
    case_name = case_entry["case_id"]
    job_case_dir = jobs_dir / case_name
    if job_case_dir.exists():
        shutil.rmtree(job_case_dir)
    job_case_dir.mkdir(parents=True, exist_ok=True)

    verify_path = case_dir / "eval" / "verify_attack.py"
    artifacts = parse_output_artifacts(verify_path)

    harbor_cmd = build_harbor_command(
        case_name,
        task_path,
        jobs_dir,
        artifacts,
        timeout_mult,
        setup_timeout_mult,
    )
    (job_case_dir / "harbor_command.sh").write_text(harbor_cmd + "\n", encoding="utf-8")
    rc = run_command(
        harbor_cmd,
        REPO,
        job_case_dir / "harbor_stdout.txt",
        job_case_dir / "harbor_stderr.txt",
    )

    trial_dir = latest_trial_dir(job_case_dir)
    reward = None
    exception_type = None
    exception_message = None
    verify_exit_code = None
    verify_status = "missing_trial_dir"
    verify_stdout = ""
    verify_stderr = ""
    attack_success: bool | None = None

    result = load_job_result(job_case_dir)
    if not result and trial_dir is not None:
        result = load_trial_result(trial_dir)
    if result:
        reward = result.get("reward")
        exc = result.get("exception")
        if isinstance(exc, dict):
            exception_type = exc.get("type")
            exception_message = exc.get("message")
    if trial_dir is not None:
        attack_success, verify_status, verify_exit_code, verify_stdout, verify_stderr = run_custom_verify(case_dir, trial_dir)
        (trial_dir / "custom_verify_stdout.txt").write_text(verify_stdout, encoding="utf-8")
        (trial_dir / "custom_verify_stderr.txt").write_text(verify_stderr, encoding="utf-8")
        (trial_dir / "custom_verify_result.json").write_text(
            json.dumps(
                {
                    "attack_success": attack_success,
                    "verify_status": verify_status,
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
        "case_id": case_name,
        "category": case_entry["category"],
        "class": case_entry["class"],
        "original_task_id": case_entry["original_task_id"],
        "job_dir": str(job_case_dir),
        "trial_dir": str(trial_dir) if trial_dir else None,
        "harbor_return_code": rc,
        "reward": reward,
        "exception_type": exception_type,
        "exception_message": exception_message,
        "attack_success": attack_success,
        "verify_status": verify_status,
        "verify_exit_code": verify_exit_code,
        "verify_stdout": verify_stdout,
        "verify_stderr": verify_stderr,
    }
    (job_case_dir / "case_result.json").write_text(
        json.dumps(case_result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return case_result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--jobs-dir", default=str(BENCH / "jobs" / "rd1-active-rerun-20260408"))
    parser.add_argument("--category", action="append", default=[])
    parser.add_argument("--case-id", action="append", default=[])
    parser.add_argument("--timeout-multiplier", type=float, default=2.0)
    parser.add_argument("--agent-setup-timeout-multiplier", type=float, default=8.0)
    parser.add_argument("--keep-existing", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    manifest = load_manifest()
    selected = manifest["cases"]
    if args.category:
        selected = [c for c in selected if c["category"] in set(args.category)]
    if args.case_id:
        selected = [c for c in selected if c["case_id"] in set(args.case_id)]

    jobs_dir = Path(args.jobs_dir)
    if jobs_dir.exists() and not args.keep_existing:
        shutil.rmtree(jobs_dir)
    jobs_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for case_entry in selected:
        results.append(
            run_case(
                case_entry,
                jobs_dir,
                args.timeout_multiplier,
                args.agent_setup_timeout_multiplier,
            )
        )
        summarize(results, jobs_dir)
    summarize(results, jobs_dir)


if __name__ == "__main__":
    main()
