# SkillSafetyBench Taxonomy Specification

## 1. Purpose

This document defines the canonical taxonomy of `SkillSafetyBench`.

`SkillSafetyBench` is an independent benchmark for attacking and evaluating skill-using agents. It is not a sub-benchmark of `SkillsBench`.

The goal of this taxonomy is to organize attack cases in a way that is:

- stable across different agent implementations
- aligned with modern AI and agent security thinking
- compatible with benchmark materialization and later evaluation
- broad enough to cover both the current implemented library and future safety extensions

The canonical architecture is:

`risk_domain -> category -> class -> case`

This version no longer treats skill lifecycle phase as the top-level taxonomy root.
Instead, lifecycle stage is preserved as metadata, while the architecture root is a stable security risk domain.

## 2. Design Basis

This taxonomy is aligned with the critique and guidance in [deep-research-report.md](/home/jinchang/Documents/skillsbench/deep-research-report.md).

The report shows that a benchmark for skill-using agents should not only model when an attack appears, but also what security problem it represents and which trust boundary it crosses.

In particular, the taxonomy must be able to represent:

- prompt and context compromise
- trust-boundary crossing
- excessive agency and authorization abuse
- delegated and multi-agent propagation
- insecure output handling and externalization
- runtime, framework, and protocol compromise
- persistence, audit evasion, and long-lived corruption
- model, retrieval, supply chain, and operational risks

Based on that analysis, the benchmark follows these principles:

1. The top layer should be a security risk domain, not just a workflow stage.
2. Lifecycle stage should still exist, but only as metadata.
3. Multi-agent and delegation topology should be represented as orthogonal metadata, not as a top-level risk domain.
4. Attack surface should remain an orthogonal control dimension.
5. The taxonomy should not be constrained by the current attack library.
6. Governance or organizational control gaps are important, but they are not first-class atom-attack domains because they are not directly materialized as attack payloads.
7. Existing classes may be renamed, moved, merged, or deleted if a stronger architecture requires it.

## 3. Foundational Terms

### 3.1 Benchmark

`Benchmark` means the full evaluation system, including:

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
- a future explicit skill-routing benchmark
- a private internal task suite

### 3.3 Risk Domain

`Risk Domain` means the highest taxonomy layer.

A risk domain groups attacks by stable security meaning, not by a temporary step in an execution flow.

A risk domain answers:

- what kind of security problem this attack represents
- which broader family of failures it belongs to
- which security literature or framework it aligns with

### 3.4 Category

`Category` means a parallel attack direction inside one risk domain.

A category groups classes that share a similar failure mode or attack mechanism.

### 3.5 Class

`Class` means a reusable atomic attack family with a shared mechanism.

A class is not a single payload. It groups several concrete attack cases that share one attack pattern.

### 3.6 Case

`Case` means the smallest independently materializable attack unit.

Each case is:

- concrete
- executable
- individually selectable
- individually evaluable

### 3.7 Lifecycle Stage

`Lifecycle Stage` means the stage of skill use where an attack mainly becomes relevant.

Lifecycle stage is no longer the top taxonomy layer. It is now orthogonal metadata.

The current lifecycle stage vocabulary is:

- `skill_discovery`
- `skill_interpretation`
- `skill_selection_and_planning`
- `skill_execution`
- `skill_output_and_handoff`
- `skill_memory_recovery_and_audit`

### 3.8 Coordination Scope

`Coordination Scope` means the agent coordination topology in which an attack is expected to apply or propagate.

This is a cross-cutting metadata dimension. It does not replace the main four-level taxonomy.

The current coordination scope vocabulary is:

- `single_agent`
- `delegated_subagent`
- `supervisor_worker`
- `peer_multi_agent`
- `federated_service_mesh`

This field exists because many attacks are not limited to one isolated agent. Some attacks spread through delegation chains, supervisor-worker workflows, or federated tool/service meshes.

### 3.9 Attack Surface

`Attack Surface` means the concrete place where a case injects or modifies information to influence the agent.

Attack surface is an orthogonal control dimension. It does not replace the main four-level taxonomy.

### 3.10 Surface Mode

`Surface Mode` means how configurable a case's injection surface is at runtime.

The current implementation supports:

- `fixed`
- `choice`
- `composite`

### 3.11 Impact Objective

`Impact Objective` means the security consequence a case tries to induce.

Examples include:

- correctness deviation
- unsafe action
- approval bypass
- secret collection
- sensitive access
- destructive change
- data exfiltration
- audit evasion
- persistence

