from __future__ import annotations

import json
from pathlib import Path

from .schemas import CaseRecord

BINARY_EXTENSIONS = {
    ".xlsx", ".xls", ".docx", ".doc", ".pptx", ".ppt",
    ".pdf", ".png", ".jpg", ".jpeg", ".gif", ".bmp",
    ".zip", ".tar", ".gz", ".bz2", ".7z",
    ".pyc", ".pyo", ".so", ".dll", ".exe",
    ".sqlite", ".db",
}


def discover_cases(benchmark_dir: Path) -> list[CaseRecord]:
    cases: list[CaseRecord] = []
    benchmark_dir = benchmark_dir.resolve()

    for metadata_path in sorted(benchmark_dir.rglob("metadata.json")):
        case_dir = metadata_path.parent
        if "risk-domain-" not in str(case_dir):
            continue

        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue

        env_dir = case_dir / "attacked_task" / "environment"
        env_files = sorted(env_dir.rglob("*")) if env_dir.is_dir() else []
        env_files = [f for f in env_files if f.is_file()]

        rationale = case_dir / "rationale.md"
        verify = case_dir / "eval" / "verify_attack.py"
        instruction = case_dir / "attacked_task" / "instruction.md"

        cases.append(CaseRecord(
            case_id=metadata.get("case_id", case_dir.name),
            case_dir=case_dir,
            metadata=metadata,
            risk_domain=metadata.get("risk_domain", ""),
            risk_domain_name=metadata.get("risk_domain_name", ""),
            attack_category=metadata.get("attack_category", ""),
            attack_category_name=metadata.get("attack_category_name", ""),
            environment_files=env_files,
            injected_files=metadata.get("injected_or_modified_files", []),
            rationale_path=rationale if rationale.exists() else None,
            verify_attack_path=verify if verify.exists() else None,
            instruction_path=instruction if instruction.exists() else None,
        ))

    return cases


def is_binary(path: Path) -> bool:
    return path.suffix.lower() in BINARY_EXTENSIONS


def read_text_safe(path: Path, max_chars: int = 8000) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        if len(text) > max_chars:
            return text[:max_chars] + "\n[... truncated ...]"
        return text
    except OSError:
        return f"[error reading {path.name}]"
