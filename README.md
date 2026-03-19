# SkillSafetyBench

`SkillSafetyBench` is an independent benchmark for attacking and evaluating skill-using agents.

This repository currently contains:

- `atom-attacks/`
  The phase/category/class/case attack library.
  Each class directory stores both the declarative YAML specs and the executable `attack.py`.
- root-level Python modules
  The runtime loader, task scanner, materializer, and CLI now live directly in the repository root.
- `configs/`
  Example runtime configuration files.

## Current Implementation Model

The current code does **not** hardcode a specific task.

Instead, it works in two stages:

1. `Code definition stage`
   The repository stores generic attack code for each case.
   Each case implementation discovers the relevant surfaces inside the supplied task at runtime.

2. `Run stage`
   A runner copies a user-specified source task to an output workspace and then applies one or more attack cases.

This keeps the attack code task-agnostic while still allowing concrete attacks to be materialized on real tasks.

## Main Components

- `catalog.py`
  Loads the YAML case library from `atom-attacks/`.
- `layout.py`
  Discovers `instruction.md`, `task.toml`, `environment/`, `skills/`, references, scripts, and `Dockerfile`.
- `case_library.py`
  Builds the runtime registry by auto-discovering `attack.py` inside `atom-attacks/`.
- `atom-attacks/**/attack.py`
  Stores the concrete per-class attack code beside `class.yaml` and `cases/*.yaml`.
- `runner.py`
  Copies a source task to an output location and applies the selected cases.
- `cli.py`
  Exposes a small CLI.

## CLI

List cases:

```bash
python3 cli.py list-cases
```

Materialize an attacked task:

```bash
python3 cli.py materialize --config configs/example-materialize.yaml
```

## Example Config

See:

- `configs/example-materialize.yaml`

The config provides:

- `source_task`
- `output_task`
- `attacks[]`
  - `case_id`
  - optional `options`

Common options include:

- `surface`
- `skill_name`
- `reference_name`
- `script_name`
- `command_name`
- `decoy_skill_name`

`surface` is only valid for cases whose YAML declares `surface_mode: choice`.

The current runtime distinguishes three attack-surface modes:

- `fixed`
  The case has one implementation-defined injection surface. Overriding it is rejected.
- `choice`
  The case supports several equivalent injection surfaces, and `options.surface` may select one.
- `composite`
  The case intentionally coordinates multiple surfaces at once, so a single surface override is rejected.

## Current Attack Surfaces Supported in Code

- task instruction poisoning
- skill doc poisoning
- skill reference poisoning
- task artifact seeding
- runtime wrapper installation with Dockerfile patching
- persistence artifact seeding

## Notes

- This is the first working implementation pass.
- The current code is focused on attack materialization, not evaluation.
- Future work should add:
  - stronger per-case payload design
  - better task adapter abstractions
  - chain composition logic
  - evaluation and attribution