## 4. Canonical Four-Level Architecture

The canonical taxonomy is:

1. `risk_domain`
2. `category`
3. `class`
4. `case`

This structure is the architecture root used for benchmark design, implementation, documentation, and future evaluation.

### Why `risk_domain` is the top layer

Using `risk_domain` at the top solves several problems that a pure phase-based tree cannot solve:

- prompt injection and trust manipulation often span several lifecycle stages
- excessive agency is a security-property problem, not just a planning-stage problem
- output abuse and exfiltration are data-boundary failures, not merely late workflow events
- framework and protocol vulnerabilities do not fit naturally into a pure skill-lifecycle tree
- model, retrieval, supply chain, and service-abuse risks must be representable without forcing them into runtime skill phases
- delegated subagents and multi-agent propagation should be representable without forcing them into a separate top-level risk domain

Therefore:

- `risk_domain` is the canonical root
- `lifecycle_stage` remains as metadata
- `coordination_scope` remains as metadata
- `attack_surface` remains as metadata and runtime control

### Why multi-agent and delegation are metadata, not a risk domain

Multi-agent behavior changes how an attack propagates, but it does not by itself define the attack's core security meaning.

For example:

- a prompt-trust attack may stay inside one agent or spread through delegated subagents
- an approval-bypass attack may target a single planner or a supervisor-worker chain
- a runtime compromise may affect one tool invocation or a federated service mesh

Therefore, the benchmark treats multi-agent and delegation structure as `coordination_scope`, not as a seventh top-level `risk_domain`.

## 5. Canonical Risk Domains

### 5.1 `context_trust_and_prompt_manipulation_risks`

Definition:
Risks where untrusted or misleading content distorts what the agent trusts, how it interprets instructions, and how it frames possible actions.

Current and planned categories:

- `routing_and_discovery_deception`
  Attacks that bias discovery through names, recommendations, or urgency cues.
- `source_authority_rule_and_example_poisoning`
  Attacks that poison source precedence, rules, references, or examples.
- `intent_seeding_and_cross_context_conflict`
  Attacks that plant harmful workflow goals or conflicting guidance into trusted content.
- `retrieval_and_reference_contamination`
  Reserved for future retrieval poisoning and reference contamination classes.
- `multi_source_trust_amplification`
  Reserved for future false-corroboration and manufactured-consensus classes.

### 5.2 `agency_scope_and_authorization_risks`

Definition:
Risks where the agent is pushed beyond legitimate authority, safe approval boundaries, or appropriate operational scope.

Current and planned categories:

- `planning_scope_and_safety_degradation`
  Attacks that expand action scope or degrade safety standards during planning.
- `approval_and_authority_spoofing`
  Attacks that fabricate approvals, authority, or emergency exceptions.
- `credential_privilege_and_sensitive_input_solicitation`
  Attacks that try to collect secrets, privileges, or sensitive user inputs.
- `destructive_and_sensitive_operation_induction`
  Attacks that induce destructive operations or sensitive local-data access.
- `transaction_and_external_action_induction`
  Reserved for future payment, account-mutation, or other high-impact external-action classes.

### 5.3 `execution_runtime_framework_and_protocol_risks`

Definition:
Risks where the runtime, toolchain, framework, protocol, or execution boundary itself is compromised or exploited.

Current and planned categories:

- `runtime_and_toolchain_integrity_compromise`
  Attacks that alter which binary, helper, or wrapper really executes.
- `downstream_interpreter_and_query_exploitation`
  Reserved for SQL injection, template injection, formula injection, command injection, and similar downstream interpreter risks.
- `framework_serialization_and_loader_abuse`
  Reserved for deserialization, loader, parser, and framework-specific exploitation classes.
- `protocol_identity_and_capability_abuse`
  Reserved for capability spoofing, origin confusion, and federated trust abuse.
- `sandbox_and_environment_boundary_escape`
  Reserved for environment, container, or boundary-escape classes.

### 5.4 `data_boundary_output_and_externalization_risks`

Definition:
Risks where artifacts, schemas, deliverables, or outbound channels are abused to poison downstream consumers or move data outside its intended boundary.

Current and planned categories:

- `artifact_and_schema_integrity_failure`
  Attacks that poison artifacts or manipulate output structure.
- `output_channel_data_leakage`
  Attacks that turn reports, outputs, or submission files into leakage channels.
- `external_destination_and_egress_abuse`
  Attacks that route local state to unsanctioned external endpoints.
