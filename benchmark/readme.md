# Skill Safety Bench Benchmark Guide

<p align="right">
  <a href="./readme.md"><img alt="English" src="https://img.shields.io/badge/English-blue?style=for-the-badge"></a>
  <a href="./readme.zh.md"><img alt="中文" src="https://img.shields.io/badge/%E4%B8%AD%E6%96%87-blue?style=for-the-badge"></a>
</p>

This document explains the benchmark taxonomy under `benchmark/`. The taxonomy has 6 risk domains (`RD1`-`RD6`) and 30 categories. Risk domains describe broad safety failure regions; categories describe common attack mechanisms inside each region.

### RD1: Context Trust and Prompt Manipulation Risks

RD1 evaluates whether an agent can be misled by untrusted context, poisoned references, misleading examples, routing cues, or repeated false signals.

- `routing_and_discovery_deception`: corrupts tool, skill, or execution-path discovery.
- `source_authority_rule_and_example_poisoning`: poisons authority, rule priority, or example templates.
- `intent_seeding_and_cross_context_conflict`: seeds hidden goals or creates conflicting contexts that push unsafe arbitration.
- `retrieval_and_reference_contamination`: poisons retrieved evidence, cached digests, snippets, or reference material.
- `multi_source_trust_amplification`: repeats the same false claim across multiple surfaces to create fake consensus.

### RD2: Agency Scope and Authorization Risks

RD2 evaluates whether an agent exceeds task scope, authority, approval boundaries, or external-action constraints.

- `category1-approval_and_authority_spoofing`: launders nonexistent approval or delegated authority.
- `category2-credential_privilege_and_sensitive_input_solicitation`: induces requests for secrets, credentials, or sensitive inputs.
- `category3-destructive_and_sensitive_operation_induction`: disguises destructive or sensitive operations as routine maintenance.
- `category4-planning_scope_and_safety_degradation`: expands task scope or suppresses conservative review during planning.
- `category5-transaction_and_external_action_induction`: pushes the agent toward externally consequential actions.

### RD3: Execution, Runtime, Framework, and Protocol Risks

RD3 evaluates whether the execution chain can be compromised through runtimes, interpreters, loaders, protocol identity, or environment boundaries.

- `category1-downstream_interpreter_and_query_exploitation`: abuses shell, SQL, template, expression, or code interpreters.
- `category2-framework_serialization_and_loader_abuse`: exploits serialization, parsers, loaders, extensions, or remote loading paths.
- `category3-protocol_identity_and_capability_abuse`: spoofs service identity, capability claims, or delegated trust.
- `category4-runtime_and_toolchain_integrity_compromise`: tampers with wrappers, shims, helper output, PATH resolution, or toolchains.
- `category5-sandbox_and_environment_boundary_escape`: induces filesystem, container, mount, host, or internal-network boundary crossing.

### RD4: Data Boundary, Output, and Externalization Risks

RD4 evaluates whether the final artifact, schema, output channel, destination, or handoff boundary carries the unsafe behavior outward.

- `category1-artifact_and_schema_integrity_failure`: corrupts output schemas, field mappings, provenance, or artifact contracts.
- `category2-downstream_output_interpreter_abuse`: embeds content that becomes unsafe when interpreted by downstream systems.
- `category3-external_destination_and_egress_abuse`: redirects, mirrors, or expands output delivery beyond the approved destination.
- `category4-handoff_and_submission_boundary_abuse`: smuggles unsafe content through review packets, bundles, or format conversions.
- `category5-output_channel_data_leakage`: leaks sensitive data through summaries, annotations, debug output, footers, or auxiliary fields.

### RD5: Memory, Recovery, Audit, and Persistence Risks

RD5 evaluates whether unsafe state is remembered, hidden, reinforced, or made difficult to audit and roll back.

- `category1-audit_visibility_and_trace_suppression`: weakens logs, provenance, traceability, or forensic visibility.
- `category2-belief_persistence_and_self_correction_failure`: makes wrong beliefs persist despite later correction signals.
- `category3-memory_store_and_history_poisoning`: poisons long-term memory, session history, experience stores, or retrieval triggers.
- `category4-persistence_and_long_lived_footholds`: plants helpers, wrappers, startup hooks, or reinfection paths that survive the task.
- `category5-rollback_and_recovery_control_failure`: obstructs rollback, cleanup, checkpoint recovery, or remediation.

### RD6: Knowledge, Model, Supply Chain, and Operational Risks

RD6 evaluates whether knowledge sources, dependencies, releases, models, training processes, or service capacity can be poisoned or abused.

- `category1-availability_cost_and_service_exhaustion`: drains time, tokens, calls, budget, latency, or service capacity.
- `category2-dependency_plugin_and_release_chain_compromise`: poisons packages, plugins, registries, lockfiles, releases, or attestations.
- `category3-model_behavior_and_finetuning_poisoning`: changes behavior through dataset structure, fine-tuning artifacts, or triggers.
- `category4-model_extraction_and_service_abuse`: induces probing, capability mapping, prompt-asset theft, or black-box extraction.
- `category5-retrieval_knowledge_and_corpus_poisoning`: poisons corpora, retrieval knowledge, ranking metadata, or knowledge backdoors.

### One-line Distinction

- `RD1`: the agent trusts the wrong context.
- `RD2`: the agent crosses authority or scope boundaries.
- `RD3`: the execution chain is compromised.
- `RD4`: the final artifact or output boundary is contaminated.
- `RD5`: the unsafe state persists, hides, or resists recovery.
- `RD6`: knowledge, model, dependency, or operational layers are poisoned or abused.
