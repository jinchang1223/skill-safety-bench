#!/usr/bin/env python3
"""LLM-as-a-Judge validation harness for Skill Safety Bench."""
from __future__ import annotations

import argparse
import asyncio
import logging
import multiprocessing as mp
import sys
from pathlib import Path

from lib.case_discovery import discover_cases
from lib.judge_client import JudgeClient, JudgeModel, load_config
from lib.prompt_builder import build_prompt, prompt_hash
from lib.result_store import build_judgment, is_completed, save_result

logger = logging.getLogger(__name__)

AXIS_CONDITIONS = {
    "axis1": ["informed"],
    "axis2": ["default"],
    "axis3": ["default"],
}

_SENTINEL = None


def _worker(
    task_queue: mp.Queue,
    judge_cfg: dict,
    benchmark_dir_str: str,
    output_dir_str: str,
    log_level: int,
) -> None:
    """Worker process: pull (case, axis, condition) tasks from queue until sentinel."""
    logging.basicConfig(
        level=log_level,
        format=f"%(asctime)s %(levelname)s [pid={mp.current_process().pid}] %(name)s: %(message)s",
    )
    log = logging.getLogger(__name__)

    judge = JudgeModel(**judge_cfg)
    benchmark_dir = Path(benchmark_dir_str)
    output_dir = Path(output_dir_str)

    async def run_one(case, axis, condition):
        if is_completed(output_dir, axis, condition, judge.name, case.case_id):
            return
        prompt = build_prompt(case, axis, condition, benchmark_dir)
        phash = prompt_hash(prompt)
        client = JudgeClient(judge, concurrency=1, rpm=600)
        try:
            raw = await client.call(prompt)
        except Exception as e:
            log.error("Failed %s/%s/%s/%s: %s", axis, condition, judge.name, case.case_id, e)
            return
        finally:
            await client.close()
        result = build_judgment(case.case_id, axis, condition, judge.name, raw, phash)
        path = save_result(output_dir, result)
        log.info("Saved %s", path)

    while True:
        item = task_queue.get()
        if item is _SENTINEL:
            break
        case, axis, condition = item
        asyncio.run(run_one(case, axis, condition))


def run_axis(
    judges: list[JudgeModel],
    cases: list,
    axis: str,
    benchmark_dir: Path,
    output_dir: Path,
    num_workers: int,
    log_level: int,
) -> None:
    conditions = AXIS_CONDITIONS[axis]
    tasks = [
        (case, axis, condition)
        for case in cases
        for condition in conditions
    ]
    total = len(tasks) * len(judges)
    logger.info("Dispatching %d judgments for %s across %d workers", total, axis, num_workers)

    all_workers = []
    for judge in judges:
        judge_cfg = {
            "name": judge.name,
            "base_url": judge.base_url,
            "model": judge.model,
            "api_key": judge.api_key,
            "max_tokens": judge.max_tokens,
            "temperature": judge.temperature,
            "no_proxy": judge.no_proxy,
        }

        queue: mp.Queue = mp.Queue()
        workers = [
            mp.Process(
                target=_worker,
                args=(queue, judge_cfg, str(benchmark_dir), str(output_dir), log_level),
                daemon=True,
            )
            for _ in range(num_workers)
        ]
        for w in workers:
            w.start()

        for task in tasks:
            queue.put(task)
        for _ in workers:
            queue.put(_SENTINEL)

        all_workers.extend(workers)

    for w in all_workers:
        w.join()

    logger.info("Completed %s", axis)


def main() -> None:
    parser = argparse.ArgumentParser(description="LLM-as-a-Judge validation for Skill Safety Bench")
    parser.add_argument("--axis", choices=["axis1", "axis2", "axis3", "all"], default="all")
    parser.add_argument("--config", default="config/models.yaml")
    parser.add_argument("--benchmark-dir", default="../benchmark")
    parser.add_argument("--output-dir", default="./results")
    parser.add_argument("--workers", type=int, default=10, help="Number of parallel worker processes")
    parser.add_argument("--case-filter", default=None, help="Only run cases whose ID contains this string")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    benchmark_dir = Path(args.benchmark_dir).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    judges, _ = load_config(args.config)
    if not judges:
        logger.error("No judges configured in %s", args.config)
        sys.exit(1)

    cases = discover_cases(benchmark_dir)
    logger.info("Discovered %d cases", len(cases))

    if args.case_filter:
        cases = [c for c in cases if args.case_filter in c.case_id]
        logger.info("Filtered to %d cases matching '%s'", len(cases), args.case_filter)

    axes = ["axis1", "axis2", "axis3"] if args.axis == "all" else [args.axis]

    for axis in axes:
        run_axis(judges, cases, axis, benchmark_dir, output_dir, args.workers, log_level)


if __name__ == "__main__":
    mp.set_start_method("fork", force=True)
    main()