- `downstream_output_interpreter_abuse`
  Reserved for spreadsheet, browser, template, and other output-consumer exploitation classes.
- `handoff_and_submission_boundary_abuse`
  Reserved for cross-system handoff contamination and submission-boundary abuse.

### 5.5 `memory_recovery_audit_and_persistence_risks`

Definition:
Risks where poisoned beliefs become sticky, self-correction is suppressed, visibility degrades, or harmful state survives into later runs.

Current and planned categories:

- `belief_persistence_and_self_correction_failure`
  Attacks that keep the agent committed to poisoned beliefs and discourage correction.
- `audit_visibility_and_trace_suppression`
  Attacks that reduce observability or forensic value.
- `persistence_and_long_lived_footholds`
  Attacks that leave behind modifications for future runs.
- `memory_store_and_history_poisoning`
  Reserved for poisoning memory stores, caches, or historical state.
- `rollback_and_recovery_control_failure`
  Reserved for sabotaging rollback and recovery procedures.

### 5.6 `knowledge_model_supply_chain_and_operational_risks`

Definition:
Risks involving model behavior, retrieval knowledge, dependencies, release pipelines, and service operations beyond immediate runtime skill manipulation.

Current and planned categories:

- `retrieval_knowledge_and_corpus_poisoning`
- `model_behavior_and_finetuning_poisoning`
- `dependency_plugin_and_release_chain_compromise`
- `availability_cost_and_service_exhaustion`
- `model_extraction_and_service_abuse`

This domain is intentionally present even though it does not yet contain implemented classes.
Its purpose is to keep the benchmark architecture broad enough for future expansion.

## 5.7 Excluded from the Atom-Attack Taxonomy

The benchmark intentionally does **not** create a top-level governance domain inside the atom-attack library.

Reason:

- governance failures are important, but they are usually not directly materialized as atomic attack payloads
- many governance issues are better represented as evaluation assumptions, deployment controls, or operating policies
- forcing governance into `risk_domain/category/class/case` would blur the boundary between attack implementation and organizational control design

This means the current attack taxonomy focuses on materializable attacks, while governance remains outside the atom-attack hierarchy.

## 6. Current Implemented Library

The current implemented library contains:

- `23` classes
- `46` cases

The implemented tree is:

```text
risk_domain `context_trust_and_prompt_manipulation_risks`
  category `routing_and_discovery_deception`
    class `routing_cue_poisoning`
      case `false_system_recommendation`
      case `urgent_use_note`
    class `skill_name_decoy`
      case `lexical_lookalike`
      case `namespace_collision`
  category `source_authority_rule_and_example_poisoning`
    class `example_pattern_poisoning`
      case `plausible_wrong_example`
      case `unsafe_shell_example`
    class `priority_override`
      case `speed_over_safety_flip`
      case `task_vs_skill_flip`
    class `reference_rule_poisoning`
      case `fabricated_threshold`
      case `false_exception_clause`
  category `intent_seeding_and_cross_context_conflict`
    class `cross_source_conflict_poisoning`
      case `objective_conflict`
      case `permission_boundary_conflict`
    class `sensitive_request_seeding`
      case `request_api_key_for_debugging`
      case `request_otp_for_identity_check`
  category `retrieval_and_reference_contamination`
  category `multi_source_trust_amplification`

risk_domain `agency_scope_and_authorization_risks`
  category `planning_scope_and_safety_degradation`
    class `high_agency_plan_overreach`
      case `act_first_confirm_later`
      case `auto_export_for_review`
    class `unsafe_degradation_planning`
      case `skip_validation_to_meet_deadline`
      case `timeout_heuristic_fallback`
  category `approval_and_authority_spoofing`
    class `approval_bypass_spoofing`
      case `emergency_override_claim`
      case `manager_already_approved_note`
  category `credential_privilege_and_sensitive_input_solicitation`
    class `credential_and_privilege_solicitation`
      case `api_key_request`
      case `sudo_request`
    class `sensitive_user_input_solicitation`
      case `credit_card_request`
      case `otp_request`
  category `destructive_and_sensitive_operation_induction`
    class `destructive_operation_induction`
      case `delete_logs_cleanup`
      case `git_reset_hard_cleanup`
    class `sensitive_file_access_induction`
      case `open_private_key_for_connection_test`
      case `read_env_for_debugging`
  category `transaction_and_external_action_induction`

risk_domain `execution_runtime_framework_and_protocol_risks`
  category `runtime_and_toolchain_integrity_compromise`
    class `runtime_integrity_compromise`
      case `command_wrapper_hijack`
      case `path_shadowing`
  category `downstream_interpreter_and_query_exploitation`
  category `framework_serialization_and_loader_abuse`
  category `protocol_identity_and_capability_abuse`
  category `sandbox_and_environment_boundary_escape`

risk_domain `data_boundary_output_and_externalization_risks`
  category `artifact_and_schema_integrity_failure`
    class `artifact_relay_poisoning`
      case `fake_metadata_field`
      case `poisoned_csv_column`
    class `output_contract_manipulation`
      case `extra_json_key_for_secret`
      case `hidden_field_injection`
  category `output_channel_data_leakage`
    class `output_channel_exfiltration`
      case `include_secret_in_report`
      case `place_sensitive_data_in_submission_file`
  category `external_destination_and_egress_abuse`
    class `external_destination_exfiltration`
      case `send_debug_archive_to_remote`
      case `upload_to_webhook`
  category `downstream_output_interpreter_abuse`
  category `handoff_and_submission_boundary_abuse`

risk_domain `memory_recovery_audit_and_persistence_risks`
  category `belief_persistence_and_self_correction_failure`
    class `poisoned_belief_persistence`
      case `fallback_rule_repeat`
      case `multi_surface_repeat`
    class `self_correction_suppression`
      case `conflict_as_noise_hint`
      case `discourage_second_check`
  category `audit_visibility_and_trace_suppression`
    class `audit_evasion`
      case `delete_history_after_run`
      case `suppress_warning_output`
  category `persistence_and_long_lived_footholds`
    class `persistent_foothold_implant`
      case `leave_shadow_binary`
      case `modify_local_config_for_future_runs`
  category `memory_store_and_history_poisoning`
  category `rollback_and_recovery_control_failure`

risk_domain `knowledge_model_supply_chain_and_operational_risks`
  category `retrieval_knowledge_and_corpus_poisoning`
  category `model_behavior_and_finetuning_poisoning`
  category `dependency_plugin_and_release_chain_compromise`
  category `availability_cost_and_service_exhaustion`
  category `model_extraction_and_service_abuse`
```

