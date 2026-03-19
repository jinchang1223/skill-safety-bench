from __future__ import annotations

from pathlib import Path

from models import MaterializationResult


def append_block(path: Path, block: str, result: MaterializationResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    original = path.read_text(encoding="utf-8") if path.exists() else ""
    if block in original:
        return
    new_text = original.rstrip() + "\n\n" + block.rstrip() + "\n"
    path.write_text(new_text, encoding="utf-8")
    _mark_modified(path, result)


def prepend_block(path: Path, block: str, result: MaterializationResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    original = path.read_text(encoding="utf-8") if path.exists() else ""
    if block in original:
        return
    new_text = block.rstrip() + "\n\n" + original.lstrip()
    path.write_text(new_text, encoding="utf-8")
    _mark_modified(path, result)


def write_file(path: Path, content: str, result: MaterializationResult, executable: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")
    if executable:
        path.chmod(0o755)
    result.created_files.append(path)


def ensure_dockerfile_runtime_support(
    dockerfile_path: Path,
    copy_source: str,
    copy_dest: str,
    env_line: str,
    result: MaterializationResult,
) -> None:
    original = dockerfile_path.read_text(encoding="utf-8")
    fragments = [
        f"COPY {copy_source} {copy_dest}",
        env_line,
    ]
    if all(fragment in original for fragment in fragments):
        return
    injected = original.rstrip() + "\n\n# SkillSafetyBench runtime payloads\n"
    if fragments[0] not in original:
        injected += fragments[0] + "\n"
    if fragments[1] not in original:
        injected += fragments[1] + "\n"
    dockerfile_path.write_text(injected, encoding="utf-8")
    _mark_modified(dockerfile_path, result)


def _mark_modified(path: Path, result: MaterializationResult) -> None:
    if path not in result.modified_files:
        result.modified_files.append(path)
