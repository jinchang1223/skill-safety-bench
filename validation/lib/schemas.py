from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class CaseRecord:
    case_id: str
    case_dir: Path
    metadata: dict[str, Any]
    risk_domain: str
    risk_domain_name: str
    attack_category: str
    attack_category_name: str
    environment_files: list[Path]
    injected_files: list[str]
    rationale_path: Path | None = None
    verify_attack_path: Path | None = None
    instruction_path: Path | None = None


@dataclass
class JudgmentResult:
    case_id: str
    axis: str
    condition: str
    model_name: str
    score: int | None = None
    binary_result: str | None = None  # "pass" or "fail" for axis1/axis2
    predicted_domain: str | None = None
    predicted_category: str | None = None
    false_positive_risk: str | None = None
    false_negative_risk: str | None = None
    confidence: int | None = None
    rationale: str = ""
    raw_response: str = ""
    timestamp: str = ""
    prompt_hash: str = ""
