# Skill Safety Bench

`Skill Safety Bench` is a fully materialized benchmark repository. It is not a framework for dynamically generating attack cases. Instead, it contains a static set of prepared benchmark cases that can be run directly with Harbor.

The recommended entry points are:

- the static benchmark cases under `benchmark/`
- the Harbor batch runner scripts centered on `scripts/start_codex_batch.sh`

## Repository Layout

The most important top-level directories and files are:

- `benchmark/`
  The benchmark itself. All risk domains, categories, and cases live here.
- `scripts/`
  Runner scripts.
  The main entry points are:
  - `start_codex_batch.sh`
  - `run_manifest_codex_batch.py`
  - `verify_replay.py`
- `.envrc`
  Environment variable configuration used when running Harbor / Codex.

## Benchmark Layout

Each case has the following structure:

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

Meaning of the key files:

- `attacked_task/`
  The actual task passed to Harbor.
- `attacked_task/tests/test_outputs.py`
  Checks whether the base task was completed correctly.
- `eval/verify_attack.py`
  Checks whether the attack behavior was induced.
- `metadata.json`
  Machine-readable case metadata.
- `rationale.md`
  Human-readable design notes.

Category directories are now uniformly named as:

- `category1-...`
- `category2-...`
- `category3-...`
- `category4-...`
- `category5-...`

For example:

```text
benchmark/risk-domain-6-knowledge-model-supply-chain-and-operational-risks/category1-availability_cost_and_service_exhaustion/
```

## Setup From Scratch

### 1. System Requirements

At minimum, you need:

- `bash`
- `python3`, recommended `>= 3.11`
- `docker`
- `uv`
- `harbor`

If Harbor is not installed yet, you can install it with:

```bash
uv tool install harbor
```

After installation, it is a good idea to verify:

```bash
harbor --help
python3 --version
docker --version
```

### 2. Harbor Runtime Prerequisites

The cases in this repository are designed to run in a SkillsBench / Harbor-style workflow, so Harbor requires at least:

- a working local Docker installation
- a user account that can access Docker
- Harbor installed and available on `PATH`

The batch script itself checks for:

- `python3`
- `harbor`
- the existence of `.envrc`

The script does not install Docker or Harbor for you. Those must be prepared at the system level first.

### 3. Configure API Environment Variables

By default, the runner scripts read the root-level [`.envrc`](./.envrc).

At minimum, it should define:

```bash
export OPENAI_BASE_URL=...
export OPENAI_API_KEY=...
```

If you need a special network mode, you can also add:

```bash
export NETWORK_MODE=host
```

or pass it at runtime via `--network-mode`.

A minimal `.envrc` example:

```bash
export OPENAI_BASE_URL="https://your-openai-compatible-endpoint/v1"
export OPENAI_API_KEY="sk-..."
```

If you use `direnv`, run this once in the repository root:

```bash
direnv allow
```

If you do not use `direnv`, that is fine. The scripts explicitly `source .envrc` at runtime.

### 4. API Connectivity Check

Before starting the actual run, the batch script automatically sends a minimal preflight request to:

- `POST $OPENAI_BASE_URL/responses`

The request includes:

- `OPENAI_API_KEY`
- the target model name

This is intended to catch problems early, such as:

- an incorrect `OPENAI_BASE_URL`
- an invalid `OPENAI_API_KEY`
- a gateway that is not compatible with OpenAI-style `/responses`
- a currently unavailable service

So if `.envrc` is already configured, you usually do not need to manually export environment variables each time. Running the script is enough.

## Running the Benchmark

### Recommended: Batch Runner Script

#### Run an entire risk domain

```bash
scripts/start_codex_batch.sh --rd 5
```

#### Run a single case

```bash
scripts/start_codex_batch.sh \
  --rd 5 \
  --case travel_planning_poisoned_belief_persistence_memory_anchor
```

#### Run a single category

```bash
scripts/start_codex_batch.sh \
  --rd 6 \
  --category category3-model_behavior_and_finetuning_poisoning
```

#### Run from a specific manifest

```bash
scripts/start_codex_batch.sh \
  --manifest benchmark/risk-domain-6-knowledge-model-supply-chain-and-operational-risks/manifest.json
```

#### Use a different env file

```bash
scripts/start_codex_batch.sh \
  --rd 5 \
  --envrc /path/to/your.envrc
```

#### Expand arguments only without executing

```bash
scripts/start_codex_batch.sh --rd 5 --dry-run
```


## Run Outputs

Each run creates a new output directory under `jobs/`, for example:

```text
jobs/codex-risk-domain-5-memory-recovery-audit-and-persistence-risks-<timestamp>/
```

The most important files are:

- `selected_cases.json`
  The cases actually selected for this run
- `batch_config.json`
  The run configuration
- `<case_id>/case_result.json`
  Per-case run result and verifier result
- `attack_results.json`
  Top-level summary focused on attack outcomes
- `summary.json`
  Overall summary
- `attack_results.csv`
- `attack_results.md`
- `summary.csv`
- `summary.md`

If you only want the most important outputs, start with:

- `jobs/<run>/attack_results.json`
- `jobs/<run>/summary.json`

## How to Interpret Results

Each case should be interpreted on two separate axes:

- whether the base task completed successfully
- whether the attack behavior was observed

The most common terminal attack outcomes are:

- `attack_success`
- `attack_not_observed`

Some verifiers may also print:

- `task_output_missing`

This means the task’s required explicit output file was missing, but the verifier still continued to evaluate the attack condition.

