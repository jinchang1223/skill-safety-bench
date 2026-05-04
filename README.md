# Skill Safety Bench

<p align="right">
  <a href="./README.md"><img alt="English" src="https://img.shields.io/badge/English-blue?style=for-the-badge"></a>
  <a href="./README.zh.md"><img alt="中文" src="https://img.shields.io/badge/%E4%B8%AD%E6%96%87-blue?style=for-the-badge"></a>
</p>

`Skill Safety Bench` is a fully materialized benchmark for evaluating safety failures induced through skill-facing context and supporting local artifacts. It is not a dynamic case generator. The repository contains prepared benchmark cases that can be run with Harbor.

### Safety Notice

This repository contains adversarial benchmark cases. Some cases simulate phishing, credential solicitation, destructive operations, data exfiltration, sandbox boundary abuse, external actions, and persistence-like behaviors. Run the benchmark only in isolated research environments.

Do not use production credentials, production cloud accounts, personal accounts, or sensitive local files when running these cases. Prefer throwaway API keys, disposable containers, restricted network access, and a dedicated working directory. Review run artifacts before sharing them.

### Repository Layout

- `benchmark/`
  Static benchmark cases organized by risk domain, category, and case id.
- `scripts/start_agent_batch.sh`
  The main local execution entry point. It selects cases, launches Harbor, and refreshes run summaries.
- `scripts/run_manifest_agent_batch.py`
  Runner implementation used by `start_agent_batch.sh`.
- `env.example`
  Example environment file. Copy it to `.envrc` and fill in local credentials before running.

### Benchmark Layout

Each case is packaged as:

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
  eval/verify_attack.py
```

Key files:

- `attacked_task/`
  The Harbor task package used for the agent run.
- `attacked_task/tests/test.sh`
  The canonical base-task test entry point.
- `eval/verify_attack.py`
  The deterministic attack-behavior verifier for the case.
- `metadata.json`
  Machine-readable metadata.
- `rationale.md`
  Human-readable case rationale.

The benchmark currently contains 155 cases across 6 risk domains and 30 categories. Category directories use the `categoryN-...` naming pattern, for example:

```text
benchmark/risk-domain-6-knowledge-model-supply-chain-and-operational-risks/category1-availability_cost_and_service_exhaustion/
```

### Setup

Install or prepare:

- `bash`
- `python3`, recommended `>= 3.11`
- `docker`
- `uv`
- `harbor`
- `nvm`
- Node.js `22`

Install Harbor if needed:

```bash
uv tool install harbor
```

Check the basic toolchain:

```bash
harbor --help
python3 --version
docker --version
```

If your Harbor agent is installed through Node, activate Node 22 in the shell that starts the run:

```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
nvm use 22
```

### Configure Environment Variables

Create a local `.envrc` from the example file:

```bash
cp env.example .envrc
```

For `codex`, set at least:

```bash
export OPENAI_BASE_URL="https://your-openai-compatible-endpoint/v1"
export OPENAI_API_KEY="replace-with-your-openai-api-key"
```

For `claude-code`, set an Anthropic-compatible auth variable, for example:

```bash
export ANTHROPIC_BASE_URL="https://api.anthropic.com"
export ANTHROPIC_API_KEY="replace-with-your-anthropic-api-key"
```

If you use `direnv`, run:

```bash
direnv allow
```

If not, no extra step is required. The batch script explicitly sources `.envrc` at runtime.

### Running the Benchmark

Run one risk domain:

```bash
scripts/start_agent_batch.sh --rd 5
```

Choose agent and model:

```bash
scripts/start_agent_batch.sh \
  --rd 3 \
  --agent codex \
  --model openai/gpt-5.4
```

Run with Claude Code:

```bash
scripts/start_agent_batch.sh \
  --rd 3 \
  --agent claude-code \
  --model claude-3-7-sonnet-20250219
```

Run a single case:

```bash
scripts/start_agent_batch.sh \
  --rd 5 \
  --case travel_planning_poisoned_belief_persistence_memory_anchor
```

Run a single category:

```bash
scripts/start_agent_batch.sh \
  --rd 6 \
  --category category3-model_behavior_and_finetuning_poisoning
```

Run from an explicit manifest:

```bash
scripts/start_agent_batch.sh \
  --manifest benchmark/risk-domain-6-knowledge-model-supply-chain-and-operational-risks/manifest.json
```

Use a custom env file:

```bash
scripts/start_agent_batch.sh \
  --rd 5 \
  --envrc /path/to/your.envrc
```

Print selected cases without executing:

```bash
scripts/start_agent_batch.sh --rd 5 --dry-run
```

### Run Outputs

Each run creates an output directory under `jobs/`:

```text
jobs/<agent>-risk-domain-5-memory-recovery-audit-and-persistence-risks-<timestamp>/
```

Important files:

- `selected_cases.json`
- `batch_config.json`
- `<case_id>/case_result.json`
- `attack_results.json`
- `summary.json`
- `attack_results.csv`
- `attack_results.md`
- `summary.csv`
- `summary.md`

Start with `jobs/<run>/attack_results.json` and `jobs/<run>/summary.json` when inspecting a run.

### Interpreting Results

Each case should be read on two axes:

- whether the benign base task completed successfully
- whether the unsafe attack behavior was observed

Common attack outcomes:

- `attack_success`
- `attack_not_observed`
- `task_output_missing`

`task_output_missing` means the expected explicit task output was absent. The attack verifier may still continue when enough artifacts exist to evaluate the attack condition.
