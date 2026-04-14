#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
BENCH = SCRIPT_DIR.parent
VERIFY_PYTHON = BENCH / ".venv-skillsbench-eval" / "bin" / "python"
VERIFY_MODULE_PACKAGE_MAP = {
    "docx": "python-docx",
    "pptx": "python-pptx",
    "openpyxl": "openpyxl",
    "pypdf": "pypdf",
    "PyPDF2": "PyPDF2",
    "PIL": "Pillow",
}


def resolve_bench_path(raw_path: str) -> Path:
    path = raw_path.strip()
    prefixes = (f"{BENCH.name}/", "skill-safety-bench/")
    for prefix in prefixes:
        if path.startswith(prefix):
            path = path[len(prefix) :]
            break
    return BENCH / path


def load_manifest(manifest_path: Path) -> dict[str, Any]:
    return json.loads(manifest_path.read_text(encoding="utf-8"))


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


def _candidate_replay_paths(original: str, root: Path) -> list[Path]:
    relative = original.lstrip("/")
    basename = Path(original).name
    candidates = []
    if relative:
        candidates.append(root / relative)
    if basename:
        candidates.append(root / basename)
    return candidates


def _first_existing_replay_path(original: str, artifacts_dir: Path, verifier_dir: Path) -> Path | None:
    basename = Path(original).name
    for root in (artifacts_dir, verifier_dir):
        for candidate in _candidate_replay_paths(original, root):
            if candidate.exists():
                return candidate
    if not basename:
        return None

    matches: list[Path] = []
    for root in (artifacts_dir, verifier_dir):
        if not root.exists():
            continue
        matches.extend(path for path in root.rglob(basename) if path.exists())
    if not matches:
        return None
    return sorted(matches, key=lambda path: (len(path.parts), str(path)))[0]


def _glob_replay_matches(original: str, artifacts_dir: Path, verifier_dir: Path) -> list[str]:
    relative = original.lstrip("/")
    basename = Path(original).name
    matches: list[str] = []
    seen: set[str] = set()

    for root in (artifacts_dir, verifier_dir):
        if not root.exists():
            continue
        patterns = [pattern for pattern in (relative, basename) if pattern]
        for pattern in patterns:
            iterator = root.glob(pattern) if "/" in pattern else root.rglob(pattern)
            for candidate in sorted(iterator):
                rendered = str(candidate)
                if rendered in seen:
                    continue
                seen.add(rendered)
                matches.append(rendered)
    return matches


def build_local_verify_script(verify_script: Path, artifacts_dir: Path) -> str:
    text = verify_script.read_text(encoding="utf-8")
    mapping: dict[str, Path] = {}
    glob_mapping: dict[str, list[str]] = {}
    verifier_dir = artifacts_dir.parent / "verifier"
    for original in parse_output_artifacts(verify_script):
        basename = Path(original).name
        if any(ch in basename for ch in "*?[]"):
            glob_mapping[original] = _glob_replay_matches(original, artifacts_dir, verifier_dir)
        resolved = _first_existing_replay_path(original, artifacts_dir, verifier_dir)
        if resolved is not None:
            mapping[original] = resolved
        else:
            mapping[original] = artifacts_dir / basename

    lines = text.splitlines(keepends=True)
    insert_at = 0
    while insert_at < len(lines):
        stripped = lines[insert_at].strip()
        if not stripped or stripped.startswith("import ") or stripped.startswith("from "):
            insert_at += 1
            continue
        break

    helper_block = (
        "import builtins as _bench_builtins\n"
        "import glob as _bench_glob_module\n"
        "import io as _bench_io\n"
        "import os as _bench_os\n"
        "import pathlib as _bench_pathlib\n"
        "\n"
        f"_BENCH_PATH_MAP = {json.dumps({k: str(v) for k, v in mapping.items()}, ensure_ascii=False, indent=2)}\n"
        f"_BENCH_GLOB_MAP = {json.dumps(glob_mapping, ensure_ascii=False, indent=2)}\n"
        "_BenchOrigPath = globals().get('Path', _bench_pathlib.Path)\n"
        "_bench_open = _bench_builtins.open\n"
        "_bench_orig_glob = _bench_glob_module.glob\n"
        "\n"
        "def _bench_remap_path(raw: str) -> str:\n"
        "    return _BENCH_PATH_MAP.get(raw, raw)\n"
        "\n"
        "def Path(*args, **kwargs):\n"
        "    path = _BenchOrigPath(*args, **kwargs)\n"
        "    return _BenchOrigPath(_bench_remap_path(str(path)))\n"
        "\n"
        "def open(file, *args, **kwargs):\n"
        "    try:\n"
        "        raw = _bench_os.fspath(file)\n"
        "    except TypeError:\n"
        "        return _bench_open(file, *args, **kwargs)\n"
        "    return _bench_open(_bench_remap_path(raw), *args, **kwargs)\n"
        "\n"
        "def _bench_glob(pattern, *args, **kwargs):\n"
        "    matches = _BENCH_GLOB_MAP.get(pattern)\n"
        "    if matches:\n"
        "        return matches\n"
        "    return _bench_orig_glob(_bench_remap_path(pattern), *args, **kwargs)\n"
        "\n"
        "_bench_builtins.open = open\n"
        "_bench_io.open = open\n"
        "_bench_glob_module.glob = _bench_glob\n"
        "\n"
    )
    lines.insert(insert_at, helper_block)
    return "".join(lines)


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


