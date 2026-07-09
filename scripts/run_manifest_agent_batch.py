#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Any

from verify_replay import parse_output_artifacts


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
STAGED_TASKS_DIRNAME = "_staged_tasks"
ENVIRONMENT_MIRROR_SKIP = {
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "compose.yml",
    "compose.yaml",
    "__pycache__",
}
LOCAL_CALENDAR_FIXTURE_NAME = "calendar_events.json"
LOCAL_CALENDAR_FIXTURE_SCHEMA = "clawsentry.skills_safety_bench.local_calendar.v1"
VERIFIER_PATH_BOOTSTRAP_MARKER = "# SSB_VERIFIER_PATH_BOOTSTRAP"
VERIFIER_PATH_BOOTSTRAP_SNIPPET = """# SSB_VERIFIER_PATH_BOOTSTRAP
export PATH="${HOME}/.local/bin:/root/.local/bin:/usr/local/bin:/usr/bin:/bin:${PATH}"
mkdir -p "${HOME}/.local/bin" 2>/dev/null || true
[ -f "${HOME}/.local/bin/env" ] || : > "${HOME}/.local/bin/env" 2>/dev/null || true
ssb_python_path() {
  if command -v python3 >/dev/null 2>&1; then
    command -v python3
    return 0
  fi
  if command -v python >/dev/null 2>&1; then
    command -v python
    return 0
  fi
  return 1
}
ssb_python() {
  ssb_py="$(ssb_python_path)" || return 127
  "${ssb_py}" "$@"
}
ssb_run_limited() {
  if command -v timeout >/dev/null 2>&1; then
    timeout 45s "$@"
  else
    "$@"
  fi
}
ssb_run_quiet_limited() {
  ssb_run_limited "$@" >/dev/null 2>&1
}
ssb_real_curl="$(command -v curl 2>/dev/null || true)"
curl() {
  for ssb_curl_arg in "$@"; do
    case "${ssb_curl_arg}" in
      https://astral.sh/uv/*|https://github.com/astral-sh/uv/*|https://github.com/astral-sh/uv/releases/*)
        printf '%s\n' ':'
        return 0
        ;;
    esac
  done
  if [ -n "${ssb_real_curl}" ]; then
    ssb_run_limited "${ssb_real_curl}" "$@"
    return $?
  fi
  return 127
}
ssb_real_apt_get="$(command -v apt-get 2>/dev/null || true)"
ssb_apt_only_bootstrap_packages() {
  for ssb_apt_arg in "$@"; do
    case "${ssb_apt_arg}" in
      install|-y|--no-install-recommends|curl|ca-certificates) ;;
      *) return 1 ;;
    esac
  done
  return 0
}
apt-get() {
  if [ "${1:-}" = "update" ] && command -v curl >/dev/null 2>&1; then
    return 0
  fi
  if [ "${1:-}" = "install" ] && command -v curl >/dev/null 2>&1 && ssb_apt_only_bootstrap_packages "$@"; then
    return 0
  fi
  if [ -n "${ssb_real_apt_get}" ]; then
    ssb_run_quiet_limited "${ssb_real_apt_get}" "$@"
    return $?
  fi
  return 127
}
ssb_pip_install_quiet() {
  ssb_py="$(ssb_python_path)" || return 1
  ssb_run_quiet_limited "${ssb_py}" -m pip install --user -q "$@" || \
    ssb_run_quiet_limited "${ssb_py}" -m pip install --break-system-packages -q "$@" || \
    ssb_run_quiet_limited "${ssb_py}" -m pip install -q "$@" || \
    { command -v pip3 >/dev/null 2>&1 && ssb_run_quiet_limited pip3 install --user -q "$@"; } || \
    { command -v pip3 >/dev/null 2>&1 && ssb_run_quiet_limited pip3 install --break-system-packages -q "$@"; } || \
    { command -v pip3 >/dev/null 2>&1 && ssb_run_quiet_limited pip3 install -q "$@"; }
}
ssb_ensure_uvx() {
  if command -v uvx >/dev/null 2>&1; then
    return 0
  fi
  ssb_pip_install_quiet uv || true
  export PATH="${HOME}/.local/bin:/root/.local/bin:/usr/local/bin:/usr/bin:/bin:${PATH}"
  hash -r 2>/dev/null || true
  command -v uvx >/dev/null 2>&1
}
ssb_uvx_pytest_fallback() {
  ssb_uvx_packages=""
  while [ "$#" -gt 0 ]; do
    case "$1" in
      --with)
        shift
        [ "$#" -gt 0 ] || return 2
        ssb_uvx_packages="${ssb_uvx_packages}${ssb_uvx_packages:+ }$1"
        shift
        ;;
      --with=*)
        ssb_uvx_pkg="${1#--with=}"
        ssb_uvx_packages="${ssb_uvx_packages}${ssb_uvx_packages:+ }${ssb_uvx_pkg}"
        shift
        ;;
      pytest)
        shift
        if [ -n "${ssb_uvx_packages}" ]; then
          # shellcheck disable=SC2086
          ssb_pip_install_quiet ${ssb_uvx_packages} || true
        fi
        ssb_python -m pytest "$@"
        return $?
        ;;
      *)
        return 127
        ;;
    esac
  done
  return 127
}
uvx() {
  ssb_real_uvx="$(type -P uvx 2>/dev/null || true)"
  if [ -n "${ssb_real_uvx}" ]; then
    "${ssb_real_uvx}" "$@"
    return $?
  fi
  ssb_uvx_pytest_fallback "$@"
  ssb_uvx_status=$?
  if [ "${ssb_uvx_status}" -ne 127 ]; then
    return "${ssb_uvx_status}"
  fi
  if ssb_ensure_uvx; then
    ssb_real_uvx="$(type -P uvx 2>/dev/null || true)"
    if [ -n "${ssb_real_uvx}" ]; then
      "${ssb_real_uvx}" "$@"
      return $?
    fi
  fi
  return "${ssb_uvx_status}"
}"""
APT_BOOTSTRAP_MARKER = "# SSB_APT_HTTPS_BOOTSTRAP"
APT_BOOTSTRAP_SNIPPET = """# SSB_APT_HTTPS_BOOTSTRAP
RUN set -eux; \\
    if [ -f /etc/apt/sources.list.d/ubuntu.sources ]; then \\
      sed -i 's|http://archive.ubuntu.com/ubuntu|https://archive.ubuntu.com/ubuntu|g; s|http://security.ubuntu.com/ubuntu|https://security.ubuntu.com/ubuntu|g' /etc/apt/sources.list.d/ubuntu.sources; \\
    fi; \\
    if [ -f /etc/apt/sources.list.d/debian.sources ]; then \\
      sed -i 's|http://deb.debian.org/debian-security|https://deb.debian.org/debian-security|g; s|http://deb.debian.org/debian|https://deb.debian.org/debian|g; s|http://security.debian.org/debian-security|https://security.debian.org/debian-security|g' /etc/apt/sources.list.d/debian.sources; \\
    fi; \\
    if [ -f /etc/apt/sources.list ]; then \\
      sed -i 's|http://deb.debian.org/debian-security|https://deb.debian.org/debian-security|g; s|http://deb.debian.org/debian|https://deb.debian.org/debian|g; s|http://security.debian.org/debian-security|https://security.debian.org/debian-security|g; s|http://archive.ubuntu.com/ubuntu|https://archive.ubuntu.com/ubuntu|g; s|http://security.ubuntu.com/ubuntu|https://security.ubuntu.com/ubuntu|g' /etc/apt/sources.list; \\
    fi; \\
    printf 'Acquire::https::Verify-Peer "false";\\nAcquire::https::Verify-Host "false";\\n' > /etc/apt/apt.conf.d/99ssb-bootstrap-insecure; \\
    apt-get update; \\
    DEBIAN_FRONTEND=noninteractive apt-get install -y ca-certificates openssl; \\
    rm -f /etc/apt/apt.conf.d/99ssb-bootstrap-insecure; \\
    apt-get update
"""
GIT_LFS_PACKAGECLOUD_INSTALL = (
    "curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | bash && \\\n"
    "    apt-get install -y git-lfs"
)
GIT_LFS_APT_FIRST_INSTALL = (
    "set -eux; \\\n"
    "    apt-get update; \\\n"
    "    if ! apt-get install -y git-lfs; then \\\n"
    "      curl -fsSL https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | bash; \\\n"
    "      apt-get update; \\\n"
    "      apt-get install -y git-lfs; \\\n"
    "    fi"
)
_PREFETCHED_DOCKER_BASE_IMAGES: set[str] = set()
_REDUNDANT_RUNTIME_NODE_APT_PACKAGES = {"nodejs", "npm"}
_NODE_BUILD_COMMAND_RE = re.compile(r"(^|[\s;&|()])(?:node|npm|npx|corepack)(?=$|[\s;&|()])")


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


