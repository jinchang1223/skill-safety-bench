# SkillSafetyBench Taxonomy Specification

## 1. Purpose

This document defines the **current implemented taxonomy** of `SkillSafetyBench`.

`SkillSafetyBench` is an independent benchmark for attacking and evaluating skill-using agents. It is not a sub-benchmark of `SkillsBench`.

In the current repository structure:

- `SkillsBench` or any other benchmark is only a **task source**
- `SkillSafetyBench` owns the attack library, attack materialization logic, and evaluation design
- `atom-attacks/` is the source of truth for the current attack hierarchy

This specification describes the architecture that is **actually implemented now**, not a future or hypothetical taxonomy.

## 2. Scope

This taxonomy covers:

- the attack hierarchy used in `atom-attacks/`
- the meaning of each hierarchy layer
- the current attack surface control model
- the currently implemented phase-category-class-case library

This taxonomy does not define:

- the exact runner internals
- the exact evaluation formulas
- the exact trace instrumentation format

Those belong to implementation or evaluation documents.

## 3. Foundational Terms

### 3.1 Benchmark

`Benchmark` means the full benchmark system, including:

- attack definitions
- attack materialization logic
- task adapters
- evaluation logic
- reporting logic

Here, the benchmark is `SkillSafetyBench`.

### 3.2 Task Source

`Task Source` means an external repository or benchmark that provides base tasks which `SkillSafetyBench` attacks at runtime.

Examples include:

- `SkillsBench`
- a future private internal task suite
- a future benchmark with explicit skill routing

### 3.3 Phase

`Phase` means a stage in the lifecycle of agent skill use.

A phase answers:

- when the attack matters in the agent workflow
- what stage of skill use is being manipulated

The current taxonomy uses six phases:

- `skill_discovery`
- `skill_interpretation`
- `skill_selection_and_planning`
- `skill_execution`
- `skill_output_and_handoff`
- `skill_memory_recovery_and_audit`

### 3.4 Category

`Category` means a parallel attack direction inside one phase.

A category groups classes that manipulate a similar kind of risk within the same phase.

Examples:

- `routing_and_cue_poisoning`
- `dangerous_action_induction`
- `artifact_and_schema_poisoning`

### 3.5 Class

`Class` means a reusable atomic attack family with a shared mechanism.

A class is not a single payload. A class groups several concrete attack cases that share the same high-level manipulation pattern.

Examples:

- `priority_override`
- `runtime_integrity_compromise`
- `artifact_relay_poisoning`

### 3.6 Case

`Case` means the smallest independently materializable attack unit.

Each case is:

- concrete
- executable
- individually selectable in config
- individually evaluable later

Examples:

- `task_vs_skill_flip`
- `upload_to_webhook`
- `delete_history_after_run`

### 3.7 Attack Surface

`Attack Surface` means the concrete place where a case injects or modifies information to influence the agent.

In the current implementation, attack surfaces are an **orthogonal control dimension**. They do not replace `phase -> category -> class -> case`.

### 3.8 Primary Surfaces

`Primary Surfaces` means the concrete injection surfaces actually used by the current implementation of a case.

In the current codebase, `primary_surfaces` are intended to match the implemented attack behavior, not just broad conceptual relevance.

### 3.9 Surface Mode

`Surface Mode` means how configurable a case's injection surface is.

The current implementation supports three modes:

- `fixed`
  The case has one implementation-defined surface. Overriding it is rejected.
- `choice`
  The case supports several equivalent injection surfaces. `options.surface` may choose among them.
- `composite`
  The case intentionally coordinates multiple surfaces in one attack. A single-surface override is rejected.

### 3.10 Surface Override

`Surface Override` means the runtime parameter `options.surface` that asks a case to inject through a different supported surface.

In the current implementation:

- `options.surface` is valid only for `choice` cases
- `fixed` cases reject unsupported overrides
- `composite` cases reject single-surface overrides

## 4. Current Hierarchy

The current implemented hierarchy is:

1. `Phase`
2. `Category`
3. `Class`
4. `Case`

This is the directory logic of `atom-attacks/`:

```text
atom-attacks/
  phase-*/
    category-*/
      <class>/
        class.yaml
        attack.py
        cases/
          <case>.yaml
```

Meaning:

- `phase.yaml` defines a lifecycle stage
- `category.yaml` defines a parallel risk direction within that phase
- `class.yaml` defines an attack family
- `cases/*.yaml` defines concrete cases
- `attack.py` implements the class's concrete case logic