def verify_python() -> str:
    if VERIFY_PYTHON.exists():
        probe = subprocess.run(
            [str(VERIFY_PYTHON), "-m", "pip", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if probe.returncode == 0:
            return str(VERIFY_PYTHON)
    return sys.executable


def maybe_install_verify_dependency(stderr: str) -> bool:
    match = re.search(r"No module named '([^']+)'", stderr)
    if not match:
        return False
    module = match.group(1)
    package = VERIFY_MODULE_PACKAGE_MAP.get(module)
    if not package:
        return False
    proc = subprocess.run(
        [verify_python(), "-m", "pip", "install", package],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return proc.returncode == 0


def classify_verify_result(
    out: str, err: str, exit_code: int | None
) -> tuple[bool | None, str, str, int | None, str, str]:
    status = out.splitlines()[-1].strip() if out else ""
    if status == "attack_success":
        return True, status, "attack_success", exit_code, out, err
    if status == "attack_partial_success":
        return False, status, "attack_partial_success", exit_code, out, err
    if status == "attack_not_observed":
        return False, status, "attack_not_observed", exit_code, out, err
    if status in {"task_output_missing", "target_missing", "artifact_missing"}:
        return False, status, "task_output_missing", exit_code, out, err
    if status in {"review_ref_missing", "memory_store_ref_missing", "memory_ref_missing"}:
        return False, status, "attack_not_observed", exit_code, out, err
    if status and re.fullmatch(r"[a-z0-9_]+", status):
        return False, status, "verifier_reported_failure", exit_code, out, err
    if "FileNotFoundError" in err and "/artifacts/" in err:
        return None, "evaluator_error", "evaluator_error", exit_code, out, err
    return None, "evaluator_error", "evaluator_error", exit_code, out, err


def run_custom_verify(case_dir: Path, trial_dir: Path) -> tuple[bool | None, str, str, int | None, str, str]:
    verify_script = case_dir / "eval" / "verify_attack.py"
    artifacts_dir = trial_dir.resolve() / "artifacts"
    if not verify_script.exists():
        return None, "missing_verify", "evaluator_error", None, "", "verify script missing"

    replay_script = trial_dir / "custom_verify_replay.py"
    replay_script.write_text(build_local_verify_script(verify_script, artifacts_dir), encoding="utf-8")
    for attempt in range(2):
        proc = subprocess.run(
            [verify_python(), replay_script.name],
            cwd=str(trial_dir),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out = proc.stdout.strip()
        err = proc.stderr.strip()
        attack_success, verify_status, verify_bucket, verify_exit_code, verify_stdout, verify_stderr = classify_verify_result(
            out,
            err,
            proc.returncode,
        )
        if verify_bucket != "evaluator_error" or attempt == 1:
            return attack_success, verify_status, verify_bucket, verify_exit_code, verify_stdout, verify_stderr
        if not maybe_install_verify_dependency(err):
            return attack_success, verify_status, verify_bucket, verify_exit_code, verify_stdout, verify_stderr
    return None, "evaluator_error", "evaluator_error", None, "", ""


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


def build_harbor_command(case_name: str, task_path: Path, jobs_dir: Path, artifacts: list[str], timeout_mult: float) -> str:
    parts = [
        "docker image rm -f hb__attacked_task:latest >/dev/null 2>&1 || true;",
        "harbor run -q -y",
        f"--timeout-multiplier {timeout_mult}",
        "-n 1",
        "-a oracle",
        f"-p {task_path}",
        f"-o {jobs_dir}",
        f"--job-name {case_name}",
    ]
    for art in artifacts:
        parts.append(f"--artifact {art}")
    return " ".join(parts)


def summarize(results: list[dict[str, Any]], jobs_dir: Path, label: str) -> None:
    summary_json = jobs_dir / "summary.json"
    summary_csv = jobs_dir / "summary.csv"
    summary_md = jobs_dir / "summary.md"
    verify_bucket_counts = Counter(r.get("verify_bucket") for r in results if r.get("verify_bucket"))
    verify_status_counts = Counter(r.get("verify_status") for r in results if r.get("verify_status"))

    summary_payload = {
        "case_count": len(results),
        "attack_success_count": sum(1 for r in results if r.get("attack_success") is True),
        "attack_partial_success_count": verify_bucket_counts.get("attack_partial_success", 0),
        "attack_not_observed_count": verify_bucket_counts.get("attack_not_observed", 0),
        "task_output_missing_count": verify_bucket_counts.get("task_output_missing", 0),
        "evaluator_error_count": verify_bucket_counts.get("evaluator_error", 0),
        "verify_bucket_counts": dict(verify_bucket_counts),
        "verify_status_counts": dict(verify_status_counts),
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
        "verify_bucket",
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
        f"# {label} Oracle Summary",
        "",
        f"- Total cases: `{total}`",
        f"- `attack_success`: `{success}`",
        f"- `attack_partial_success`: `{verify_bucket_counts.get('attack_partial_success', 0)}`",
        f"- ASR: `{(success / total * 100):.1f}%`" if total else "- ASR: `n/a`",
        f"- `attack_not_observed`: `{verify_bucket_counts.get('attack_not_observed', 0)}`",
        f"- `task_output_missing`: `{verify_bucket_counts.get('task_output_missing', 0)}`",
        f"- `evaluator_error`: `{verify_bucket_counts.get('evaluator_error', 0)}`",
        f"- `execution_error`: `{verify_bucket_counts.get('execution_error', 0)}`",
        f"- `verifier_reported_failure`: `{verify_bucket_counts.get('verifier_reported_failure', 0)}`",
        "",
        "## Raw Verify Status Counts",
        "",
    ]
    for status, count in sorted(verify_status_counts.items()):
        lines.append(f"- `{status}`: `{count}`")
    lines.extend(
        [
            "",
        "## Per Case",
        "",
        ]
    )
    for row in results:
        lines.append(
            f"- `{row['case_id']}`: reward=`{row.get('reward')}`, verify_status=`{row.get('verify_status')}`, verify_bucket=`{row.get('verify_bucket')}`, attack_success=`{row.get('attack_success')}`, exception_type=`{row.get('exception_type')}`"
        )
    summary_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_case(case_entry: dict[str, Any], jobs_dir: Path, timeout_mult: float) -> dict[str, Any]:
    case_dir = resolve_bench_path(case_entry["case_path"])
    task_path = resolve_bench_path(case_entry.get("task_path", "")) if case_entry.get("task_path") else case_dir / "attacked_task"
    case_name = case_entry["case_id"]
    job_case_dir = jobs_dir / case_name
    if job_case_dir.exists():
        shutil.rmtree(job_case_dir)
    job_case_dir.mkdir(parents=True, exist_ok=True)

    verify_path = case_dir / "eval" / "verify_attack.py"
    artifacts = parse_output_artifacts(verify_path)
    harbor_cmd = build_harbor_command(case_name, task_path, jobs_dir, artifacts, timeout_mult)
    (job_case_dir / "harbor_command.sh").write_text(harbor_cmd + "\n", encoding="utf-8")

    rc = run_command(
        harbor_cmd,
        BENCH,
        job_case_dir / "harbor_stdout.txt",
        job_case_dir / "harbor_stderr.txt",
    )

    trial_dir = latest_trial_dir(job_case_dir)
    reward = None
    exception_type = None
    exception_message = None
    verify_exit_code = None
    verify_status = "missing_trial_dir"
    verify_bucket = "execution_error"
    verify_stdout = ""
    verify_stderr = ""
    attack_success: bool | None = None

    result = load_job_result(job_case_dir)
    if not result and trial_dir is not None:
        result = load_trial_result(trial_dir)
    if result:
        rewards = result.get("verifier_result", {}).get("rewards", {})
        reward = rewards.get("reward", result.get("reward"))
        exc = result.get("exception") or result.get("exception_info")
        if isinstance(exc, dict):
            exception_type = exc.get("type") or exc.get("exception_type")
            exception_message = exc.get("message") or exc.get("exception_message")
    if trial_dir is not None:
        attack_success, verify_status, verify_bucket, verify_exit_code, verify_stdout, verify_stderr = run_custom_verify(
            case_dir, trial_dir
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
        "verify_bucket": verify_bucket,
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
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--jobs-dir", required=True)
    parser.add_argument("--label")
    parser.add_argument("--category", action="append", default=[])
    parser.add_argument("--case-id", action="append", default=[])
    parser.add_argument("--timeout-multiplier", type=float, default=1.0)
    parser.add_argument("--keep-existing", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    manifest_path = Path(args.manifest).resolve()
    manifest = load_manifest(manifest_path)
    label = args.label or manifest.get("risk_domain_name") or manifest_path.parent.name
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
        results.append(run_case(case_entry, jobs_dir, args.timeout_multiplier))
        summarize(results, jobs_dir, label)
    summarize(results, jobs_dir, label)


if __name__ == "__main__":
    main()
