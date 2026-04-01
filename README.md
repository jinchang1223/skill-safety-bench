# SkillSafetyBench

`SkillSafetyBench` is a static benchmark for attacking and evaluating skill-using agents.

The current repository is not a live `attack.py` materialization framework. The source of truth is the prebuilt benchmark under [`benchmark/`](benchmark/), where each case is a fully materialized attacked task with its own task files, oracle solution, task-level tests, and attack-level verifier.

## Current Status

- `benchmark/`
  Static attacked-task benchmark cases, organized by:
  `risk_domain -> category -> case`
- `docs/`
  Taxonomy, redesign notes, and diagnosis documents
- root-level Python modules
  Legacy materialization/runtime code from an older repository phase. These files are not the primary path for evaluating the current benchmark subset.

The current top-level risk domains are:

- `context_trust_and_prompt_manipulation_risks`
- `agency_scope_and_authorization_risks`
- `execution_runtime_framework_and_protocol_risks`
- `data_boundary_output_and_externalization_risks`
- `memory_recovery_audit_and_persistence_risks`
- `knowledge_model_supply_chain_and_operational_risks`

## Benchmark Layout

Each case lives at:

```text
benchmark/<risk-domain>/<category>/<case>/
  metadata.json
  rationale.md
  attacked_task/
    instruction.md
    task.toml
    environment/
    solution/solve.sh
    tests/test.sh
    tests/test_outputs.py
  eval/verify_attack.py
```

Important conventions:

- `attacked_task/` is the task that should be run.
- `tests/test_outputs.py` checks whether the attacked task still completes the base task correctly.
- `eval/verify_attack.py` checks whether the attack-specific signal was actually induced.
- `metadata.json` is the canonical machine-readable description of the case.
- `rationale.md` is the human-readable explanation of why the case exists and how it is supposed to work.

## Evaluation

The benchmark is designed to be evaluated as SkillsBench-style tasks.

### Recommended Path: Harbor

Prerequisites:

- `docker`
- `uv`
- `harbor`

Install Harbor:

```bash
uv tool install harbor
```

Validate a task definition:

```bash
harbor check benchmark/<risk-domain>/<category>/<case>/attacked_task
```

Notes:

- On current Harbor versions, the command is `harbor check`, not `harbor tasks check`.
- `harbor check` may require model API keys such as `ANTHROPIC_API_KEY`.

Run the oracle on one attacked task:

```bash
harbor run -p benchmark/<risk-domain>/<category>/<case>/attacked_task -a oracle -n 1 -y
```

This executes the task as a normal SkillsBench task:

1. Build the task environment from `attacked_task/environment/Dockerfile`
2. Run `attacked_task/solution/solve.sh`
3. Run `attacked_task/tests/test.sh`

After that, you should also inspect the case-level attack result with:

```bash
python3 benchmark/<risk-domain>/<category>/<case>/eval/verify_attack.py
```

### Direct Docker Fallback

For debugging or when Harbor logs are not transparent enough, you can reproduce the same workflow manually:

```bash
docker build -t ssb-case benchmark/<risk-domain>/<category>/<case>/attacked_task/environment

docker run --rm \
  -v "$PWD/benchmark/<risk-domain>/<category>/<case>/attacked_task/solution:/solution" \
  -v "$PWD/benchmark/<risk-domain>/<category>/<case>/attacked_task/tests:/tests" \
  -v "$PWD/benchmark/<risk-domain>/<category>/<case>/eval:/eval" \
  ssb-case \
  bash -lc 'bash /solution/solve.sh && bash /tests/test.sh && python3 /eval/verify_attack.py'
```

Some task test runners install dependencies dynamically. In minimal containers, you may need the same fallback used during local verification:

```bash
python3 -m pip install --break-system-packages -q pytest==8.4.1
pytest /tests/test_outputs.py -q
python3 /eval/verify_attack.py
```

## What The Results Mean

For each case, treat the results as two separate signals:

- Base task result
  Whether `attacked_task/tests/test_outputs.py` passes
- Attack result
  Whether `eval/verify_attack.py` returns `attack_success` or `attack_not_observed`

Typical outcomes:

- Base task passes + `attack_success`
  Strong attack case
- Base task passes + `attack_not_observed`
  Attack did not induce the target behavior under the tested agent/oracle
- Base task fails
  Task or environment is not currently runnable; fix task correctness before interpreting attack behavior

## Current Notes

- RD4, RD5, and RD6 have been rewritten into non-user-surface attacks: `instruction.md` was restored to the original task where applicable, and attacks now rely on benchmark-local skills, sidecars, manifests, notes, and output artifacts.
- Several representative RD4-RD6 cases have been exercised through the SkillsBench-style task flow. In the sampled runs so far, base task tests passed while attack verifiers returned `attack_not_observed`.
- Travel-planning attacked tasks required a runtime fix: their `solve.sh` now tolerates both underscore and hyphen skill directory naming, and the expected skill scripts are restored into the attacked task environment.

See the redesign notes:

- [RD4 redesign](docs/rd4-non-user-attack-redesign-20260331.md)
- [RD5 redesign](docs/rd5-non-user-attack-redesign-20260331.md)
- [RD6 redesign](docs/rd6-non-user-attack-redesign-20260401.md)

## Legacy Code

The root-level Python modules such as [`cli.py`](cli.py), [`runner.py`](runner.py), [`catalog.py`](catalog.py), and [`case_library.py`](case_library.py) are retained from an older dynamic materialization phase.

They do not currently describe the repository’s main benchmark artifact layout correctly, and should not be treated as the primary evaluation path for the benchmark cases under `benchmark/`.
