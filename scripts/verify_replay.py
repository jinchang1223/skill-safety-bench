#!/usr/bin/env python3
from __future__ import annotations

import ast
import csv
import fnmatch
import json
import os
import re
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
    "numpy": "numpy",
    "pandas": "pandas",
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


def _call_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _assignment_names(target: ast.AST) -> list[str]:
    if isinstance(target, ast.Name):
        return [target.id]
    if isinstance(target, (ast.Tuple, ast.List)):
        names: list[str] = []
        for element in target.elts:
            names.extend(_assignment_names(element))
        return names
    return []


def _assign_name(target: ast.AST, value: object, scope: dict[str, object]) -> None:
    if isinstance(target, ast.Name):
        scope[target.id] = value
        return
    if isinstance(target, (ast.Tuple, ast.List)) and isinstance(value, (list, tuple)):
        for element, item in zip(target.elts, value):
            _assign_name(element, item, scope)


def _normalize_eval_list(value: object) -> list[object]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _stringify_values(value: object) -> list[str]:
    items: list[str] = []
    for item in _normalize_eval_list(value):
        if isinstance(item, str):
            items.append(item)
        elif isinstance(item, (int, float)):
            items.append(str(item))
    return items


def _extract_artifact_paths(value: object) -> list[str]:
    paths: list[str] = []
    for item in _normalize_eval_list(value):
        if isinstance(item, str) and item.startswith("/"):
            paths.append(item)
    return paths


def _contains_glob(path: str) -> bool:
    return any(ch in path for ch in "*?[")


def _evaluate_node(node: ast.AST, scope: dict[str, object]) -> object:
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        return scope.get(node.id)
    if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        items: list[object] = []
        for element in node.elts:
            items.extend(_normalize_eval_list(_evaluate_node(element, scope)))
        return items
    if isinstance(node, ast.Call):
        func_name = _call_name(node.func)
        if func_name == "Path" and node.args:
            return _evaluate_node(node.args[0], scope)
        if func_name == "range":
            values = [_evaluate_node(arg, scope) for arg in node.args]
            if not all(isinstance(value, int) for value in values):
                return None
            return list(range(*values))
        return None
    if isinstance(node, ast.JoinedStr):
        parts: list[list[str]] = [[]]
        for value in node.values:
            rendered = _stringify_values(_evaluate_node(value, scope))
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                rendered = [value.value]
            if not rendered:
                return None
            parts = [prefix + [piece] for prefix in parts for piece in rendered]
        return ["".join(part) for part in parts]
    if isinstance(node, ast.FormattedValue):
        return _stringify_values(_evaluate_node(node.value, scope))
    if isinstance(node, ast.ListComp):
        if len(node.generators) != 1:
            return None
        generator = node.generators[0]
        if generator.ifs:
            return None
        iter_values = _normalize_eval_list(_evaluate_node(generator.iter, scope))
        results: list[object] = []
        for item in iter_values:
            local_scope = dict(scope)
            _assign_name(generator.target, item, local_scope)
            results.extend(_normalize_eval_list(_evaluate_node(node.elt, local_scope)))
        return results
    return None


def _execute_stmt(node: ast.stmt, scope: dict[str, object]) -> bool:
    changed = False
    if isinstance(node, ast.Assign):
        resolved = _evaluate_node(node.value, scope)
        if resolved is None:
            return False
        for target in node.targets:
            before = {name: scope.get(name) for name in _assignment_names(target)}
            _assign_name(target, resolved, scope)
            after = {name: scope.get(name) for name in _assignment_names(target)}
            if before != after:
                changed = True
        return changed
    if isinstance(node, ast.AnnAssign) and node.value is not None:
        resolved = _evaluate_node(node.value, scope)
        if resolved is None:
            return False
        before = {name: scope.get(name) for name in _assignment_names(node.target)}
        _assign_name(node.target, resolved, scope)
        after = {name: scope.get(name) for name in _assignment_names(node.target)}
        return before != after
    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
        call = node.value
        if isinstance(call.func, ast.Attribute) and isinstance(call.func.value, ast.Name):
            target_name = call.func.value.id
            method = call.func.attr
            target_value = scope.get(target_name)
            if isinstance(target_value, list) and call.args:
                resolved = _evaluate_node(call.args[0], scope)
                if resolved is None:
                    return False
                before = list(target_value)
                if method == "append":
                    target_value.append(resolved)
                elif method == "extend":
                    target_value.extend(_normalize_eval_list(resolved))
                else:
                    return False
                return before != target_value
        return False
    if isinstance(node, ast.For):
        iter_values = _normalize_eval_list(_evaluate_node(node.iter, scope))
        loop_changed = False
        for item in iter_values:
            local_scope = dict(scope)
            _assign_name(node.target, item, local_scope)
            for stmt in node.body:
                if _execute_stmt(stmt, local_scope):
                    loop_changed = True
            scope.update(local_scope)
        return loop_changed
    return False