def _dockerfile_logical_lines(source: str) -> list[str]:
    logical_lines: list[str] = []
    current = ""
    for raw_line in source.splitlines():
        stripped_right = raw_line.rstrip()
        if not current:
            current = stripped_right
        else:
            current += " " + stripped_right.lstrip()
        if stripped_right.endswith("\\"):
            current = current[:-1].rstrip()
            continue
        logical_lines.append(current)
        current = ""
    if current:
        logical_lines.append(current)
    return logical_lines


def _dockerfile_invokes_node_during_build(source: str) -> bool:
    for logical_line in _dockerfile_logical_lines(source):
        stripped = logical_line.strip()
        if not stripped or stripped.startswith("#") or not stripped.upper().startswith("RUN "):
            continue
        command = stripped[4:]
        for segment in re.split(r"\s*(?:&&|;|\|\|)\s*", command):
            if "apt-get" in segment and re.search(r"\binstall\b", segment):
                continue
            if _NODE_BUILD_COMMAND_RE.search(segment):
                return True
    return False


def _remove_redundant_runtime_node_apt_packages(source: str) -> str:
    if _dockerfile_invokes_node_during_build(source):
        return source

    lines: list[str] = []
    changed = False
    for line in source.splitlines():
        package = line.strip().removesuffix("\\").strip()
        if package in _REDUNDANT_RUNTIME_NODE_APT_PACKAGES:
            changed = True
            continue
        lines.append(line)
    if not changed:
        return source
    return "\n".join(lines) + ("\n" if source.endswith("\n") else "")


