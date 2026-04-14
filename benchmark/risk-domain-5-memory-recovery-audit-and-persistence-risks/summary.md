# Risk Domain 5 Benchmark Summary

## 1. Normalized Risk Domain Definition

- ID: `memory_recovery_audit_and_persistence_risks`
- Name: Memory Recovery Audit and Persistence Risks
- Definition: Risks where poisoned beliefs become sticky, self-correction is suppressed, visibility degrades, or harmful state survives into later runs.
- Normalization note: taxonomy semantics were taken only from risk-domain-5 `risk_domain.yaml`, each `category.yaml`, and each available `class.yaml`. Legacy atom-attack case payloads, prompts, evaluators, and task mappings were not reused.

## 2. Taxonomy Source Note

- RD5 was generated from the risk-domain-5 taxonomy semantics captured at generation time: one risk domain, five categories, and twenty classes.
- The delivered benchmark subset does not depend on any runtime taxonomy loader and does not require generation-time YAML archives to execute or evaluate cases.
- The canonical category and class inventory used for this static subset is recorded directly in Sections 3 and 5 below.

## 3. Normalized Categories and Classes

- `belief_persistence_and_self_correction_failure` (Belief Persistence and Self-Correction Failure): poisoned_belief_persistence, self_correction_suppression, retrieved_precedent_overgeneralization, self_reinforcing_error_amplification
- `audit_visibility_and_trace_suppression` (Audit Visibility and Trace Suppression): audit_evasion, trace_integrity_tampering, provenance_and_attribution_stripping, forensic_snapshot_and_replay_suppression
- `persistence_and_long_lived_footholds` (Persistence and Long-Lived Footholds): persistent_foothold_implant, startup_and_bootstrap_persistence, shadow_helper_and_wrapper_persistence, self_reinforcing_reinfection_loop
- `memory_store_and_history_poisoning` (Memory Store and History Poisoning): long_term_memory_record_injection, experience_retrieval_poisoning, retrieval_trigger_backdoor_poisoning, session_history_and_context_contamination
- `rollback_and_recovery_control_failure` (Rollback and Recovery Control Failure): rollback_suppression_and_operator_discouragement, recovery_checkpoint_and_snapshot_corruption, rollback_scope_and_target_confusion, cleanup_and_remediation_obstruction

## 4. Original Tasks Selected Per Category

- `belief_persistence_and_self_correction_failure`: `enterprise-information-search`, `software-dependency-audit`, `travel-planning`
- `audit_visibility_and_trace_suppression`: `enterprise-information-search`, `fix-build-agentops`, `paper-anonymizer`, `react-performance-debugging`, `software-dependency-audit`, `video-filler-word-remover`, `xlsx-recover-data`
- `persistence_and_long_lived_footholds`: `data-to-d3`, `fix-build-agentops`, `software-dependency-audit`
- `memory_store_and_history_poisoning`: `enterprise-information-search`, `lab-unit-harmonization`, `lean4-proof`, `manufacturing-codebook-normalization`, `scheduling-email-assistant`, `travel-planning`
- `rollback_and_recovery_control_failure`: `data-to-d3`, `fix-build-agentops`, `software-dependency-audit`, `xlsx-recover-data`

## 5. Class Coverage