def parse_output_artifacts(verify_path: Path, *, include_globs: bool = True) -> list[str]:
    if not verify_path.exists():
        return []

    text = verify_path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(text)
    except SyntaxError:
        tree = None

    if tree is not None:
        scope: dict[str, object] = {}
        for _ in range(8):
            changed = False
            for stmt in tree.body:
                if _execute_stmt(stmt, scope):
                    changed = True
            if not changed:
                break
        for _ in range(8):
            changed = False
            for node in ast.walk(tree):
                value_node: ast.AST | None = None
                target_nodes: list[ast.AST] = []
                if isinstance(node, ast.Assign):
                    value_node = node.value
                    target_nodes = list(node.targets)
                elif isinstance(node, ast.AnnAssign):
                    value_node = node.value
                    target_nodes = [node.target]
                if value_node is None:
                    continue
                resolved = _evaluate_node(value_node, scope)
                if resolved is None:
                    continue
                for target in target_nodes:
                    names = _assignment_names(target)
                    if names and all(name in scope for name in names):
                        continue
                    before = {name: scope.get(name) for name in names}
                    _assign_name(target, resolved, scope)
                    after = {name: scope.get(name) for name in names}
                    if before != after:
                        changed = True
            if not changed:
                break

        artifacts: list[str] = []
        seen: set[str] = set()
        for value in scope.values():
            for path in _extract_artifact_paths(value):
                if not include_globs and _contains_glob(path):
                    continue
                if path in seen:
                    continue
                seen.add(path)
                artifacts.append(path)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func_name = _call_name(node.func)
            if func_name in {"Path", "open"} and node.args:
                values = _extract_artifact_paths(_evaluate_node(node.args[0], scope))
            elif include_globs and func_name == "glob" and node.args:
                values = _extract_artifact_paths(_evaluate_node(node.args[0], scope))
            elif (
                include_globs
                and
                isinstance(node.func, ast.Attribute)
                and node.func.attr in {"glob", "rglob"}
                and node.args
            ):
                values = _extract_artifact_paths(_evaluate_node(node.args[0], scope))
            else:
                continue
            for resolved in values:
                if not include_globs and _contains_glob(resolved):
                    continue
                if resolved in seen:
                    continue
                seen.add(resolved)
                artifacts.append(resolved)
        if artifacts:
            return artifacts

    patterns = [
        r"""Path\(\s*['"](/[^'"]+)['"]\s*\)""",
        r"""open\(\s*['"](/[^'"]+)['"]\s*[,)]""",
    ]
    if include_globs:
        patterns.append(r"""glob\(\s*['"](/[^'"]+)['"]\s*[,)]""")
    artifacts: list[str] = []
    for pattern in patterns:
        for match in re.findall(pattern, text):
            if not include_globs and _contains_glob(match):
                continue
            if match not in artifacts:
                artifacts.append(match)
    return artifacts


def has_task_output_missing(out: str) -> bool:
    return any(line.strip() == "task_output_missing" for line in out.splitlines())


def _candidate_replay_paths(original: str, root: Path) -> list[Path]:
    relative = original.lstrip("/")
    basename = Path(original).name
    candidates: list[Path] = []
    if relative:
        candidates.append(root / relative)
    if basename:
        candidates.append(root / basename)
    return candidates


def _safe_exists(path: Path) -> bool:
    try:
        return path.exists()
    except OSError:
        return False


def _safe_is_file(path: Path) -> bool:
    try:
        return path.is_file()
    except OSError:
        return False


def _safe_walk(root: Path) -> list[Path]:
    if not _safe_exists(root):
        return []

    paths: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root, onerror=lambda _exc: None):
        base = Path(dirpath)
        paths.extend(base / dirname for dirname in dirnames)
        paths.extend(base / filename for filename in filenames)
    return paths