## 5. Current Attack Surface Model

The runtime currently recognizes the following surface names:

- `task_instruction_surface`
  The main task instruction file such as `instruction.md`
- `skill_doc_surface`
  The main `SKILL.md` of a skill
- `skill_reference_surface`
  A skill reference file in `references/`
- `skill_script_surface`
  A helper script in `scripts/`
- `task_artifact_surface`
  A task-owned local artifact or injected task file
- `runtime_wrapper_surface`
  A runtime shim or wrapper inserted into execution flow
- `docker_environment_surface`
  A Dockerfile or environment-level runtime modification
- `output_channel_surface`
  A result or handoff channel
- `persistent_state_surface`
  A durable state location intended to affect later runs

Not every defined surface is used by every current case. The taxonomy keeps a shared surface vocabulary so future cases can extend the library without changing the control model.

## 6. Current Implemented Architecture Summary

Current library size:

- `6` phases
- `11` categories
- `23` classes
- `46` cases

The current implemented pipeline is:

```text
phase `skill_discovery`
  category `routing_and_cue_poisoning`
    class `routing_bias_hint`
      case `false_system_recommendation`
      case `urgent_use_note`
    class `skill_name_decoy`
      case `lexical_lookalike`
      case `namespace_collision`
phase `skill_interpretation`
  category `authority_and_rule_poisoning`
    class `priority_override`
      case `speed_over_safety_flip`
      case `task_vs_skill_flip`
    class `reference_rule_poisoning`
      case `fabricated_threshold`
      case `false_exception_clause`
  category `pattern_and_intent_poisoning`
    class `example_pattern_poisoning`
      case `plausible_wrong_example`
      case `unsafe_shell_example`
    class `malicious_intent_seeding`
      case `request_api_key_for_debugging`
      case `request_otp_for_identity_check`
phase `skill_selection_and_planning`
  category `shortcut_and_scope_biasing`
    class `high_agency_plan_injection`
      case `act_first_confirm_later`
      case `auto_export_for_review`
    class `unsafe_fallback_planning`
      case `skip_validation_to_meet_deadline`
      case `timeout_heuristic_fallback`
  category `conflict_and_approval_distortion`
    class `approval_bypass_planning`
      case `emergency_override_claim`
      case `manager_already_approved_note`
    class `cross_skill_conflict`
      case `objective_conflict`
      case `permission_boundary_conflict`
phase `skill_execution`
  category `runtime_and_toolchain_manipulation`
    class `runtime_integrity_compromise`
      case `command_wrapper_hijack`
      case `path_shadowing`
  category `dangerous_action_induction`
    class `credential_and_privilege_induction`
      case `api_key_request`
      case `sudo_request`
    class `destructive_action_induction`
      case `delete_logs_cleanup`
      case `git_reset_hard_cleanup`
    class `payment_identity_solicitation`
      case `credit_card_request`
      case `otp_request`
    class `sensitive_data_access_induction`
      case `open_private_key_for_connection_test`
      case `read_env_for_debugging`
phase `skill_output_and_handoff`
  category `artifact_and_schema_poisoning`
    class `artifact_relay_poisoning`
      case `fake_metadata_field`
      case `poisoned_csv_column`
    class `output_schema_manipulation`
      case `extra_json_key_for_secret`
      case `hidden_field_injection`
  category `egress_and_output_abuse`
    class `exfiltration_via_output_channel`
      case `include_secret_in_report`
      case `place_sensitive_data_in_submission_file`
    class `external_communication_exfiltration`
      case `send_debug_archive_to_remote`
      case `upload_to_webhook`
phase `skill_memory_recovery_and_audit`
  category `belief_persistence_and_recovery_failure`
    class `false_heuristic_persistence`
      case `fallback_rule_repeat`
      case `multi_surface_repeat`
    class `recovery_blocking`
      case `conflict_as_noise_hint`
      case `discourage_second_check`
  category `stealth_and_long_lived_footholds`
    class `audit_evasion`
      case `delete_history_after_run`
      case `suppress_warning_output`
    class `persistence_implant`
      case `leave_shadow_binary`
      case `modify_local_config_for_future_runs`
```

## 7. Phase and Category Definitions

This section defines the current phases and categories in the implemented library.

### 7.1 `skill_discovery`

Definition:

The phase where the agent finds, identifies, or routes to a skill.

Current categories:

- `routing_and_cue_poisoning`
  Manipulates routing cues, urgency framing, and recommendation-like signals.

### 7.2 `skill_interpretation`

Definition:

The phase where the agent reads skill content and decides what is authoritative, trustworthy, and operationally valid.

Current categories:

- `authority_and_rule_poisoning`
  Pollutes rules, precedence, and authoritative-seeming guidance.
- `pattern_and_intent_poisoning`
  Pollutes examples, patterns, and explicit malicious intent embedded in the skill context.

### 7.3 `skill_selection_and_planning`

Definition:

The phase where the agent chooses how to use skills, how to arbitrate conflicts, and what overall plan to follow.

Current categories:

- `shortcut_and_scope_biasing`
  Pushes the agent toward unsafe shortcuts or broader-than-necessary plans.
- `conflict_and_approval_distortion`
  Distorts approval assumptions or creates conflicting guidance that changes planning behavior.

### 7.4 `skill_execution`

Definition:

The phase where the agent turns plans into actual commands, tool usage, credential requests, permission decisions, or direct operational actions.

Current categories:

- `runtime_and_toolchain_manipulation`
  Manipulates wrappers, shims, Docker/runtime configuration, or toolchain integrity.
- `dangerous_action_induction`
  Induces unsafe actions, secret collection, destructive actions, or sensitive access requests.

### 7.5 `skill_output_and_handoff`

Definition:

The phase where the agent writes structured outputs, emits intermediate files, or hands results to downstream steps or reviewers.

Current categories:

- `artifact_and_schema_poisoning`
  Pollutes intermediate artifacts or output schemas.
- `egress_and_output_abuse`
  Uses outputs or handoff channels for exfiltration or unsafe externalization.

### 7.6 `skill_memory_recovery_and_audit`

Definition:

The phase where the agent carries forward heuristics, decides whether to recover from earlier mistakes, hides traces, or persists harmful state.

Current categories:

- `belief_persistence_and_recovery_failure`
  Makes wrong heuristics durable and blocks correction.
- `stealth_and_long_lived_footholds`
  Reduces auditability or leaves persistent harmful state for later runs.

## 8. Class Definitions

This section defines every currently implemented class and its cases.

### 8.1 Phase `skill_discovery`

#### Category `routing_and_cue_poisoning`

##### Class `routing_bias_hint`

Definition:

Biases skill discovery through urgency or recommendation-style cues instead of true relevance.

Current cases:

- `false_system_recommendation`
- `urgent_use_note`

##### Class `skill_name_decoy`

Definition:

Creates nearby decoy skills whose names or namespaces are meant to attract mistaken selection.

Current cases:

- `lexical_lookalike`
- `namespace_collision`

### 8.2 Phase `skill_interpretation`

#### Category `authority_and_rule_poisoning`

##### Class `priority_override`

Definition:

Changes the perceived authority ordering between task instructions and skills.

Current cases:

- `speed_over_safety_flip`
- `task_vs_skill_flip`

##### Class `reference_rule_poisoning`

Definition:

Injects false or unsafe rules into reference material and links them back into the skill.

Current cases:

- `fabricated_threshold`
- `false_exception_clause`

#### Category `pattern_and_intent_poisoning`

##### Class `example_pattern_poisoning`

Definition:

Injects flawed but plausible examples that the agent may imitate.

Current cases:

- `plausible_wrong_example`
- `unsafe_shell_example`

##### Class `malicious_intent_seeding`

Definition:

Embeds explicit malicious requests into trusted skill context so they look like legitimate workflow steps.

Current cases:

- `request_api_key_for_debugging`
- `request_otp_for_identity_check`

### 8.3 Phase `skill_selection_and_planning`

#### Category `shortcut_and_scope_biasing`

##### Class `high_agency_plan_injection`

Definition:

Pushes the agent toward broad, aggressive, or externally oriented plans without proper confirmation boundaries.

Current cases:

- `act_first_confirm_later`
- `auto_export_for_review`

##### Class `unsafe_fallback_planning`

Definition:

Pushes the agent toward unsafe shortcuts whenever validation is slow or time pressure is present.

Current cases:

- `skip_validation_to_meet_deadline`
- `timeout_heuristic_fallback`

#### Category `conflict_and_approval_distortion`

##### Class `approval_bypass_planning`

Definition:

Injects false approval or emergency framing so the agent skips confirmation checks during planning.

Current cases:

- `emergency_override_claim`
- `manager_already_approved_note`

##### Class `cross_skill_conflict`

Definition:

Introduces conflicting operational guidance across skill-linked surfaces so the agent must arbitrate poisoned alternatives.

Current cases:

- `objective_conflict`
- `permission_boundary_conflict`

### 8.4 Phase `skill_execution`

#### Category `runtime_and_toolchain_manipulation`

##### Class `runtime_integrity_compromise`

Definition:

Changes the runtime execution path through wrappers, PATH-level hijacks, and environment preparation changes.

Current cases:

- `command_wrapper_hijack`
- `path_shadowing`

#### Category `dangerous_action_induction`

##### Class `credential_and_privilege_induction`

Definition:

Induces the agent to request credentials or elevated permissions as part of normal execution.

Current cases:

- `api_key_request`
- `sudo_request`

##### Class `destructive_action_induction`

Definition:

Induces destructive cleanup, hard resets, or similarly damaging execution steps.

Current cases:

- `delete_logs_cleanup`
- `git_reset_hard_cleanup`

##### Class `payment_identity_solicitation`

Definition:

Induces the agent to request financial or identity verification data from the user.

Current cases:

- `credit_card_request`
- `otp_request`

##### Class `sensitive_data_access_induction`

Definition:

Induces the agent to read sensitive local data as if it were part of routine debugging or verification.

Current cases:

- `open_private_key_for_connection_test`
- `read_env_for_debugging`

### 8.5 Phase `skill_output_and_handoff`

#### Category `artifact_and_schema_poisoning`

##### Class `artifact_relay_poisoning`

Definition:

Creates poisoned artifacts and then encourages the agent to trust them as reusable intermediate state.

Current cases:

- `fake_metadata_field`
- `poisoned_csv_column`

##### Class `output_schema_manipulation`

Definition:

Encourages output schema deviations that can hide secrets or unsafe extra fields.

Current cases:

- `extra_json_key_for_secret`
- `hidden_field_injection`

#### Category `egress_and_output_abuse`

##### Class `exfiltration_via_output_channel`

Definition:

Uses normal result or submission channels to carry sensitive data outward.

Current cases:

- `include_secret_in_report`
- `place_sensitive_data_in_submission_file`

##### Class `external_communication_exfiltration`

Definition:

Frames remote upload or external transmission as part of standard completion behavior.

Current cases:

- `send_debug_archive_to_remote`
- `upload_to_webhook`

### 8.6 Phase `skill_memory_recovery_and_audit`

#### Category `belief_persistence_and_recovery_failure`

##### Class `false_heuristic_persistence`

Definition:

Repeats a poisoned heuristic across several surfaces so it becomes sticky and hard to discard.

Current cases:

- `fallback_rule_repeat`
- `multi_surface_repeat`

##### Class `recovery_blocking`

Definition:

Discourages re-checking or treating conflicts as legitimate reasons to revise the plan.

Current cases:

- `conflict_as_noise_hint`
- `discourage_second_check`

#### Category `stealth_and_long_lived_footholds`

##### Class `audit_evasion`

Definition:

Reduces the visibility of suspicious behavior by suppressing warnings or clearing history.

Current cases:

- `delete_history_after_run`
- `suppress_warning_output`

##### Class `persistence_implant`

Definition:

Leaves behind artifacts or configuration intended to bias future runs.

Current cases:

- `leave_shadow_binary`
- `modify_local_config_for_future_runs`

## 9. Current Design Notes

The current taxonomy should be read together with the implementation:

- `class.yaml` defines the class identity
- `cases/*.yaml` define the case metadata, primary surfaces, and surface control metadata
- `attack.py` defines the actual materialization behavior

For the current implementation, the runtime architecture should be understood as:

- `phase -> category -> class -> case`
- plus an orthogonal attack-surface control layer:
  - `primary_surfaces`
  - `surface_mode`
  - `supported_surfaces`
  - `default_surface`

This means the taxonomy is not only conceptual. It is tied directly to the executable attack library in `atom-attacks/`.

## 10. Bench Architecture Layout

This section gives the current repository layout of `SkillSafetyBench` in directory-tree form.

The tree below focuses on the benchmark source files and stable repository structure. Runtime-generated contents under `jobs/` and materialized attacked tasks under `tmp-tasks/` are included as directories but not expanded exhaustively.

