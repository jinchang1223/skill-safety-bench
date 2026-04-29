from __future__ import annotations

import json
import re
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from .schemas import JudgmentResult


def _result_path(output_dir: Path, axis: str, condition: str, model_name: str, case_id: str) -> Path:
    return output_dir / axis / condition / model_name / f"{case_id}.json"


def is_completed(output_dir: Path, axis: str, condition: str, model_name: str, case_id: str) -> bool:
    p = _result_path(output_dir, axis, condition, model_name, case_id)
    if not p.exists():
        return False
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return "raw_response" in data and data["raw_response"]
    except (json.JSONDecodeError, OSError):
        return False


def save_result(output_dir: Path, result: JudgmentResult) -> Path:
    p = _result_path(output_dir, result.axis, result.condition, result.model_name, result.case_id)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(asdict(result), ensure_ascii=False, indent=2), encoding="utf-8")
    return p


def load_all_results(output_dir: Path) -> list[JudgmentResult]:
    results: list[JudgmentResult] = []
    for p in sorted(output_dir.rglob("*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            results.append(JudgmentResult(**{
                k: v for k, v in data.items()
                if k in JudgmentResult.__dataclass_fields__
            }))
        except (json.JSONDecodeError, OSError, TypeError):
            continue
    return results


def parse_judge_response(raw: str, axis: str) -> dict:
    json_match = re.search(r'\{[^{}]*\}', raw, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

    parsed: dict = {"_parse_failed": True}

    score_match = re.search(r'"?score"?\s*[:=]\s*(\d)', raw)
    if score_match:
        parsed["score"] = int(score_match.group(1))

    if axis == "axis3":
        domain_match = re.search(r'"?predicted_risk_domain"?\s*[:=]\s*"([^"]+)"', raw)
        if domain_match:
            parsed["predicted_risk_domain"] = domain_match.group(1)
        cat_match = re.search(r'"?predicted_attack_category"?\s*[:=]\s*"([^"]+)"', raw)
        if cat_match:
            parsed["predicted_attack_category"] = cat_match.group(1)

    rationale_match = re.search(r'"?rationale"?\s*[:=]\s*"([^"]*)"', raw, re.DOTALL)
    if rationale_match:
        parsed["rationale"] = rationale_match.group(1)

    return parsed


def build_judgment(
    case_id: str, axis: str, condition: str, model_name: str,
    raw_response: str, prompt_hash_val: str,
) -> JudgmentResult:
    parsed = parse_judge_response(raw_response, axis)
    now = datetime.now(timezone.utc).isoformat()

    result = JudgmentResult(
        case_id=case_id,
        axis=axis,
        condition=condition,
        model_name=model_name,
        raw_response=raw_response,
        timestamp=now,
        prompt_hash=prompt_hash_val,
        rationale=parsed.get("rationale", ""),
    )

    if axis in ("axis1", "axis2"):
        result.score = parsed.get("score")
    if axis == "axis2":
        result.false_positive_risk = parsed.get("false_positive_risk")
        result.false_negative_risk = parsed.get("false_negative_risk")
    if axis == "axis3":
        result.predicted_domain = parsed.get("predicted_risk_domain")
        result.predicted_category = parsed.get("predicted_attack_category")
        result.confidence = parsed.get("confidence")

    return result