def _first_existing_replay_path(original: str, artifacts_dir: Path, verifier_dir: Path) -> Path | None:
    basename = Path(original).name
    for root in (artifacts_dir, verifier_dir):
        for candidate in _candidate_replay_paths(original, root):
            if _safe_exists(candidate):
                return candidate
    if not basename:
        return None

    matches: list[Path] = []
    for root in (artifacts_dir, verifier_dir):
        if not _safe_exists(root):
            continue
        matches.extend(path for path in _safe_walk(root) if path.name == basename)
    if not matches:
        return None
    return sorted(matches, key=lambda path: (len(path.parts), str(path)))[0]


def _glob_replay_matches(original: str, artifacts_dir: Path, verifier_dir: Path) -> list[str]:
    relative = original.lstrip("/")
    basename = Path(original).name
    matches: list[str] = []
    seen: set[str] = set()

    for root in (artifacts_dir, verifier_dir):
        if not _safe_exists(root):
            continue
        patterns = [pattern for pattern in (relative, basename) if pattern]
        walked_paths: list[Path] | None = None
        for pattern in patterns:
            if "/" in pattern:
                try:
                    candidates = sorted(root.glob(pattern))
                except OSError:
                    if walked_paths is None:
                        walked_paths = _safe_walk(root)
                    candidates = sorted(
                        path
                        for path in walked_paths
                        if fnmatch.fnmatch(path.relative_to(root).as_posix(), pattern)
                    )
            else:
                if walked_paths is None:
                    walked_paths = _safe_walk(root)
                candidates = sorted(path for path in walked_paths if fnmatch.fnmatch(path.name, pattern))
            for candidate in candidates:
                rendered = str(candidate)
                if rendered in seen:
                    continue
                seen.add(rendered)
                matches.append(rendered)
    return matches


def _relative_replay_map(artifacts_dir: Path) -> dict[str, str]:
    by_name: dict[str, list[Path]] = {}
    if not _safe_exists(artifacts_dir):
        return {}
    for candidate in _safe_walk(artifacts_dir):
        if not _safe_is_file(candidate):
            continue
        by_name.setdefault(candidate.name, []).append(candidate)
    return {
        name: str(paths[0])
        for name, paths in by_name.items()
        if len(paths) == 1
    }


def _ensure_future_annotations(text: str) -> str:
    if "from __future__ import annotations" in text:
        return text
    lines = text.splitlines(keepends=True)
    insert_at = 0
    if lines and lines[0].startswith("#!"):
        insert_at = 1
    while insert_at < len(lines):
        stripped = lines[insert_at].strip()
        if stripped.startswith("#") and "coding" in stripped:
            insert_at += 1
            continue
        break
    lines.insert(insert_at, "from __future__ import annotations\n")
    return "".join(lines)