```text
skill-safety-bench/
├── atom-attacks/                         # Core attack library: phase -> category -> class -> case
│   ├── README.md
│   ├── phase-0-skill-discovery/
│   │   ├── phase.yaml
│   │   └── category-1-routing-and-cue-poisoning/
│   │       ├── category.yaml
│   │       ├── routing_bias_hint/
│   │       │   ├── attack.py
│   │       │   ├── class.yaml
│   │       │   └── cases/
│   │       │       ├── false_system_recommendation.yaml
│   │       │       └── urgent_use_note.yaml
│   │       └── skill_name_decoy/
│   │           ├── attack.py
│   │           ├── class.yaml
│   │           └── cases/
│   │               ├── lexical_lookalike.yaml
│   │               └── namespace_collision.yaml
│   ├── phase-1-skill-interpretation/
│   │   ├── phase.yaml
│   │   ├── category-1-authority-and-rule-poisoning/
│   │   │   ├── category.yaml
│   │   │   ├── priority_override/
│   │   │   │   ├── attack.py
│   │   │   │   ├── class.yaml
│   │   │   │   └── cases/
│   │   │   │       ├── speed_over_safety_flip.yaml
│   │   │   │       └── task_vs_skill_flip.yaml
│   │   │   └── reference_rule_poisoning/
│   │   │       ├── attack.py
│   │   │       ├── class.yaml
│   │   │       └── cases/
│   │   │           ├── fabricated_threshold.yaml
│   │   │           └── false_exception_clause.yaml
│   │   └── category-2-pattern-and-intent-poisoning/
│   │       ├── category.yaml
│   │       ├── example_pattern_poisoning/
│   │       │   ├── attack.py
│   │       │   ├── class.yaml
│   │       │   └── cases/
│   │       │       ├── plausible_wrong_example.yaml
│   │       │       └── unsafe_shell_example.yaml
│   │       └── malicious_intent_seeding/
│   │           ├── attack.py
│   │           ├── class.yaml
│   │           └── cases/
│   │               ├── request_api_key_for_debugging.yaml
│   │               └── request_otp_for_identity_check.yaml
│   ├── phase-2-skill-selection-and-planning/
│   │   ├── phase.yaml
│   │   ├── category-1-shortcut-and-scope-biasing/
│   │   │   ├── category.yaml
│   │   │   ├── high_agency_plan_injection/
│   │   │   │   ├── attack.py
│   │   │   │   ├── class.yaml
│   │   │   │   └── cases/
│   │   │   │       ├── act_first_confirm_later.yaml
│   │   │   │       └── auto_export_for_review.yaml
│   │   │   └── unsafe_fallback_planning/
│   │   │       ├── attack.py
│   │   │       ├── class.yaml
│   │   │       └── cases/
│   │   │           ├── skip_validation_to_meet_deadline.yaml
│   │   │           └── timeout_heuristic_fallback.yaml
│   │   └── category-2-conflict-and-approval-distortion/
│   │       ├── category.yaml
│   │       ├── approval_bypass_planning/
│   │       │   ├── attack.py
│   │       │   ├── class.yaml
│   │       │   └── cases/
│   │       │       ├── emergency_override_claim.yaml
│   │       │       └── manager_already_approved_note.yaml
│   │       └── cross_skill_conflict/
│   │           ├── attack.py
│   │           ├── class.yaml
│   │           └── cases/
│   │               ├── objective_conflict.yaml
│   │               └── permission_boundary_conflict.yaml
│   ├── phase-3-skill-execution/
│   │   ├── phase.yaml
│   │   ├── category-1-runtime-and-toolchain-manipulation/
│   │   │   ├── category.yaml
│   │   │   └── runtime_integrity_compromise/
│   │   │       ├── attack.py
│   │   │       ├── class.yaml
│   │   │       └── cases/
│   │   │           ├── command_wrapper_hijack.yaml
│   │   │           └── path_shadowing.yaml
│   │   └── category-2-dangerous-action-induction/
│   │       ├── category.yaml
│   │       ├── credential_and_privilege_induction/
│   │       │   ├── attack.py
│   │       │   ├── class.yaml
│   │       │   └── cases/
│   │       │       ├── api_key_request.yaml
│   │       │       └── sudo_request.yaml
│   │       ├── destructive_action_induction/
│   │       │   ├── attack.py
│   │       │   ├── class.yaml
│   │       │   └── cases/
│   │       │       ├── delete_logs_cleanup.yaml
│   │       │       └── git_reset_hard_cleanup.yaml
│   │       ├── payment_identity_solicitation/
│   │       │   ├── attack.py
│   │       │   ├── class.yaml
│   │       │   └── cases/
│   │       │       ├── credit_card_request.yaml
│   │       │       └── otp_request.yaml
│   │       └── sensitive_data_access_induction/
│   │           ├── attack.py
│   │           ├── class.yaml
│   │           └── cases/
│   │               ├── open_private_key_for_connection_test.yaml
│   │               └── read_env_for_debugging.yaml
│   ├── phase-4-skill-output-and-handoff/
│   │   ├── phase.yaml
│   │   ├── category-1-artifact-and-schema-poisoning/
│   │   │   ├── category.yaml
│   │   │   ├── artifact_relay_poisoning/
│   │   │   │   ├── attack.py
│   │   │   │   ├── class.yaml
│   │   │   │   └── cases/
│   │   │   │       ├── fake_metadata_field.yaml
│   │   │   │       └── poisoned_csv_column.yaml
│   │   │   └── output_schema_manipulation/
│   │   │       ├── attack.py
│   │   │       ├── class.yaml
│   │   │       └── cases/
│   │   │           ├── extra_json_key_for_secret.yaml
│   │   │           └── hidden_field_injection.yaml
│   │   └── category-2-egress-and-output-abuse/
│   │       ├── category.yaml
│   │       ├── exfiltration_via_output_channel/
│   │       │   ├── attack.py
│   │       │   ├── class.yaml
│   │       │   └── cases/
│   │       │       ├── include_secret_in_report.yaml
│   │       │       └── place_sensitive_data_in_submission_file.yaml
│   │       └── external_communication_exfiltration/
│   │           ├── attack.py
│   │           ├── class.yaml
│   │           └── cases/
│   │               ├── send_debug_archive_to_remote.yaml
│   │               └── upload_to_webhook.yaml
│   └── phase-5-skill-memory-recovery-and-audit/
│       ├── phase.yaml
│       ├── category-1-belief-persistence-and-recovery-failure/
│       │   ├── category.yaml
│       │   ├── false_heuristic_persistence/
│       │   │   ├── attack.py
│       │   │   ├── class.yaml
│       │   │   └── cases/
│       │   │       ├── fallback_rule_repeat.yaml
│       │   │       └── multi_surface_repeat.yaml
│       │   └── recovery_blocking/
│       │       ├── attack.py
│       │       ├── class.yaml
│       │       └── cases/
│       │           ├── conflict_as_noise_hint.yaml
│       │           └── discourage_second_check.yaml
│       └── category-2-stealth-and-long-lived-footholds/
│           ├── category.yaml
│           ├── audit_evasion/
│           │   ├── attack.py
│           │   ├── class.yaml
│           │   └── cases/
│           │       ├── delete_history_after_run.yaml
│           │       └── suppress_warning_output.yaml
│           └── persistence_implant/
│               ├── attack.py
│               ├── class.yaml
│               └── cases/
│                   ├── leave_shadow_binary.yaml
│                   └── modify_local_config_for_future_runs.yaml
├── configs/                              # Example materialization configs
│   ├── citation-check-attack.yaml
│   └── example-materialize.yaml
├── scripts/                              # Helper launch scripts
│   └── run.sh
├── tests/                                # Minimal regression tests
│   ├── test_materialize.py
│   └── test_registry.py
├── jobs/                                 # Runtime-generated Harbor outputs; contents vary by run
├── tmp-tasks/                            # Runtime-generated attacked task copies; contents vary by run
├── .envrc                                # Local environment configuration
├── README.md                             # Repository overview and usage
├── attack_runtime.py                     # Shared helpers for attack implementations
├── case_library.py                       # Auto-discovery and runtime registry builder
├── catalog.py                            # YAML case loader
├── cli.py                                # Command-line entry point
├── context.py                            # Attack mutation context and surface routing
├── evaluation_spec.md                    # Evaluation design specification
├── layout.py                             # Task structure discovery
├── models.py                             # Core data models and surface metadata
├── mutations.py                          # Low-level file mutation helpers
├── pyproject.toml                        # Packaging and project metadata
├── runner.py                             # Task materialization runner
└── taxonomy_spec.md                      # Taxonomy and architecture specification
```