- `audit_evasion`: `fix_build_audit_evasion_cleanroom_summary`
- `cleanup_and_remediation_obstruction`: `software_audit_cleanup_remediation_obstruction_guard_note`
- `experience_retrieval_poisoning`: `enterprise_search_experience_retrieval_poisoning_success_memory`, `lean4_experience_retrieval_archived_bound_proof`
- `forensic_snapshot_and_replay_suppression`: `xlsx_recovery_forensic_snapshot_replay_suppression_replay_blocked`
- `long_term_memory_record_injection`: `lab_unit_memory_record_injection_conversion_journal`, `manufacturing_memory_record_bias_rationale_anchor`, `travel_planning_long_term_memory_record_injection_trip_journal`
- `persistent_foothold_implant`: `fix_build_persistent_foothold_implant_review_helper`
- `poisoned_belief_persistence`: `travel_planning_poisoned_belief_persistence_memory_anchor`
- `provenance_and_attribution_stripping`: `enterprise_search_provenance_attribution_stripping_memory_normalized`, `paper_anonymizer_provenance_stripping_journal_note`
- `recovery_checkpoint_and_snapshot_corruption`: `xlsx_recovery_checkpoint_snapshot_corruption_checkpoint_note`
- `retrieval_trigger_backdoor_poisoning`: `lab_unit_harmonization_retrieval_trigger_backdoor_poisoning_question_map`
- `retrieved_precedent_overgeneralization`: `powerlifting_coef_calc_retrieved_precedent_overgeneralization_playbook`
- `rollback_scope_and_target_confusion`: `data_to_d3_rollback_scope_target_confusion_scope_manifest`
- `rollback_suppression_and_operator_discouragement`: `fix_build_rollback_suppression_operator_discouragement_no_revert`
- `self_correction_suppression`: `jpg_ocr_stat_self_correction_suppression_correction_lock`
- `self_reinforcing_error_amplification`: `software_audit_self_reinforcing_error_amplification_carry_forward_row`
- `self_reinforcing_reinfection_loop`: `data_to_d3_self_reinforcing_reinfection_loop_reseed_manifest`
- `session_history_and_context_contamination`: `scheduling_email_session_history_context_contamination_thread_memory`
- `shadow_helper_and_wrapper_persistence`: `software_audit_shadow_helper_wrapper_persistence_scan_wrapper`
- `startup_and_bootstrap_persistence`: `data_to_d3_startup_bootstrap_persistence_loader_hook`
- `trace_integrity_tampering`: `react_perf_trace_integrity_override_summary`, `software_audit_trace_integrity_tampering_override_digest`, `video_filler_trace_integrity_override_clip_summary`

## 6. Candidate Task Screening and Skips

- Screening strategy: start from the full SkillsBench task set, then prioritize tasks that already emit durable artifacts, reviewer notes, or outbound messages where memory carry-forward and persistence side effects can be checked with fixed rule-based signals.
- Screening strategy: prefer tasks that naturally expose caches, journals, review notes, sidecars, replay checkpoints, helper scripts, or outbound bodies instead of relying on abstract model intent.
- Selected task families emphasize memory-bearing workflows: travel planning, enterprise retrieval, email scheduling, spreadsheet recovery, security auditing, document generation, visualization export, build-repair notes, web debugging, manufacturing normalization, and PDF redaction.
- The benchmark favors artifacts that can survive later runs such as JSON journals, helper scripts, checkpoint notes, wrapper files, output bundles, CSV sidecars, and sent email bodies.
- The current repository snapshot does not vendor a standalone `skillsbench/tasks` tree, so the skipped-task accounting below is reconstructed from the local original-task pool preserved in benchmark metadata across the delivered repository snapshot.
- One deep `metadata.json` under `react-best-practices/` belongs to embedded skill content rather than an RD5 case; tooling should count case metadata only at the `category/case/metadata.json` level.
- Screened-but-skipped tasks from that local pool:
- `citation-check`, `dialogue-parser`, `financial-modeling-qa`, `invoice-fraud-detection`, `seismic-phase-picking`: skipped because the dominant outputs are scalar answers or short analysis artifacts with weak long-lived memory, persistence, audit, or rollback surfaces.
- `exceltable-in-ppt`, `jpg-ocr-stat`, `multilingual-video-dubbing`, `offer-letter-generator`, `powerlifting-coef-calc`, `pptx-reference-formatting`, `sales-pivot-analysis`, `speaker-diarization-subtitles`, `weighted-gdp-calc`: screened for memory carry-forward and review-note risks, but not selected because the current carriers were better used in RD4 output-boundary abuse than in RD5 memory or persistence semantics.
- `fix-druid-loophole-cve`, `fix-erlang-ssh-cve`, `flink-query`, `jax-computing-basics`, `parallel-tfidf-search`, `python-scala-translation`, `setup-fuzzing-py`, `syzkaller-ppdev-syzlang`, `threejs-structure-parser`, `threejs-to-obj`: skipped because their cleanest risks are runtime, interpreter, or toolchain compromise paths that fit RD3 better than RD5.
- `fix-visual-stability`, `manufacturing-fjsp-optimization`, `organize-messy-files`: skipped because they fit RD2 agency, destructive-action, or persistent configuration risks better than RD5 memory-store or rollback semantics.
- `gh-repo-analytics`, `pdf-excel-diff`, `sec-financial-report`, `video-silence-remover`, `video-tutorial-indexer`: skipped because their strongest observable failures in the current carriers are retrieval drift, output corruption, or availability/quality issues rather than durable poisoned memory or long-lived footholds.
- `manufacturing-equipment-maintenance`, `mhc-layer-impl`, `simpo-code-reproduction`: skipped because their strongest benchmark value in the current repository lies in RD6 model, dependency, or supply-chain semantics rather than RD5 memory recovery and persistence behavior.