def maybe_patch_task_dockerfile(task_path: Path) -> None:
    dockerfile_path = task_path / "environment" / "Dockerfile"
    if not dockerfile_path.exists():
        return

    original = dockerfile_path.read_text(encoding="utf-8")
    patched = original.replace(GIT_LFS_PACKAGECLOUD_INSTALL, GIT_LFS_APT_FIRST_INSTALL)
    patched = _remove_redundant_runtime_node_apt_packages(patched)

    if APT_BOOTSTRAP_MARKER in patched or "apt-get update" not in patched:
        if patched != original:
            dockerfile_path.write_text(patched, encoding="utf-8")
        return

    lines = patched.splitlines()
    insert_at = None
    for idx, line in enumerate(lines):
        if line.lstrip().startswith("FROM "):
            insert_at = idx + 1
            break

    if insert_at is None:
        if patched != original:
            dockerfile_path.write_text(patched, encoding="utf-8")
        return

    patched_lines = lines[:insert_at] + ["", APT_BOOTSTRAP_SNIPPET.rstrip(), ""] + lines[insert_at:]
    dockerfile_path.write_text("\n".join(patched_lines) + "\n", encoding="utf-8")


def _dockerfile_base_images(dockerfile_path: Path) -> list[str]:
    if not dockerfile_path.exists():
        return []
    images: list[str] = []
    seen: set[str] = set()
    for line in dockerfile_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = re.match(r"^FROM\s+(?:--platform=\S+\s+)?(\S+)", stripped)
        if not match:
            continue
        image = match.group(1)
        if image.lower() == "scratch" or "$" in image:
            continue
        if image not in seen:
            images.append(image)
            seen.add(image)
    return images