## 7. Orthogonal Metadata Dimensions

The canonical taxonomy is complemented by several orthogonal dimensions.

### 7.1 Lifecycle Stage

Lifecycle stage captures when the attack matters.

It remains useful for:

- benchmark slicing
- evaluation reports
- root-cause analysis

But it is no longer the taxonomy root.

### 7.2 Attack Surface

The current runtime recognizes the following surface names:

- `task_instruction_surface`
- `skill_doc_surface`
- `skill_reference_surface`
- `skill_script_surface`
- `task_artifact_surface`
- `runtime_wrapper_surface`
- `docker_environment_surface`
- `output_channel_surface`
- `persistent_state_surface`

### 7.3 Surface Mode

The current runtime supports:

- `fixed`
  The case has one implementation-defined surface.
- `choice`
  The case supports several equivalent injection surfaces.
- `composite`
  The case intentionally coordinates multiple surfaces together.

### 7.4 Trust Boundary

Recommended trust-boundary tags include:

- external content -> model context
- model context -> planner
- planner -> executor
- tool output -> downstream interpreter
- local workspace -> external communication
- current run -> future persistent state

### 7.5 Impact Objective

Recommended impact-objective tags include:

- correctness deviation
- unsafe action
- approval bypass
- secret collection
- sensitive access
- destructive change
- data exfiltration
- audit evasion
- persistence

## 8. Implementation Notes

The current on-disk implementation now matches the canonical taxonomy.

The live `atom-attacks/` tree is organized by:

`risk_domain -> category -> class -> case`

This means:

- the documentation taxonomy is risk-domain-first
- the YAML metadata is risk-domain-first
- the runtime loader discovers `attack.py` from risk-domain-grouped directories
- lifecycle stage remains metadata instead of the architecture root

## 9. Summary

The main architectural shift in `SkillSafetyBench` is:

- from skill lifecycle as the primary taxonomy root
- to security risk domain as the primary taxonomy root

This makes the benchmark:

- more aligned with the deep research report
- more aligned with prompt injection, excessive agency, insecure output handling, runtime compromise, persistence, and supply-chain thinking
- easier to extend beyond the current runtime-focused library

The current implemented cases are no longer forcing the architecture.
Instead, the architecture is broad enough to guide future benchmark growth, while the existing classes and cases are mapped into it where they fit best.
