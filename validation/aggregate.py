#!/usr/bin/env python3
"""Aggregate LLM-as-a-Judge results into summary reports."""
from __future__ import annotations

import argparse
import csv
import json
import logging
import math
import sys
from collections import defaultdict
from io import StringIO
from pathlib import Path

from lib.result_store import load_all_results
from lib.schemas import JudgmentResult

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Krippendorff's alpha (self-contained, no external dependency)
# ---------------------------------------------------------------------------

def _krippendorff_alpha(units: list[dict[str, int | str]], metric: str = "ordinal") -> float | None:
    """Compute Krippendorff's alpha for a list of units.

    Each unit is a dict mapping rater_name -> value.
    metric: 'nominal' or 'ordinal'.
    """
    if not units:
        return None

    all_values: set = set()
    for u in units:
        all_values.update(u.values())
    if len(all_values) < 2:
        return None

    value_list = sorted(all_values, key=str)
    val_idx = {v: i for i, v in enumerate(value_list)}
    V = len(value_list)

    if metric == "nominal":
        delta = [[0.0 if i == j else 1.0 for j in range(V)] for i in range(V)]
    else:
        delta = [[(i - j) ** 2 for j in range(V)] for i in range(V)]

    Do = 0.0
    n_pairs_total = 0
    marginals = [0] * V

    for u in units:
        vals = list(u.values())
        m = len(vals)
        if m < 2:
            continue
        counts = [0] * V
        for v in vals:
            counts[val_idx[v]] += 1
            marginals[val_idx[v]] += 1

        for c in range(V):
            for k in range(V):
                if c != k:
                    Do += counts[c] * counts[k] * delta[c][k]
        n_pairs = m * (m - 1)
        n_pairs_total += n_pairs

    if n_pairs_total == 0:
        return None
    Do /= n_pairs_total

    n_total = sum(marginals)
    De = 0.0
    for c in range(V):
        for k in range(V):
            if c != k:
                De += marginals[c] * marginals[k] * delta[c][k]

    De_denom = n_total * (n_total - 1)
    if De_denom == 0:
        return None
    De /= De_denom

    if De == 0:
        return None
    return 1.0 - Do / De


# ---------------------------------------------------------------------------
# Bootstrap CI
# ---------------------------------------------------------------------------

import random


def _bootstrap_ci(values: list[float], n_boot: int = 2000, ci: float = 0.95) -> tuple[float, float]:
    if len(values) < 2:
        return (float("nan"), float("nan"))
    rng = random.Random(42)
    means = []
    for _ in range(n_boot):
        sample = [rng.choice(values) for _ in range(len(values))]
        means.append(sum(sample) / len(sample))
    means.sort()
    lo = int((1 - ci) / 2 * n_boot)
    hi = int((1 + ci) / 2 * n_boot)
    return (means[lo], means[min(hi, len(means) - 1)])


# ---------------------------------------------------------------------------
# Aggregation helpers
# ---------------------------------------------------------------------------

def _group_by(results: list[JudgmentResult], key) -> dict:
    groups = defaultdict(list)
    for r in results:
        groups[key(r)].append(r)
    return dict(groups)


def _aggregate_scores(results: list[JudgmentResult]) -> dict:
    scores = [r.score for r in results if r.score is not None]
    if not scores:
        return {"n": 0, "mean": None, "std": None, "ci_lo": None, "ci_hi": None}
    mean = sum(scores) / len(scores)
    var = sum((s - mean) ** 2 for s in scores) / len(scores)
    ci_lo, ci_hi = _bootstrap_ci([float(s) for s in scores])
    return {
        "n": len(scores),
        "mean": round(mean, 3),
        "std": round(math.sqrt(var), 3),
        "ci_lo": round(ci_lo, 3),
        "ci_hi": round(ci_hi, 3),
    }


def _aggregate_binary(results: list[JudgmentResult]) -> dict:
    valid = [r for r in results if r.binary_result in ("pass", "fail")]
    if not valid:
        return {"n": 0, "pass_rate": None, "pass_count": 0, "fail_count": 0}
    passes = sum(1 for r in valid if r.binary_result == "pass")
    return {
        "n": len(valid),
        "pass_rate": round(passes / len(valid), 3),
        "pass_count": passes,
        "fail_count": len(valid) - passes,
    }