def _docker_image_available(image: str) -> bool:
    result = subprocess.run(
        ["docker", "image", "inspect", image],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def prefetch_dockerfile_base_images(task_path: Path) -> None:
    if os.environ.get("SSB_DOCKER_PREFETCH_BASE_IMAGES", "1").lower() in {
        "0",
        "false",
        "no",
        "off",
    }:
        return
    dockerfile_path = task_path / "environment" / "Dockerfile"
    for image in _dockerfile_base_images(dockerfile_path):
        if image in _PREFETCHED_DOCKER_BASE_IMAGES:
            continue
        _PREFETCHED_DOCKER_BASE_IMAGES.add(image)
        if _docker_image_available(image):
            continue
        result = subprocess.run(["docker", "pull", image], check=False)
        if result.returncode != 0:
            print(
                f"[warn] docker pull failed for base image {image}; continuing with compose build",
                file=sys.stderr,
                flush=True,
            )


def mirror_environment_payload_into_task_root(task_path: Path) -> None:
    env_dir = task_path / "environment"
    if not env_dir.exists():
        return

    for item in sorted(env_dir.iterdir()):
        if item.name in ENVIRONMENT_MIRROR_SKIP:
            continue
        destination = task_path / item.name
        if destination.exists():
            continue
        if item.is_dir():
            shutil.copytree(item, destination)
        else:
            shutil.copy2(item, destination)


def _task_has_calendar_skill(task_path: Path) -> bool:
    skills_dir = task_path / "environment" / "skills"
    if not skills_dir.exists():
        return False
    return any(path.name == "calendar-events-list.js" for path in skills_dir.rglob("*"))


def _local_calendar_fixture_payload() -> dict[str, Any]:
    return {
        "schema_version": LOCAL_CALENDAR_FIXTURE_SCHEMA,
        "events": [
            {
                "id": "work5a-busy-1",
                "summary": "Existing calendar hold",
                "start": {"dateTime": "2026-01-08T10:30:00-08:00"},
                "end": {"dateTime": "2026-01-08T11:30:00-08:00"},
            },
            {
                "id": "work5a-busy-2",
                "summary": "Existing external appointment",
                "start": {"dateTime": "2026-01-09T09:00:00-08:00"},
                "end": {"dateTime": "2026-01-09T10:00:00-08:00"},
            },
        ],
    }


def _patch_calendar_fixture_copy(task_path: Path) -> None:
    dockerfile_path = task_path / "environment" / "Dockerfile"
    if not dockerfile_path.exists():
        return
    text = dockerfile_path.read_text(encoding="utf-8")
    if LOCAL_CALENDAR_FIXTURE_NAME in text:
        return

    lines = text.splitlines()
    insert_at = None
    for idx, line in enumerate(lines):
        if line.lstrip().startswith("COPY skills "):
            insert_at = idx
            break
    if insert_at is None:
        for idx, line in enumerate(lines):
            if line.lstrip().startswith("FROM "):
                insert_at = idx + 1
                break
    if insert_at is None:
        return

    copy_line = f"COPY {LOCAL_CALENDAR_FIXTURE_NAME} /root/{LOCAL_CALENDAR_FIXTURE_NAME}"
    patched = lines[:insert_at] + [copy_line] + lines[insert_at:]
    dockerfile_path.write_text("\n".join(patched) + "\n", encoding="utf-8")


def stage_local_calendar_fixture_if_needed(task_path: Path) -> None:
    if not _task_has_calendar_skill(task_path):
        return

    payload = _local_calendar_fixture_payload()
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    for destination in (
        task_path / LOCAL_CALENDAR_FIXTURE_NAME,
        task_path / "environment" / LOCAL_CALENDAR_FIXTURE_NAME,
    ):
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(text, encoding="utf-8")
    _patch_calendar_fixture_copy(task_path)


def patch_verifier_test_path(task_path: Path) -> None:
    test_script = task_path / "tests" / "test.sh"
    if not test_script.exists():
        return
    original = test_script.read_text(encoding="utf-8")
    if VERIFIER_PATH_BOOTSTRAP_MARKER in original:
        return

    lines = original.splitlines()
    insert_at = 0
    if lines and lines[0].startswith("#!"):
        insert_at = 1
        if len(lines) > 1 and lines[1] == "":
            insert_at = 2

    patched_lines = (
        lines[:insert_at]
        + [VERIFIER_PATH_BOOTSTRAP_SNIPPET]
        + lines[insert_at:]
    )
    test_script.write_text("\n".join(patched_lines) + "\n", encoding="utf-8")


def stage_task_for_run(task_path: Path, jobs_dir: Path, case_name: str) -> Path:
    staged_root = jobs_dir / STAGED_TASKS_DIRNAME
    staged_root.mkdir(parents=True, exist_ok=True)
    staged_task_path = staged_root / case_name
    if staged_task_path.exists():
        shutil.rmtree(staged_task_path)
    shutil.copytree(task_path, staged_task_path)
    mirror_environment_payload_into_task_root(staged_task_path)
    stage_local_calendar_fixture_if_needed(staged_task_path)
    patch_verifier_test_path(staged_task_path)
    return staged_task_path


def build_harbor_command(
    *,
    task_path: Path,
    jobs_dir: Path,
    case_name: str,
    agent: str,
    model: str,
    reasoning_effort: str,
    retries: int,
    agent_timeout_multiplier: float,
    agent_setup_timeout_multiplier: float | None,
    agent_import_path: str,
    environment_import_path: str,
    agent_kwargs: list[str],
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
            f"-p {shlex.quote(str(task_path))}",
            f"-o {shlex.quote(str(jobs_dir))}",
            f"--job-name {shlex.quote(case_name)}",
        ]
    )
    if agent_import_path:
        parts.append(f"--agent-import-path {shlex.quote(agent_import_path)}")
    else:
        parts.append(f"-a {agent}")
    if model:
        parts.append(f"-m {shlex.quote(model)}")
    if environment_import_path:
        parts.append(f"--environment-import-path {shlex.quote(environment_import_path)}")
    if reasoning_effort:
        parts.append(f"--ak {shlex.quote(f'reasoning_effort={reasoning_effort}')}")
    for agent_kwarg in agent_kwargs:
        parts.append(f"--ak {shlex.quote(agent_kwarg)}")
    for artifact in artifacts:
        parts.append(f"--artifact {shlex.quote(artifact)}")
    return " ".join(parts)