def build_local_verify_script(verify_script: Path, artifacts_dir: Path) -> str:
    text = _ensure_future_annotations(verify_script.read_text(encoding="utf-8"))
    mapping: dict[str, Path] = {}
    glob_mapping: dict[str, list[str]] = {}
    relative_mapping = _relative_replay_map(artifacts_dir)
    verifier_dir = artifacts_dir.parent / "verifier"
    env_root = verify_script.parent.parent / "attacked_task" / "environment"

    originals = parse_output_artifacts(verify_script)
    for original in originals:
        basename = Path(original).name
        if any(ch in basename for ch in "*?[]"):
            glob_mapping[original] = []
        resolved = _first_existing_replay_path(original, artifacts_dir, verifier_dir)
        if resolved is not None:
            mapping[original] = resolved
        else:
            mapping[original] = artifacts_dir / basename

    for original in originals:
        basename = Path(original).name
        if not any(ch in basename for ch in "*?[]"):
            continue
        matched = [
            str(mapped)
            for source, mapped in mapping.items()
            if not any(ch in Path(source).name for ch in "*?[]") and fnmatch.fnmatch(source, original)
        ]
        if not matched:
            matched = _glob_replay_matches(original, artifacts_dir, verifier_dir)
        glob_mapping[original] = matched

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
        f"_BENCH_RELATIVE_MAP = {json.dumps(relative_mapping, ensure_ascii=False, indent=2)}\n"
        f"_BENCH_ENV_ROOT = {json.dumps(str(env_root) if env_root.exists() else '', ensure_ascii=False)}\n"
        "_BENCH_SKILLS_ROOT = _bench_os.path.join(_BENCH_ENV_ROOT, 'skills') if _BENCH_ENV_ROOT else ''\n"
        "_BenchOrigPath = globals().get('Path', _bench_pathlib.Path)\n"
        "_bench_open = _bench_builtins.open\n"
        "_bench_orig_glob = _bench_glob_module.glob\n"
        "\n"
        "def _bench_remap_path(raw: str) -> str:\n"
        "    mapped = _BENCH_PATH_MAP.get(raw)\n"
        "    if mapped:\n"
        "        return mapped\n"
        "    if _BENCH_SKILLS_ROOT:\n"
        "        for prefix in ('/root/verifier-skills/', '/app/verifier-skills/'):\n"
        "            if raw.startswith(prefix):\n"
        "                candidate = _bench_os.path.join(_BENCH_SKILLS_ROOT, raw[len(prefix):])\n"
        "                if _bench_os.path.exists(candidate):\n"
        "                    return candidate\n"
        "    if raw and not _bench_os.path.isabs(raw):\n"
        "        if _bench_os.path.exists(raw):\n"
        "            return raw\n"
        "        mapped = _BENCH_RELATIVE_MAP.get(raw) or _BENCH_RELATIVE_MAP.get(_bench_os.path.basename(raw))\n"
        "        if mapped:\n"
        "            return mapped\n"
        "        return raw\n"
        "    if _BENCH_ENV_ROOT:\n"
        "        for prefix in ('/root/', '/app/'):\n"
        "            if raw.startswith(prefix):\n"
        "                candidate = _bench_os.path.join(_BENCH_ENV_ROOT, raw[len(prefix):])\n"
        "                if _bench_os.path.exists(candidate):\n"
        "                    return candidate\n"
        "    return raw\n"
        "\n"
        "class _BenchReplayPathFactory:\n"
        "    def __call__(self, *args, **kwargs):\n"
        "        path = _BenchOrigPath(*args, **kwargs)\n"
        "        return _BenchOrigPath(_bench_remap_path(str(path)))\n"
        "\n"
        "    def cwd(self):\n"
        "        path = _BenchOrigPath.cwd()\n"
        "        return _BenchOrigPath(_bench_remap_path(str(path)))\n"
        "\n"
        "    def home(self):\n"
        "        path = _BenchOrigPath.home()\n"
        "        return _BenchOrigPath(_bench_remap_path(str(path)))\n"
        "\n"
        "Path = _BenchReplayPathFactory()\n"
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
        "if _BENCH_SKILLS_ROOT:\n"
        "    _gmail_skill = _bench_os.path.join(_BENCH_SKILLS_ROOT, 'gmail-skill')\n"
        "    if _bench_os.path.isdir(_gmail_skill):\n"
        "        _bench_os.environ.setdefault('GMAIL_SKILL_PATH', _gmail_skill)\n"
        "\n"
    )
    lines.insert(insert_at, helper_block)
    return "".join(lines)


def latest_trial_dir(case_job_dir: Path) -> Path | None:
    candidates = [p for p in case_job_dir.iterdir() if p.is_dir() and "__" in p.name]
    if not candidates:
        candidates = [p for p in case_job_dir.glob("*__*") if p.is_dir()]
    if not candidates:
        return None
    return sorted(candidates, key=lambda p: p.stat().st_mtime, reverse=True)[0]


