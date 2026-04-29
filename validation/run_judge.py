#!/usr/bin/env python3
"""LLM-as-a-Judge validation harness for Skill Safety Bench."""
from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from pathlib import Path

from lib.case_discovery import discover_cases
from lib.judge_client import JudgeClient, load_config
from lib.prompt_builder import build_prompt, prompt_hash
from lib.result_store import build_judgment, is_completed, save_result

logger = logging.getLogger(__name__)

AXIS_CONDITIONS = {
    "axis1": ["blind", "informed"],
    "axis2": ["default"],
    "axis3": ["default"],
}


async def judge_one(
    client: JudgeClient,
    case,
    axis: str,
    condition: str,
    benchmark_dir: Path,
    output_dir: Path,
) -> None:
    if is_completed(output_dir, axis, condition, client.judge.name, case.case_id):
        return

    prompt = build_prompt(case, axis, condition, benchmark_dir)
    phash = prompt_hash(prompt)

    try:
        raw = await client.call(prompt)
    except Exception as e:
        logger.error("Failed %s/%s/%s/%s: %s", axis, condition, client.judge.name, case.case_id, e)
        return

    result = build_judgment(case.case_id, axis, condition, client.judge.name, raw, phash)
    path = save_result(output_dir, result)
    logger.info("Saved %s", path)


async def run_axis(
    clients: list[JudgeClient],
    cases: list,
    axis: str,
    benchmark_dir: Path,
    output_dir: Path,
) -> None:
    conditions = AXIS_CONDITIONS[axis]
    tasks = []
    for client in clients:
        for case in cases:
            for condition in conditions:
                tasks.append(judge_one(client, case, axis, condition, benchmark_dir, output_dir))

    total = len(tasks)
    logger.info("Dispatching %d judgments for %s", total, axis)
    await asyncio.gather(*tasks)
    logger.info("Completed %s", axis)


async def main_async(args: argparse.Namespace) -> None:
    benchmark_dir = Path(args.benchmark_dir).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    judges, rate_limits = load_config(args.config)
    if not judges:
        logger.error("No judges configured in %s", args.config)
        sys.exit(1)

    concurrency = args.concurrency or rate_limits.get("default_concurrency", 10)
    rpm = rate_limits.get("default_rpm", 60)

    clients = [JudgeClient(j, concurrency=concurrency, rpm=rpm) for j in judges]

    cases = discover_cases(benchmark_dir)
    logger.info("Discovered %d cases", len(cases))

    if args.case_filter:
        cases = [c for c in cases if args.case_filter in c.case_id]
        logger.info("Filtered to %d cases matching '%s'", len(cases), args.case_filter)

    axes = ["axis1", "axis2", "axis3"] if args.axis == "all" else [args.axis]

    try:
        for axis in axes:
            await run_axis(clients, cases, axis, benchmark_dir, output_dir)
    finally:
        for c in clients:
            await c.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="LLM-as-a-Judge validation for Skill Safety Bench")
    parser.add_argument("--axis", choices=["axis1", "axis2", "axis3", "all"], default="all")
    parser.add_argument("--config", default="config/models.yaml")
    parser.add_argument("--benchmark-dir", default="../benchmark")
    parser.add_argument("--output-dir", default="./results")
    parser.add_argument("--concurrency", type=int, default=None)
    parser.add_argument("--case-filter", default=None, help="Only run cases whose ID contains this string")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
