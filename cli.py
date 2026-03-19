from __future__ import annotations

import argparse
import json
from pathlib import Path

from catalog import load_case_specs
from runner import load_materialization_config, materialize_attacked_task


def main() -> None:
    parser = argparse.ArgumentParser(prog="ssb")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list-cases", help="List available attack cases")
    list_parser.add_argument("--phase", help="Optional phase filter")

    materialize_parser = subparsers.add_parser("materialize", help="Copy a task and apply selected attack cases")
    materialize_parser.add_argument("--config", required=True, type=Path, help="Path to a materialization config YAML")

    args = parser.parse_args()

    if args.command == "list-cases":
        _list_cases(args.phase)
        return
    if args.command == "materialize":
        config = load_materialization_config(args.config)
        result = materialize_attacked_task(config)
        print(json.dumps(
            {
                "output_task": str(result.output_task),
                "applied_cases": result.applied_cases,
                "created_files": [str(path) for path in result.created_files],
                "modified_files": [str(path) for path in result.modified_files],
            },
            indent=2,
        ))


def _list_cases(phase: str | None) -> None:
    specs = load_case_specs()
    rows = []
    for spec in specs.values():
        if phase and spec.phase != phase:
            continue
        rows.append(
            {
                "id": spec.id,
                "phase": spec.phase,
                "category": spec.category,
                "class": spec.class_id,
                "name": spec.name,
            }
        )
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