_BROAD_HARBOR_ARTIFACT_DIRS = {
    ".",
    "/",
    "/app",
    "/etc",
    "/home",
    "/root",
    "/tmp",
    "/usr",
    "/var",
    "/workspace",
}
_BROAD_HOME_ARTIFACT_ROOT_NAMES = {"build", "workspace", "work", "project", "projects"}


def _contains_glob(path: str) -> bool:
    return any(ch in path for ch in "*?[]")


def _safe_glob_artifact_for_harbor(path: str) -> str | None:
    parent = str(Path(path).parent)
    if not parent or parent in _BROAD_HARBOR_ARTIFACT_DIRS:
        return None
    if not Path(parent).is_absolute():
        return None
    if _contains_glob(parent):
        return None
    if _is_broad_home_artifact_dir(parent):
        return None
    return parent


def _is_broad_home_artifact_dir(path: str) -> bool:
    parts = PurePosixPath(str(path or "")).parts
    if len(parts) < 4 or parts[0] != "/" or parts[1] != "home":
        return False
    root_name = parts[3]
    if root_name not in _BROAD_HOME_ARTIFACT_ROOT_NAMES:
        return False
    if len(parts) == 4:
        return True
    if len(parts) == 5 and parts[4] == "failed":
        return True
    if root_name == "build" and len(parts) <= 6 and parts[4] == "failed":
        return True
    return False


def normalize_artifacts_for_harbor(artifacts: list[str]) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for artifact in artifacts:
        candidate = artifact
        if _contains_glob(artifact):
            candidate = _safe_glob_artifact_for_harbor(artifact)
        if not candidate:
            continue
        if candidate in seen:
            continue
        seen.add(candidate)
        normalized.append(candidate)
    return normalized


def wrap_with_envrc(command: str, envrc_path: Path) -> str:
    quoted_envrc = shlex.quote(str(envrc_path))
    return (
        f"set -a; source {quoted_envrc}; set +a; "
        'if [ -n "${SSB_HARBOR_SHIM_DIR:-}" ] && [ -d "${SSB_HARBOR_SHIM_DIR}" ]; then '
        'export PATH="${SSB_HARBOR_SHIM_DIR}:${PATH}"; '
        "fi; "
        f"{command}"
    )


def maybe_prefix_network_mode(command: str, network_mode: str | None) -> str:
    if not network_mode:
        return command
    return f"export NETWORK_MODE={shlex.quote(network_mode)}; {command}"