# CONTINUE_MARKER


def _compute_alpha_for_axis(results: list[JudgmentResult], axis: str, condition: str) -> float | None:
    by_case = _group_by(
        [r for r in results if r.axis == axis and r.condition == condition],
        lambda r: r.case_id,
    )
    units = []
    for case_id, rs in by_case.items():
        unit = {}
        for r in rs:
            if axis == "axis3":
                val = r.predicted_domain
            else:
                val = r.binary_result
            if val is not None:
                unit[r.model_name] = val
        if len(unit) >= 2:
            units.append(unit)

    metric = "nominal"
    return _krippendorff_alpha(units, metric=metric)


def _axis3_accuracy(results: list[JudgmentResult], cases_meta: dict[str, dict]) -> dict:
    axis3 = [r for r in results if r.axis == "axis3"]
    domain_correct = 0
    category_correct = 0
    total = 0
    for r in axis3:
        meta = cases_meta.get(r.case_id, {})
        gt_domain = meta.get("risk_domain", "")
        gt_cat = meta.get("attack_category", "")
        if r.predicted_domain is None:
            continue
        total += 1
        pred_d = r.predicted_domain.lower().replace("-", "_").replace(" ", "_")
        gt_d = gt_domain.lower().replace("-", "_").replace(" ", "_")
        if pred_d == gt_d or pred_d in gt_d or gt_d in pred_d:
            domain_correct += 1
            pred_c = (r.predicted_category or "").lower().replace("-", "_").replace(" ", "_")
            gt_c = gt_cat.lower().replace("-", "_").replace(" ", "_")
            if pred_c == gt_c or pred_c in gt_c or gt_c in pred_c:
                category_correct += 1
    return {
        "total": total,
        "domain_accuracy": round(domain_correct / total, 3) if total else None,
        "category_accuracy": round(category_correct / total, 3) if total else None,
    }


# CONTINUE_MARKER_2


def _load_cases_meta(benchmark_dir: Path) -> dict[str, dict]:
    meta = {}
    for p in sorted(benchmark_dir.rglob("metadata.json")):
        if "risk-domain-" not in str(p):
            continue
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
            meta[d["case_id"]] = d
        except (json.JSONDecodeError, OSError, KeyError):
            continue
    return meta


