# LLM-as-a-Judge Validation Harness

Validates the soundness of the Skill Safety Bench benchmark using LLM judges across three evaluation axes.

## Evaluation Axes

**Axis 1 — Attack Plausibility**: Are the adversarial modifications realistic and well-camouflaged? Runs two conditions:
- *Blind*: Judge sees all environment files without knowing which are injected. Rates trustworthiness 1-5.
- *Informed*: Judge is told which files were modified. Rates camouflage quality 1-5.

**Axis 2 — Verifier-Attack Alignment**: Does each `verify_attack.py` correctly detect the attack described in `metadata.json`? Checks for false-positive and false-negative risks. Rates alignment 1-5.

**Axis 3 — Taxonomy Coherence**: Given the case rationale and the full RD1-RD6 taxonomy, can a judge independently classify the case into the correct risk domain and category? Measures exact-match accuracy.

## Setup

```bash
pip install -r requirements.txt
```

Edit `config/models.yaml` with your judge model endpoints. The harness uses the OpenAI-compatible chat completions API, so any provider with that interface works:

```yaml
judges:
  - name: "judge-1"
    base_url: "https://api.example.com/v1"
    model: "model-name"
    api_key_env: "JUDGE_1_API_KEY"    # reads from this env var
    max_tokens: 4096
    temperature: 0.0

rate_limits:
  default_rpm: 60
  default_concurrency: 10
```

## Usage

Run all axes on all 158 cases:

```bash
python run_judge.py --axis all --config config/models.yaml -v
```

Run a single axis:

```bash
python run_judge.py --axis axis2 --config config/models.yaml
```

Filter to specific cases:

```bash
python run_judge.py --axis axis1 --case-filter xlsx_recovery
```

The harness supports resume — re-running skips already-completed judgments.

## Aggregation

After judgments are collected:

```bash
python aggregate.py --results-dir ./results --output-dir ./reports
```

Produces `reports/report.json` and `reports/report.md` with:

- Per-axis mean scores, std, 95% bootstrap CI
- Krippendorff's alpha for inter-judge agreement (ordinal for axes 1-2, nominal for axis 3)
- Per-risk-domain breakdowns
- Axis 3 domain and category exact-match accuracy

## Project Structure

```
validation/
  run_judge.py              # CLI entry point
  aggregate.py              # Post-hoc analysis
  config/
    models.yaml             # Judge model config (fill in before running)
  prompts/
    axis1_blind.txt         # Attack plausibility — blind condition
    axis1_informed.txt      # Attack plausibility — informed condition
    axis2_alignment.txt     # Verifier-attack alignment
    axis3_taxonomy.txt      # Taxonomy coherence
  lib/
    schemas.py              # CaseRecord, JudgmentResult dataclasses
    case_discovery.py       # Walks benchmark/, loads metadata
    prompt_builder.py       # Fills prompt templates with per-case context
    judge_client.py         # Async OpenAI-compatible API client
    result_store.py         # One JSON per judgment, resume logic
  requirements.txt
```