def run_case(
    case_entry: dict[str, Any],
    *,
    jobs_dir: Path,
    agent: str,
    model: str,
    reasoning_effort: str,
    retries: int,
    agent_timeout_multiplier: float,
    agent_setup_timeout_multiplier: float | None,
    agent_import_path: str,
    environment_import_path: str,
    agent_kwargs: list[str],
    envrc_path: Path,
    network_mode: str | None,
) -> None:
    case_name = case_entry["case_id"]
    case_dir = resolve_bench_path(case_entry["case_path"])
    source_task_path = resolve_bench_path(case_entry.get("task_path", "")) if case_entry.get("task_path") else case_dir / "attacked_task"
    task_path = stage_task_for_run(source_task_path, jobs_dir, case_name)
    verify_path = case_dir / "eval" / "verify_attack.py"
    artifacts = normalize_artifacts_for_harbor(parse_output_artifacts(verify_path, include_globs=True))
    maybe_patch_task_dockerfile(task_path)
    prefetch_dockerfile_base_images(task_path)

    case_job_dir = jobs_dir / case_name
    if case_job_dir.exists():
        shutil.rmtree(case_job_dir)
    case_job_dir.mkdir(parents=True, exist_ok=True)

    cmd = build_harbor_command(
        task_path=task_path,
        jobs_dir=jobs_dir,
        case_name=case_name,
        agent=agent,
        model=model,
        reasoning_effort=reasoning_effort,
        retries=retries,
        agent_timeout_multiplier=agent_timeout_multiplier,
        agent_setup_timeout_multiplier=agent_setup_timeout_multiplier,
        agent_import_path=agent_import_path,
        environment_import_path=environment_import_path,
        agent_kwargs=agent_kwargs,
        artifacts=artifacts,
    )
    cmd = maybe_prefix_network_mode(cmd, network_mode)
    wrapped_cmd = wrap_with_envrc(cmd, envrc_path)
    (case_job_dir / "harbor_command.sh").write_text(
        wrapped_cmd + "\n", encoding="utf-8"
    )
    print(f"[run] {case_name}")
    subprocess.run(["bash", "-c", wrapped_cmd], cwd=str(BENCH), check=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--jobs-dir", required=True)
    parser.add_argument("--envrc", default=str((BENCH / ".envrc").resolve()))
    parser.add_argument("--agent", default=os.environ.get("SSB_AGENT", "codex"))
    parser.add_argument(
        "--model",
        default=os.environ.get("SSB_MODEL", ""),
    )
    parser.add_argument("--reasoning-effort", default=os.environ.get("SSB_REASONING_EFFORT", ""))
    parser.add_argument("--network-mode")
    parser.add_argument("--retries", type=int, default=1)
    parser.add_argument("--agent-timeout-multiplier", type=float, default=3.0)
    parser.add_argument("--agent-setup-timeout-multiplier", type=float, default=8.0)
    parser.add_argument("--agent-import-path", default="")
    parser.add_argument("--environment-import-path", default="")
    parser.add_argument("--agent-kwarg", action="append", default=[])
    parser.add_argument("--case-filter", action="append", default=[])
    parser.add_argument("--category-filter", action="append", default=[])
    args = parser.parse_args()

    manifest_path = Path(args.manifest).resolve()
    jobs_dir = Path(args.jobs_dir).resolve()
    jobs_dir.mkdir(parents=True, exist_ok=True)
    envrc_path = Path(args.envrc).resolve()

    if (
        os.environ.get("SSB_KEEP_PROXY_ENV") != "1"
        and os.environ.get("SSB_PRESERVE_PROXY_ENV") != "1"
    ):
        for key in PROXY_ENV_KEYS:
            os.environ.pop(key, None)

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
        "agent": args.agent,
        "model": args.model,
        "reasoning_effort": args.reasoning_effort,
        "network_mode": args.network_mode,
        "agent_timeout_multiplier": args.agent_timeout_multiplier,
        "agent_setup_timeout_multiplier": args.agent_setup_timeout_multiplier,
        "agent_import_path": args.agent_import_path,
        "environment_import_path": args.environment_import_path,
        "agent_kwargs": args.agent_kwarg,
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
            agent=args.agent,
            model=args.model,
            reasoning_effort=args.reasoning_effort,
            retries=args.retries,
            agent_timeout_multiplier=args.agent_timeout_multiplier,
            agent_setup_timeout_multiplier=args.agent_setup_timeout_multiplier,
            agent_import_path=args.agent_import_path,
            environment_import_path=args.environment_import_path,
            agent_kwargs=args.agent_kwarg,
            envrc_path=envrc_path,
            network_mode=args.network_mode,
        )


if __name__ == "__main__":
    main()
