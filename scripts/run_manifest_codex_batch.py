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
PROXY_ENV_KEYS = (
    "http_proxy",
    "https_proxy",
    "all_proxy",
    "no_proxy",
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "ALL_PROXY",
    "NO_PROXY",
)
APT_BOOTSTRAP_MARKER = "# SSB_APT_HTTPS_BOOTSTRAP"
APT_BOOTSTRAP_SNIPPET = """# SSB_APT_HTTPS_BOOTSTRAP
RUN set -eux; \\
    if [ -f /etc/apt/sources.list.d/ubuntu.sources ]; then \\
      sed -i 's|http://archive.ubuntu.com/ubuntu|https://archive.ubuntu.com/ubuntu|g; s|http://security.ubuntu.com/ubuntu|https://security.ubuntu.com/ubuntu|g' /etc/apt/sources.list.d/ubuntu.sources; \\
    fi; \\
    if [ -f /etc/apt/sources.list ]; then \\
      sed -i 's|http://deb.debian.org/debian|https://deb.debian.org/debian|g; s|http://security.debian.org/debian-security|https://security.debian.org/debian-security|g; s|http://archive.ubuntu.com/ubuntu|https://archive.ubuntu.com/ubuntu|g; s|http://security.ubuntu.com/ubuntu|https://security.ubuntu.com/ubuntu|g' /etc/apt/sources.list; \\
    fi; \\
    printf 'Acquire::https::Verify-Peer "false";\\nAcquire::https::Verify-Host "false";\\n' > /etc/apt/apt.conf.d/99ssb-bootstrap-insecure; \\
    apt-get update; \\
    DEBIAN_FRONTEND=noninteractive apt-get install -y ca-certificates openssl; \\
    rm -f /etc/apt/apt.conf.d/99ssb-bootstrap-insecure; \\
    apt-get update
"""


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


def maybe_patch_task_dockerfile(task_path: Path) -> None:
    dockerfile_path = task_path / "environment" / "Dockerfile"
    if not dockerfile_path.exists():
        return

    original = dockerfile_path.read_text(encoding="utf-8")
    if APT_BOOTSTRAP_MARKER in original or "apt-get update" not in original:
        return

    lines = original.splitlines()
    insert_at = None
    for idx, line in enumerate(lines):
        if line.lstrip().startswith("FROM "):
            insert_at = idx + 1
            break

    if insert_at is None:
        return

    patched_lines = lines[:insert_at] + ["", APT_BOOTSTRAP_SNIPPET.rstrip(), ""] + lines[insert_at:]
    dockerfile_path.write_text("\n".join(patched_lines) + "\n", encoding="utf-8")


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


def maybe_prefix_network_mode(command: str, network_mode: str | None) -> str:
    if not network_mode:
        return command
    return f"export NETWORK_MODE={shlex.quote(network_mode)}; {command}"


def run_case(
    case_entry: dict[str, Any],
    *,
    jobs_dir: Path,
    model: str,
    retries: int,
    agent_timeout_multiplier: float,
    agent_setup_timeout_multiplier: float | None,
    envrc_path: Path,
    network_mode: str | None,
) -> None:
    case_name = case_entry["case_id"]
    case_dir = resolve_bench_path(case_entry["case_path"])
    task_path = resolve_bench_path(case_entry.get("task_path", "")) if case_entry.get("task_path") else case_dir / "attacked_task"
    verify_path = case_dir / "eval" / "verify_attack.py"
    artifacts = parse_output_artifacts(verify_path)
    maybe_patch_task_dockerfile(task_path)

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
    cmd = maybe_prefix_network_mode(cmd, network_mode)
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
    parser.add_argument("--network-mode")
    parser.add_argument("--retries", type=int, default=1)
    parser.add_argument("--agent-timeout-multiplier", type=float, default=3.0)
    parser.add_argument("--agent-setup-timeout-multiplier", type=float, default=8.0)
    parser.add_argument("--case-filter", action="append", default=[])
    parser.add_argument("--category-filter", action="append", default=[])
    args = parser.parse_args()

    for key in PROXY_ENV_KEYS:
        os.environ.pop(key, None)

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
        "network_mode": args.network_mode,
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
            network_mode=args.network_mode,
        )


if __name__ == "__main__":
    main()
