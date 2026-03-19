from __future__ import annotations

import json
import shutil
from pathlib import Path

import yaml

from case_library import build_registry
from context import AttackContext
from models import AttackSelection, MaterializationConfig, MaterializationResult


def materialize_attacked_task(config: MaterializationConfig) -> MaterializationResult:
    source = config.source_task.resolve()
    output = config.output_task.resolve()
    if output.exists():
        raise FileExistsError(f"output task already exists: {output}")
    shutil.copytree(source, output)
    result = MaterializationResult(output_task=output)
    registry = build_registry()

    for selection in config.attacks:
        if selection.case_id not in registry:
            raise KeyError(f"unknown case id: {selection.case_id}")
        registered = registry[selection.case_id]
        ctx = AttackContext(task_root=output, case_spec=registered.spec, result=result, options=selection.options)
        registered.apply(ctx)
        result.applied_cases.append(selection.case_id)

    _write_manifest(output, config, result)
    return result


def load_materialization_config(path: Path) -> MaterializationConfig:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    attacks = tuple(
        AttackSelection(case_id=item["case_id"], options=item.get("options", {}))
        for item in data.get("attacks", [])
    )
    return MaterializationConfig(
        source_task=Path(data["source_task"]),
        output_task=Path(data["output_task"]),
        attacks=attacks,
    )


def _write_manifest(output: Path, config: MaterializationConfig, result: MaterializationResult) -> None:
    manifest_dir = output / ".skill-safety-bench"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "source_task": str(config.source_task),
        "output_task": str(config.output_task),
        "applied_cases": result.applied_cases,
        "created_files": [str(path.relative_to(output)) for path in result.created_files],
        "modified_files": [str(path.relative_to(output)) for path in result.modified_files],
    }
    (manifest_dir / "materialization.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