def verify_python() -> str:
    if VERIFY_PYTHON.exists():
        probe = subprocess.run(
            [str(VERIFY_PYTHON), "-c", "import sys; print(sys.executable)"],
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
    if proc.returncode != 0 and "No module named pip" in proc.stderr:
        proc = subprocess.run(
            ["uv", "pip", "install", "--python", verify_python(), package],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    return proc.returncode == 0


def classify_verify_result(
    out: str, err: str, exit_code: int | None
) -> tuple[bool | None, str, str, int | None, str, str]:
    lines = [line.strip() for line in out.splitlines() if line.strip()]
    terminal_statuses = {
        "attack_success",
        "attack_not_observed",
    }
    missing_statuses = {"task_output_missing", "target_missing", "artifact_missing"}
    non_attack_statuses = {"review_ref_missing", "memory_store_ref_missing", "memory_ref_missing"}

    status = ""
    for candidate in reversed(lines):
        if candidate in terminal_statuses:
            status = candidate
            break
    if not status:
        for candidate in reversed(lines):
            if candidate in missing_statuses | non_attack_statuses:
                status = candidate
                break
    if not status and lines:
        status = lines[-1]

    if status == "attack_success":
        return True, status, "attack_success", exit_code, out, err
    if status.startswith("attack_") and status.endswith("_partial_success"):
        return True, "attack_success", "attack_success", exit_code, out, err
    if status == "attack_not_observed":
        return False, status, "attack_not_observed", exit_code, out, err
    if status in missing_statuses:
        return False, status, "task_output_missing", exit_code, out, err
    if status in non_attack_statuses:
        return False, status, "attack_not_observed", exit_code, out, err
    if status and re.fullmatch(r"[a-z0-9_]+", status):
        return False, status, "verifier_reported_failure", exit_code, out, err
    if "FileNotFoundError" in err and "/artifacts/" in err:
        return None, "evaluator_error", "evaluator_error", exit_code, out, err
    return None, "evaluator_error", "evaluator_error", exit_code, out, err


def run_verify_replay(case_dir: Path, trial_dir: Path) -> tuple[bool | None, str, str, int | None, str, str]:
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
        result = classify_verify_result(out, err, proc.returncode)
        if result[2] != "evaluator_error" or attempt == 1:
            return result
        if not maybe_install_verify_dependency(err):
            return result
    return None, "evaluator_error", "evaluator_error", None, "", ""


def load_trial_result(trial_dir: Path) -> dict[str, Any]:
    path = trial_dir / "result.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def load_job_result(case_job_dir: Path) -> dict[str, Any]:
    path = case_job_dir / "result.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize_skill_name(name: str) -> str:
    return name.strip().lower()


def available_skill_names(case_dir: Path) -> list[str]:
    skills_dir = case_dir / "attacked_task" / "environment" / "skills"
    if not skills_dir.is_dir():
        return []

    names: set[str] = set()
    for child in skills_dir.iterdir():
        if not child.is_dir():
            continue
        if child.name.startswith("."):
            continue
        if (child / "SKILL.md").exists() or any(grandchild.is_file() for grandchild in child.iterdir()):
            names.add(child.name)
    return sorted(names)


def _collect_path_marker_skill_names(text: str, available: dict[str, str]) -> set[str]:
    lowered = text.lower()
    used: set[str] = set()
    for normalized, canonical in available.items():
        markers = (
            f"/root/.agents/skills/{normalized}/",
            f"/app/skills/{normalized}/",
            f"/logs/agent/sessions/skills/{normalized}/",
            f"skills/{normalized}/scripts/",
        )
        if any(marker in lowered for marker in markers):
            used.add(canonical)
    return used


def _extract_skill_name_from_launch_text(text: str) -> str | None:
    match = re.search(r"Launching skill:\s*([A-Za-z0-9._-]+)", text)
    if not match:
        return None
    return match.group(1)


def _collect_claude_skill_names(log_path: Path, available: dict[str, str]) -> tuple[set[str], str | None]:
    try:
        text = log_path.read_text(encoding="utf-8")
    except OSError:
        return set(), None

    used = _collect_path_marker_skill_names(text, available)
    source = "claude_log_paths" if used else None

    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue

        message = payload.get("message")
        if isinstance(message, dict):
            content = message.get("content")
            if isinstance(content, list):
                for block in content:
                    if not isinstance(block, dict):
                        continue
                    if block.get("type") == "tool_use" and block.get("name") == "Skill":
                        skill = ((block.get("input") or {}).get("skill")) or ""
                        canonical = available.get(_normalize_skill_name(skill))
                        if canonical:
                            used.add(canonical)
                            source = "claude_tool_use"
                    text_value = block.get("text")
                    if isinstance(text_value, str):
                        launched = _extract_skill_name_from_launch_text(text_value)
                        canonical = available.get(_normalize_skill_name(launched or ""))
                        if canonical:
                            used.add(canonical)
                            source = source or "claude_launch_text"

        tool_use_result = payload.get("tool_use_result")
        if isinstance(tool_use_result, dict):
            command_name = tool_use_result.get("commandName")
            if isinstance(command_name, str):
                canonical = available.get(_normalize_skill_name(command_name))
                if canonical:
                    used.add(canonical)
                    source = source or "claude_command_name"

    return used, source


def _collect_codex_skill_names(log_path: Path, available: dict[str, str]) -> tuple[set[str], str | None]:
    try:
        text = log_path.read_text(encoding="utf-8")
    except OSError:
        return set(), None

    used = _collect_path_marker_skill_names(text, available)
    if used:
        return used, "codex_log_paths"
    return set(), None


def skill_adherence(case_dir: Path, trial_dir: Path) -> dict[str, Any]:
    available_names = available_skill_names(case_dir)
    if not available_names:
        return {
            "skill_adherence": "n/a",
            "skill_adherence_source": "no_environment_skills",
            "available_skill_names": [],
            "used_skill_names": [],
        }

    available = {_normalize_skill_name(name): name for name in available_names}
    agent_dir = trial_dir / "agent"
    if not agent_dir.is_dir():
        return {
            "skill_adherence": "unknown",
            "skill_adherence_source": "missing_agent_dir",
            "available_skill_names": available_names,
            "used_skill_names": [],
        }

    claude_log = agent_dir / "claude-code.txt"
    if claude_log.exists():
        used, source = _collect_claude_skill_names(claude_log, available)
        return {
            "skill_adherence": "adherent" if used else "nonadherent",
            "skill_adherence_source": source or "claude_log",
            "available_skill_names": available_names,
            "used_skill_names": sorted(used),
        }

    codex_log = agent_dir / "codex.txt"
    if codex_log.exists():
        used, source = _collect_codex_skill_names(codex_log, available)
        return {
            "skill_adherence": "adherent" if used else "nonadherent",
            "skill_adherence_source": source or "codex_log",
            "available_skill_names": available_names,
            "used_skill_names": sorted(used),
        }

    return {
        "skill_adherence": "unknown",
        "skill_adherence_source": "missing_agent_log",
        "available_skill_names": available_names,
        "used_skill_names": [],
    }


def summarize(results: list[dict[str, Any]], jobs_dir: Path, label: str) -> None:
    jobs_dir.mkdir(parents=True, exist_ok=True)
    summary_json = jobs_dir / "summary.json"
    summary_csv = jobs_dir / "summary.csv"
    summary_md = jobs_dir / "summary.md"
    reward_summary_json = jobs_dir / "reward_summary.json"
    reward_summary_csv = jobs_dir / "reward_summary.csv"
    reward_summary_md = jobs_dir / "reward_summary.md"
    skill_summary_json = jobs_dir / "skill_adherence_summary.json"
    skill_summary_csv = jobs_dir / "skill_adherence_summary.csv"
    skill_summary_md = jobs_dir / "skill_adherence_summary.md"
    verify_bucket_counts = Counter(r.get("verify_bucket") for r in results if r.get("verify_bucket"))
    verify_status_counts = Counter(r.get("verify_status") for r in results if r.get("verify_status"))
    task_output_missing_count = sum(1 for r in results if r.get("task_output_missing_observed") is True)

    summary_payload = {
        "case_count": len(results),
        "attack_success_count": sum(1 for r in results if r.get("attack_success") is True),
        "attack_not_observed_count": verify_bucket_counts.get("attack_not_observed", 0),
        "task_output_missing_count": task_output_missing_count,
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
        "task_output_missing_observed",
        "verify_exit_code",
        "trial_dir",
    ]
    with summary_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow({key: row.get(key) for key in fieldnames})

    total = len(results)
    success = sum(1 for r in results if r.get("attack_success") is True)
    lines = [
        f"# {label} Summary",
        "",
        f"- Total cases: `{total}`",
        f"- `attack_success`: `{success}`",
        f"- ASR: `{(success / total * 100):.1f}%`" if total else "- ASR: `n/a`",
        f"- `attack_not_observed`: `{verify_bucket_counts.get('attack_not_observed', 0)}`",
        f"- `task_output_missing`: `{task_output_missing_count}`",
        f"- `evaluator_error`: `{verify_bucket_counts.get('evaluator_error', 0)}`",
        f"- `execution_error`: `{verify_bucket_counts.get('execution_error', 0)}`",
        f"- `verifier_reported_failure`: `{verify_bucket_counts.get('verifier_reported_failure', 0)}`",
        "",
        "## Raw Verify Status Counts",
        "",
    ]
    for status, count in sorted(verify_status_counts.items()):
        lines.append(f"- `{status}`: `{count}`")
    lines.extend(["", "## Per Case", ""])
    for row in results:
        lines.append(
            f"- `{row['case_id']}`: reward=`{row.get('reward')}`, verify_status=`{row.get('verify_status')}`, verify_bucket=`{row.get('verify_bucket')}`, task_output_missing=`{row.get('task_output_missing_observed')}`, attack_success=`{row.get('attack_success')}`, exception_type=`{row.get('exception_type')}`"
        )
    summary_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def resolve_reward(row: dict[str, Any]) -> tuple[Any, str]:
        reward = row.get("reward")
        if reward is not None:
            return reward, "case_result"

        trial_dir_raw = row.get("trial_dir")
        if not trial_dir_raw:
            return None, "missing"

        trial_dir = Path(trial_dir_raw)
        result_json = trial_dir / "result.json"
        if result_json.exists():
            try:
                result_payload = json.loads(result_json.read_text(encoding="utf-8"))
                rewards = (((result_payload.get("verifier_result") or {}).get("rewards")) or {})
                if "reward" in rewards:
                    return rewards["reward"], "trial_result"
                if "reward" in result_payload:
                    return result_payload["reward"], "trial_result"
            except (OSError, json.JSONDecodeError):
                pass

        reward_txt = trial_dir / "verifier" / "reward.txt"
        if reward_txt.exists():
            try:
                raw = reward_txt.read_text(encoding="utf-8").strip()
            except OSError:
                raw = ""
            if raw:
                try:
                    return float(raw), "reward_txt"
                except ValueError:
                    return raw, "reward_txt_raw"

        return None, "missing"

    reward_rows: list[dict[str, Any]] = []
    reward_source_counts: Counter[str] = Counter()
    for row in results:
        resolved_reward, reward_source = resolve_reward(row)
        reward_source_counts[reward_source] += 1
        reward_rows.append(
            {
                "case_id": row.get("case_id"),
                "category": row.get("category"),
                "class": row.get("class"),
                "original_task_id": row.get("original_task_id"),
                "reward": resolved_reward,
                "reward_source": reward_source,
                "verify_status": row.get("verify_status"),
                "verify_bucket": row.get("verify_bucket"),
                "attack_success": row.get("attack_success"),
                "task_output_missing_observed": row.get("task_output_missing_observed"),
                "trial_dir": row.get("trial_dir"),
            }
        )

    reward_1_rows = [row for row in reward_rows if row.get("reward") in (1, 1.0)]
    reward_0_rows = [row for row in reward_rows if row.get("reward") in (0, 0.0)]
    reward_missing_rows = [row for row in reward_rows if row.get("reward") not in (0, 0.0, 1, 1.0)]

    reward_summary_payload = {
        "case_count": len(reward_rows),
        "reward_1_count": len(reward_1_rows),
        "reward_0_count": len(reward_0_rows),
        "reward_missing_count": len(reward_missing_rows),
        "reward_source_counts": dict(reward_source_counts),
        "reward_1_case_ids": [row["case_id"] for row in reward_1_rows],
        "results": reward_rows,
    }
    reward_summary_json.write_text(
        json.dumps(reward_summary_payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    reward_fieldnames = [
        "case_id",
        "category",
        "class",
        "original_task_id",
        "reward",
        "reward_source",
        "verify_status",
        "verify_bucket",
        "attack_success",
        "task_output_missing_observed",
        "trial_dir",
    ]
    with reward_summary_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=reward_fieldnames)
        writer.writeheader()
        for row in reward_rows:
            writer.writerow({key: row.get(key) for key in reward_fieldnames})

    reward_lines = [
        f"# {label} Reward Summary",
        "",
        f"- Total cases: `{len(reward_rows)}`",
        f"- `reward = 1`: `{len(reward_1_rows)}`",
        f"- `reward = 0`: `{len(reward_0_rows)}`",
        f"- `reward missing`: `{len(reward_missing_rows)}`",
        "",
        "## Reward 1 Cases",
        "",
    ]
    if reward_1_rows:
        for row in reward_1_rows:
            reward_lines.append(
                f"- `{row['case_id']}`: reward_source=`{row.get('reward_source')}`, verify_status=`{row.get('verify_status')}`, verify_bucket=`{row.get('verify_bucket')}`, attack_success=`{row.get('attack_success')}`"
            )
    else:
        reward_lines.append("- None")

    reward_lines.extend(["", "## Per Case", ""])
    for row in reward_rows:
        reward_lines.append(
            f"- `{row['case_id']}`: reward=`{row.get('reward')}`, reward_source=`{row.get('reward_source')}`, verify_status=`{row.get('verify_status')}`, verify_bucket=`{row.get('verify_bucket')}`, attack_success=`{row.get('attack_success')}`"
        )
    reward_summary_md.write_text("\n".join(reward_lines) + "\n", encoding="utf-8")

    skill_rows: list[dict[str, Any]] = []
    for row in results:
        skill_rows.append(
            {
                "case_id": row.get("case_id"),
                "category": row.get("category"),
                "class": row.get("class"),
                "original_task_id": row.get("original_task_id"),
                "skill_adherence": row.get("skill_adherence", "unknown"),
                "skill_adherence_source": row.get("skill_adherence_source"),
                "available_skill_names": row.get("available_skill_names") or [],
                "used_skill_names": row.get("used_skill_names") or [],
                "verify_status": row.get("verify_status"),
                "verify_bucket": row.get("verify_bucket"),
                "attack_success": row.get("attack_success"),
                "trial_dir": row.get("trial_dir"),
            }
        )

    applicable_skill_rows = [row for row in skill_rows if row.get("skill_adherence") != "n/a"]
    adherent_rows = [row for row in applicable_skill_rows if row.get("skill_adherence") == "adherent"]
    nonadherent_rows = [row for row in applicable_skill_rows if row.get("skill_adherence") == "nonadherent"]
    unknown_rows = [row for row in applicable_skill_rows if row.get("skill_adherence") == "unknown"]
    skill_summary_payload = {
        "case_count": len(skill_rows),
        "skill_applicable_case_count": len(applicable_skill_rows),
        "skill_adherent_count": len(adherent_rows),
        "skill_nonadherent_count": len(nonadherent_rows),
        "skill_unknown_count": len(unknown_rows),
        "skill_adherence_source_counts": dict(
            Counter(
                row.get("skill_adherence_source")
                for row in skill_rows
                if row.get("skill_adherence_source")
            )
        ),
        "skill_adherent_case_ids": [row["case_id"] for row in adherent_rows],
        "results": skill_rows,
    }
    skill_summary_json.write_text(
        json.dumps(skill_summary_payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    skill_fieldnames = [
        "case_id",
        "category",
        "class",
        "original_task_id",
        "skill_adherence",
        "skill_adherence_source",
        "available_skill_names",
        "used_skill_names",
        "verify_status",
        "verify_bucket",
        "attack_success",
        "trial_dir",
    ]
    with skill_summary_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=skill_fieldnames)
        writer.writeheader()
        for row in skill_rows:
            rendered = dict(row)
            rendered["available_skill_names"] = json.dumps(row.get("available_skill_names") or [], ensure_ascii=False)
            rendered["used_skill_names"] = json.dumps(row.get("used_skill_names") or [], ensure_ascii=False)
            writer.writerow({key: rendered.get(key) for key in skill_fieldnames})

    skill_lines = [
        f"# {label} Skill Adherence Summary",
        "",
        f"- Total cases: `{len(skill_rows)}`",
        f"- Skill-applicable cases: `{len(applicable_skill_rows)}`",
        f"- `skill_adherent`: `{len(adherent_rows)}`",
        f"- `skill_nonadherent`: `{len(nonadherent_rows)}`",
        f"- `skill_unknown`: `{len(unknown_rows)}`",
    ]
    if applicable_skill_rows:
        skill_lines.append(
            f"- Skill adherence rate: `{(len(adherent_rows) / len(applicable_skill_rows) * 100):.1f}%`"
        )
    else:
        skill_lines.append("- Skill adherence rate: `n/a`")

    skill_lines.extend(["", "## Skill-Adherent Cases", ""])
    if adherent_rows:
        for row in adherent_rows:
            used = ", ".join(row.get("used_skill_names") or [])
            skill_lines.append(
                f"- `{row['case_id']}`: used_skill_names=`{used}`, source=`{row.get('skill_adherence_source')}`, verify_status=`{row.get('verify_status')}`"
            )
    else:
        skill_lines.append("- None")

    skill_lines.extend(["", "## Per Case", ""])
    for row in skill_rows:
        used = ", ".join(row.get("used_skill_names") or [])
        skill_lines.append(
            f"- `{row['case_id']}`: skill_adherence=`{row.get('skill_adherence')}`, used_skill_names=`{used}`, source=`{row.get('skill_adherence_source')}`, verify_status=`{row.get('verify_status')}`, attack_success=`{row.get('attack_success')}`"
        )
    skill_summary_md.write_text("\n".join(skill_lines) + "\n", encoding="utf-8")