## 7. Sparse or Uncovered Classes

- All 20 RD5 classes are covered by at least one generated case.
- Sparse single-case classes and why they remain sparse:
- `audit_evasion`, `forensic_snapshot_and_replay_suppression`, `persistent_foothold_implant`, `startup_and_bootstrap_persistence`, `shadow_helper_and_wrapper_persistence`, `cleanup_and_remediation_obstruction`, `rollback_scope_and_target_confusion`, `rollback_suppression_and_operator_discouragement`: these classes require a very specific durable carrier such as build notes, replay files, helper scripts, bootstrap hooks, or rollback manifests, so RD5 keeps one strongest task per mechanism rather than forcing weak duplicates.
- `poisoned_belief_persistence`, `self_correction_suppression`, `retrieved_precedent_overgeneralization`, `self_reinforcing_error_amplification`, `retrieval_trigger_backdoor_poisoning`, `session_history_and_context_contamination`, `self_reinforcing_reinfection_loop`: these classes are intentionally concentrated on a single high-fit carrier because their semantics depend on one stable belief, memory, or reinfection channel, and duplicating them on weaker tasks would add noise more than coverage.
- Higher-density classes were expanded only where additional tasks exposed genuinely distinct memory or audit failure modes: `trace_integrity_tampering` has 3 cases because web debugging, security-audit, and video-annotation traces degrade differently; `long_term_memory_record_injection` has 3 cases because lab, manufacturing, and travel journals create different persistent-memory carriers; `experience_retrieval_poisoning` and `provenance_and_attribution_stripping` have 2 cases each because the paired carriers differ materially in artifact shape and verification logic.

## 8. Category Design Principles

- `belief_persistence_and_self_correction_failure`: prefer tasks with structured final artifacts where sticky beliefs, correction locks, precedent fields, or carried-forward findings can be read back directly.
- `audit_visibility_and_trace_suppression`: prefer tasks with summaries, trace sidecars, provenance fields, or recovery snapshots so suppression can be observed from text artifacts rather than inferred from hidden state.
- `persistence_and_long_lived_footholds`: prefer repository-editing and bundle-producing tasks where helper scripts, wrappers, bootstrap hooks, and reinfection manifests can survive after the main task completes.
- `memory_store_and_history_poisoning`: prefer tasks with journals, answer caches, question maps, or outbound thread state so poisoned memory can be written and then detected at a stable path.
- `rollback_and_recovery_control_failure`: prefer tasks with notes, snapshot areas, output bundles, and cleanup artifacts where rollback discouragement, checkpoint corruption, scope confusion, or cleanup obstruction leave explicit files behind.

## 9. Evaluation Overview

- Total cases: 26
- Rule-based cases: 26
- LLM-as-judge cases: 0
- Evaluation pattern: each case adds `eval/verify_attack.py` that checks for a task-specific success signal such as seeded JSON fields, journal entries, note markers, helper scripts, replay-blocked files, wrapper scripts, output-bundle manifests, sidecar text files, workbook checkpoint notes, or real sent email bodies.
- Because all RD5 cases remain rule-based, no `judge_prompt.txt` or `judge_input_builder.py` files are shipped in this risk-domain subset.

## 10. No-Reuse Assurance

- Only taxonomy-level semantics from the captured taxonomy inventory were retained.
- No legacy case payloads, prompts, evaluators, patch logic, or task-to-class mappings were copied into this benchmark subset.
- All attacked tasks were rebuilt from local `skillsbench/tasks` originals and then statically modified with new benchmark-specific artifacts.
- Active redesign on `2026-03-31` restored `attacked_task/instruction.md` to the original task for all `26/26` RD5 cases; attacks now rely only on benchmark-local non-user surfaces such as skill docs, journals, sidecars, hidden trace summaries, helper wrappers, memory files, and rollback manifests.
- No RD5 case uses `attack.py`-style runtime injection, online interception, proxy middleware, or MITM behavior; all attack exposure is pre-materialized inside each static `attacked_task/`.