def aggregate(results_dir: Path, benchmark_dir: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    results = load_all_results(results_dir)
    if not results:
        logger.error("No results found in %s", results_dir)
        sys.exit(1)

    logger.info("Loaded %d judgments", len(results))
    cases_meta = _load_cases_meta(benchmark_dir)

    report: dict = {"total_judgments": len(results), "axes": {}}

    for axis in ["axis1", "axis2", "axis3"]:
        axis_results = [r for r in results if r.axis == axis]
        if not axis_results:
            continue

        axis_report: dict = {}

        if axis == "axis1":
            cond_results = [r for r in axis_results if r.condition == "informed"]
            axis_report["informed"] = {
                "overall": _aggregate_binary(cond_results),
                "by_model": {
                    m: _aggregate_binary(rs)
                    for m, rs in _group_by(cond_results, lambda r: r.model_name).items()
                },
                "by_domain": {
                    d: _aggregate_binary(rs)
                    for d, rs in _group_by(cond_results, lambda r: cases_meta.get(r.case_id, {}).get("risk_domain_name", "unknown")).items()
                },
                "alpha": _compute_alpha_for_axis(cond_results, axis, "informed"),
            }

        elif axis == "axis2":
            axis_report["overall"] = _aggregate_binary(axis_results)
            axis_report["by_model"] = {
                m: _aggregate_binary(rs)
                for m, rs in _group_by(axis_results, lambda r: r.model_name).items()
            }
            axis_report["by_domain"] = {
                d: _aggregate_binary(rs)
                for d, rs in _group_by(axis_results, lambda r: cases_meta.get(r.case_id, {}).get("risk_domain_name", "unknown")).items()
            }
            axis_report["alpha"] = _compute_alpha_for_axis(axis_results, axis, "default")

        elif axis == "axis3":
            axis_report["accuracy"] = _axis3_accuracy(axis_results, cases_meta)
            axis_report["by_model"] = {}
            for m, rs in _group_by(axis_results, lambda r: r.model_name).items():
                axis_report["by_model"][m] = _axis3_accuracy(rs, cases_meta)
            axis_report["alpha"] = _compute_alpha_for_axis(axis_results, axis, "default")

        report["axes"][axis] = axis_report

    # Write JSON
    (output_dir / "report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Write markdown summary
    _write_markdown(report, output_dir / "report.md")

    logger.info("Reports written to %s", output_dir)


# CONTINUE_MARKER_3


def _write_markdown(report: dict, path: Path) -> None:
    lines = ["# LLM-as-a-Judge Validation Report", ""]
    lines.append(f"Total judgments: {report['total_judgments']}")
    lines.append("")

    for axis, data in report.get("axes", {}).items():
        lines.append(f"## {axis.upper()}")
        lines.append("")

        if axis == "axis1":
            cd = data.get("informed", {})
            ov = cd.get("overall", {})
            lines.append(f"### Informed Condition (Camouflage Quality)")
            lines.append(f"- Pass rate: {ov.get('pass_rate')} ({ov.get('pass_count')} pass / {ov.get('fail_count')} fail, n={ov.get('n')})")
            lines.append(f"- Krippendorff alpha: {cd.get('alpha')}")
            lines.append("")
            lines.append("| Model | Pass Rate | Pass | Fail | N |")
            lines.append("|-------|-----------|------|------|---|")
            for m, ms in cd.get("by_model", {}).items():
                lines.append(f"| {m} | {ms.get('pass_rate')} | {ms.get('pass_count')} | {ms.get('fail_count')} | {ms.get('n')} |")
            lines.append("")
            lines.append("| Domain | Pass Rate | N |")
            lines.append("|--------|-----------|---|")
            for d, ds in cd.get("by_domain", {}).items():
                lines.append(f"| {d} | {ds.get('pass_rate')} | {ds.get('n')} |")
            lines.append("")

        elif axis == "axis2":
            ov = data.get("overall", {})
            lines.append(f"- Pass rate: {ov.get('pass_rate')} ({ov.get('pass_count')} pass / {ov.get('fail_count')} fail, n={ov.get('n')})")
            lines.append(f"- Krippendorff alpha: {data.get('alpha')}")
            lines.append("")
            lines.append("| Model | Pass Rate | Pass | Fail | N |")
            lines.append("|-------|-----------|------|------|---|")
            for m, ms in data.get("by_model", {}).items():
                lines.append(f"| {m} | {ms.get('pass_rate')} | {ms.get('pass_count')} | {ms.get('fail_count')} | {ms.get('n')} |")
            lines.append("")

        elif axis == "axis3":
            acc = data.get("accuracy", {})
            lines.append(f"- Domain accuracy: {acc.get('domain_accuracy')} (n={acc.get('total')})")
            lines.append(f"- Category accuracy: {acc.get('category_accuracy')}")
            lines.append(f"- Krippendorff alpha: {data.get('alpha')}")
            lines.append("")
            lines.append("| Model | Domain Acc | Category Acc | N |")
            lines.append("|-------|-----------|-------------|---|")
            for m, ms in data.get("by_model", {}).items():
                lines.append(f"| {m} | {ms.get('domain_accuracy')} | {ms.get('category_accuracy')} | {ms.get('total')} |")
            lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Aggregate LLM-as-a-Judge results")
    parser.add_argument("--results-dir", default="./results")
    parser.add_argument("--benchmark-dir", default="../benchmark")
    parser.add_argument("--output-dir", default="./reports")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    aggregate(
        Path(args.results_dir).resolve(),
        Path(args.benchmark_dir).resolve(),
        Path(args.output_dir).resolve(),
    )


if __name__ == "__main__":
    main()