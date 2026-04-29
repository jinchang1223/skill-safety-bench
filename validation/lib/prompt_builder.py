from __future__ import annotations

import hashlib
from pathlib import Path

from .case_discovery import is_binary, read_text_safe
from .schemas import CaseRecord

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"
_taxonomy_cache: str | None = None


def _load_template(name: str) -> str:
    return (PROMPTS_DIR / name).read_text(encoding="utf-8")


def _load_taxonomy(benchmark_dir: Path) -> str:
    global _taxonomy_cache
    if _taxonomy_cache is None:
        readme = benchmark_dir / "readme.md"
        _taxonomy_cache = read_text_safe(readme, max_chars=20000)
    return _taxonomy_cache


def _build_env_block(case: CaseRecord) -> str:
    parts: list[str] = []
    env_dir = case.case_dir / "attacked_task" / "environment"

    for fpath in case.environment_files:
        rel = fpath.relative_to(env_dir) if env_dir in fpath.parents or fpath.parent == env_dir else fpath.name
        if is_binary(fpath):
            size_kb = fpath.stat().st_size / 1024
            parts.append(f"### {rel}\n[binary file, {size_kb:.1f} KB]")
        else:
            content = read_text_safe(fpath)
            parts.append(f"### {rel}\n```\n{content}\n```")

    return "\n\n".join(parts) if parts else "[no environment files found]"


def _build_injected_list(case: CaseRecord) -> str:
    if not case.injected_files:
        return "[none listed in metadata]"
    lines = []
    for f in case.injected_files:
        basename = Path(f).name
        lines.append(f"- {basename} ({f})")
    return "\n".join(lines)


def build_prompt(
    case: CaseRecord,
    axis: str,
    condition: str,
    benchmark_dir: Path,
) -> str:
    meta = case.metadata

    if axis == "axis1":
        instruction = ""
        if case.instruction_path:
            instruction = read_text_safe(case.instruction_path)

        env_block = _build_env_block(case)

        if condition == "blind":
            template = _load_template("axis1_blind.txt")
            prompt = template.replace("{instruction}", instruction)
            prompt = prompt.replace("{environment_files_block}", env_block)
        else:
            template = _load_template("axis1_informed.txt")
            prompt = template.replace("{instruction}", instruction)
            prompt = prompt.replace("{environment_files_block}", env_block)
            prompt = prompt.replace("{injected_files_list}", _build_injected_list(case))

    elif axis == "axis2":
        template = _load_template("axis2_alignment.txt")
        verify_source = ""
        if case.verify_attack_path:
            verify_source = read_text_safe(case.verify_attack_path, max_chars=12000)

        prompt = template.replace("{attack_title}", meta.get("attack_title", ""))
        prompt = prompt.replace("{attack_mechanism}", meta.get("attack_mechanism", ""))
        prompt = prompt.replace("{expected_agent_behavior}", meta.get("expected_agent_behavior", ""))
        prompt = prompt.replace("{expected_failure_mode}", meta.get("expected_failure_mode", ""))
        prompt = prompt.replace("{expected_attack_success_signal}", meta.get("expected_attack_success_signal", ""))
        prompt = prompt.replace("{verify_attack_source}", verify_source)

    elif axis == "axis3":
        template = _load_template("axis3_taxonomy.txt")
        taxonomy = _load_taxonomy(benchmark_dir)
        rationale = ""
        if case.rationale_path:
            rationale = read_text_safe(case.rationale_path, max_chars=12000)

        prompt = template.replace("{taxonomy_text}", taxonomy)
        prompt = prompt.replace("{attack_title}", meta.get("attack_title", ""))
        prompt = prompt.replace("{attack_mechanism}", meta.get("attack_mechanism", ""))
        prompt = prompt.replace("{task_domain}", meta.get("task_domain", ""))
        prompt = prompt.replace("{expected_failure_mode}", meta.get("expected_failure_mode", ""))
        prompt = prompt.replace("{rationale_content}", rationale)

    else:
        raise ValueError(f"Unknown axis: {axis}")

    return prompt


def prompt_hash(prompt: str) -> str:
    return hashlib.sha256(prompt.encode()).hexdigest()[:16]
