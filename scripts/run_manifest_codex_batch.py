#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
BENCH = SCRIPT_DIR.parent


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
    if not verify_path.exists():
        return []
    text = verify_path.read_text(encoding="utf-8")
    artifacts = []
    for match in re.findall(r"""['"](/[^'"]+)['"]""", text):
        if match not in artifacts:
            artifacts.append(match)
    return artifacts


def build_harbor_command(
    *,
    task_path: Path,
    jobs_dir: Path,
    case_name: str,
    model: str,
    retries: int,
    agent_timeout_multiplier: float,
    agent_setup_timeout_multiplier: float | None,
    artifacts: list[str],
) -> str:
    parts = [
        "harbor run -q",
        f"-r {retries}",
        f"--agent-timeout-multiplier {agent_timeout_multiplier}",
    ]
    if agent_setup_timeout_multiplier is not None:
        parts.append(f"--agent-setup-timeout-multiplier {agent_setup_timeout_multiplier}")
    parts.extend(
        [
            f"-p {task_path}",
            "-a codex",
            f"-m {model}",
            f"-o {jobs_dir}",
            f"--job-name {case_name}",
        ]
    )
    for artifact in artifacts:
        parts.append(f"--artifact {artifact}")
    return " ".join(parts)


def wrap_with_envrc(command: str, envrc_path: Path) -> str:
    quoted_envrc = shlex.quote(str(envrc_path))
    return f"set -a; source {quoted_envrc}; set +a; {command}"


def run_case(
    case_entry: dict[str, Any],
    *,
    jobs_dir: Path,
    model: str,
    retries: int,
    agent_timeout_multiplier: float,
    agent_setup_timeout_multiplier: float | None,
    envrc_path: Path,
) -> None:
    case_name = case_entry["case_id"]
    case_dir = resolve_bench_path(case_entry["case_path"])
    task_path = resolve_bench_path(case_entry.get("task_path", "")) if case_entry.get("task_path") else case_dir / "attacked_task"
    verify_path = case_dir / "eval" / "verify_attack.py"
    artifacts = parse_output_artifacts(verify_path)

    case_job_dir = jobs_dir / case_name
    if case_job_dir.exists():
        shutil.rmtree(case_job_dir)
    case_job_dir.mkdir(parents=True, exist_ok=True)

    cmd = build_harbor_command(
        task_path=task_path,
        jobs_dir=jobs_dir,
        case_name=case_name,
        model=model,
        retries=retries,
        agent_timeout_multiplier=agent_timeout_multiplier,
        agent_setup_timeout_multiplier=agent_setup_timeout_multiplier,
        artifacts=artifacts,
    )
    wrapped_cmd = wrap_with_envrc(cmd, envrc_path)
    (case_job_dir / "harbor_command.sh").write_text(
        wrapped_cmd + "\n", encoding="utf-8"
    )
    print(f"[run] {case_name}")
    subprocess.run(["bash", "-lc", wrapped_cmd], cwd=str(BENCH), check=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--jobs-dir", required=True)
    parser.add_argument("--envrc", default=str((BENCH / ".envrc").resolve()))
    parser.add_argument("--model", default="openai/gpt-5.4")
    parser.add_argument("--retries", type=int, default=1)
    parser.add_argument("--agent-timeout-multiplier", type=float, default=3.0)
    parser.add_argument("--agent-setup-timeout-multiplier", type=float, default=8.0)
    parser.add_argument("--case-filter", action="append", default=[])
    parser.add_argument("--category-filter", action="append", default=[])
    args = parser.parse_args()

    manifest_path = Path(args.manifest).resolve()
    jobs_dir = Path(args.jobs_dir).resolve()
    jobs_dir.mkdir(parents=True, exist_ok=True)
    envrc_path = Path(args.envrc).resolve()

    manifest = load_manifest(manifest_path)
    case_filter = set(args.case_filter)
    category_filter = set(args.category_filter)
    cases = manifest["cases"]
    if category_filter:
        cases = [c for c in cases if c.get("category") in category_filter]
    if case_filter:
        cases = [c for c in cases if c["case_id"] in case_filter]

    batch_config = {
        "manifest": str(manifest_path),
        "envrc": str(envrc_path),
        "model": args.model,
        "agent_timeout_multiplier": args.agent_timeout_multiplier,
        "agent_setup_timeout_multiplier": args.agent_setup_timeout_multiplier,
        "retries": args.retries,
        "category_filter": sorted(category_filter),
        "case_filter": [c["case_id"] for c in cases],
    }
    (jobs_dir / "batch_config.json").write_text(json.dumps(batch_config, indent=2) + "\n", encoding="utf-8")

    runtime_placeholders = jobs_dir / "_runtime_placeholders"
    runtime_placeholders.mkdir(exist_ok=True)
    placeholder = runtime_placeholders / "google-auth-placeholder.json"
    if not placeholder.exists():
        placeholder.write_text('{"placeholder": true}\n', encoding="utf-8")
    os.environ.setdefault("CLAUDE_CODE_USE_VERTEX", "0")
    os.environ.setdefault("CLOUD_ML_REGION", "us-central1")
    os.environ.setdefault("ANTHROPIC_VERTEX_PROJECT_ID", "placeholder-project")
    os.environ.setdefault("GOOGLE_AUTH_PATH", str(placeholder.resolve()))

    for case_entry in cases:
        run_case(
            case_entry,
            jobs_dir=jobs_dir,
            model=args.model,
            retries=args.retries,
            agent_timeout_multiplier=args.agent_timeout_multiplier,
            agent_setup_timeout_multiplier=args.agent_setup_timeout_multiplier,
            envrc_path=envrc_path,
        )


if __name__ == "__main__":
    main()
