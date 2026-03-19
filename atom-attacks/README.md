# SkillSafetyBench Atom Attacks

This directory stores the concrete atomic attack library for `SkillSafetyBench`.

## Structure

The directory uses four nested layers:

1. `Phase`
   Definition:
   A `Phase` is a stage in the lifecycle of agent skill use.

2. `Category`
   Definition:
   A `Category` is a parallel risk theme inside a phase.
   A category collects attack classes that manipulate the same stage of skill use in a similar way.

3. `Class`
   Definition:
   A `Class` is an atomic attack family.
   A class is broader than a single payload but narrower than a whole phase.

4. `Case`
   Definition:
   A `Case` is one concrete atomic attack instance that can later be materialized by a runner.

The filesystem layout is:

```text
atom-attacks/
  phase-<n>-<phase-name>/
    phase.yaml
    category-<n>-<category-name>/
      category.yaml
      <attack-class>/
        class.yaml
        attack.py
        cases/
          <case-id>.yaml
```

## Naming Rules

- `phase.yaml`
  Defines the meaning of the phase and why it matters.
- `category.yaml`
  Defines the category name and the common risk theme shared by its classes.
- `class.yaml`
  Defines the attack class, its mechanism, and the type of unsafe behavior it tries to induce.
- `attack.py`
  Implements the executable attack logic for the class.
  One `attack.py` file can register several concrete cases from the sibling `cases/` directory.
- `cases/*.yaml`
  Defines one concrete atomic attack case.

## Case Status

This directory now stores both the canonical declarative attack specifications and the colocated executable implementations.

They are currently used for:

- case discovery
- taxonomy lookup
- CLI listing
- registry coverage checks

The executable attack code is colocated in each class directory as `attack.py`.

Each implementation is matched to a YAML case by `case_id`, and the runtime loader discovers these `attack.py` files directly from this tree.

The YAML files do not execute attacks by themselves.
They define the taxonomy and per-case metadata that the runtime uses while loading the neighboring `attack.py` modules.

They do not yet define:

- the full runtime option schema for every case
- evaluation metrics
- scoring logic
- runner instrumentation beyond materialization

Those will be added later after the case set is finalized.
