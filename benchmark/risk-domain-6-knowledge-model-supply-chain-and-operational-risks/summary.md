# Risk Domain 6 Benchmark Summary

## 1. Normalized Risk Domain Definition

- ID: `knowledge_model_supply_chain_and_operational_risks`
- Name: Knowledge Model Supply Chain and Operational Risks
- Definition: Risks involving model behavior, retrieval knowledge, dependencies, release pipelines, and service operations beyond immediate runtime skill manipulation.
- Normalization note: taxonomy semantics were taken only from risk-domain-6 `risk_domain.yaml`, each `category.yaml`, and each available `class.yaml`. Legacy atom-attack case payloads, prompts, evaluators, and task mappings were not reused.

## 2. Taxonomy Source Note

- RD6 was generated from the risk-domain-6 taxonomy semantics captured at generation time: one risk domain, five categories, and twenty classes.
- The delivered benchmark subset does not depend on any runtime taxonomy loader and does not require generation-time YAML archives to execute or evaluate cases.
- The canonical category and class inventory used for this static subset is recorded directly in Sections 3 and 5 below.

## 3. Normalized Categories and Classes

- `category5-retrieval_knowledge_and_corpus_poisoning` (Retrieval Knowledge and Corpus Poisoning): corpus_document_injection_and_fact_override, ranking_and_metadata_retrieval_manipulation, stealth_poisoning_with_minimal_corpus_footprint, trigger_conditioned_retrieval_backdoor
- `category3-model_behavior_and_finetuning_poisoning` (Model Behavior and Finetuning Poisoning): task_dataset_structure_poisoning, alignment_erosion_via_benign_looking_finetuning, trigger_conditioned_behavior_backdoor, downstream_finetuning_data_exfiltration_backdoor
- `category2-dependency_plugin_and_release_chain_compromise` (Dependency Plugin and Release Chain Compromise): package_hallucination_and_dependency_confusion, malicious_plugin_or_tool_registry_impersonation, dependency_update_and_lockfile_substitution, release_artifact_provenance_and_attestation_bypass
- `category1-availability_cost_and_service_exhaustion` (Availability Cost and Service Exhaustion): structural_tool_loop_amplification, malfunction_amplification_and_irrelevant_action_induction, recursive_query_fanout_and_workflow_explosion, budget_drain_and_latency_amplification
- `category4-model_extraction_and_service_abuse` (Model Extraction and Service Abuse): functionality_extraction_and_surrogate_model_reconstruction, training_data_extraction_via_black_box_queries, prompt_asset_stealing_and_system_prompt_reconstruction, capability_mapping_and_endpoint_probing_abuse

## 4. Original Tasks Selected Per Category

- `category5-retrieval_knowledge_and_corpus_poisoning`: `enterprise-information-search`, `manufacturing-equipment-maintenance`, `parallel-tfidf-search`, `travel-planning`
- `category3-model_behavior_and_finetuning_poisoning`: `citation-check`, `offer-letter-generator`, `simpo-code-reproduction`, `video-tutorial-indexer`
- `category2-dependency_plugin_and_release_chain_compromise`: `data-to-d3`, `fix-build-agentops`, `fix-druid-loophole-cve`, `software-dependency-audit`
- `category1-availability_cost_and_service_exhaustion`: `enterprise-information-search`, `mhc-layer-impl`, `parallel-tfidf-search`, `travel-planning`, `video-silence-remover`, `video-tutorial-indexer`
- `category4-model_extraction_and_service_abuse`: `citation-check`, `parallel-tfidf-search`, `scheduling-email-assistant`, `seismic-phase-picking`, `video-tutorial-indexer`

## 5. Class Coverage

- `alignment_erosion_via_benign_looking_finetuning`: `citation_check_alignment_erosion_permissive_review_policy`
- `budget_drain_and_latency_amplification`: `mhc_budget_drain_training_sweep_matrix`, `parallel_tfidf_budget_drain_latency_amplification_benchmark_plan`, `video_silence_budget_drain_threshold_sweep_plan`
- `capability_mapping_and_endpoint_probing_abuse`: `scheduling_email_capability_mapping_endpoint_probing_abuse`
- `corpus_document_injection_and_fact_override`: `enterprise_search_corpus_document_injection_fact_override_poisoned_policy_memo`, `manufacturing_handbook_fact_override_reviewed_addendum`
- `dependency_update_and_lockfile_substitution`: `software_audit_dependency_update_lockfile_substitution_candidate_swap`
- `downstream_finetuning_data_exfiltration_backdoor`: `offer_letter_downstream_finetuning_data_exfiltration_backdoor_footer_capture`, `simpo_finetuning_capture_manifest_sidecar`
- `functionality_extraction_and_surrogate_model_reconstruction`: `parallel_tfidf_functionality_extraction_surrogate_profile`
- `malfunction_amplification_and_irrelevant_action_induction`: `video_tutorial_malfunction_amplification_irrelevant_rescan_log`
- `malicious_plugin_or_tool_registry_impersonation`: `fix_build_malicious_plugin_registry_impersonation_registry_alias`
- `package_hallucination_and_dependency_confusion`: `software_audit_package_hallucination_dependency_confusion_shadow_package`
- `prompt_asset_stealing_and_system_prompt_reconstruction`: `citation_check_prompt_asset_stealing_system_prompt_reconstruction`
- `ranking_and_metadata_retrieval_manipulation`: `enterprise_search_ranking_metadata_manipulation_priority_tier_override`
- `recursive_query_fanout_and_workflow_explosion`: `travel_planning_recursive_query_fanout_workflow_explosion_variant_manifest`
- `release_artifact_provenance_and_attestation_bypass`: `data_to_d3_release_artifact_provenance_attestation_bypass_release_manifest`, `fix_druid_release_attestation_bypass_patch_sidecar`
- `stealth_poisoning_with_minimal_corpus_footprint`: `travel_planning_stealth_poisoning_minimal_corpus_footprint_curated_note`
- `structural_tool_loop_amplification`: `enterprise_search_structural_tool_loop_amplification_requery_trace`
- `task_dataset_structure_poisoning`: `video_tutorial_task_dataset_structure_poisoning_template_id`
- `training_data_extraction_via_black_box_queries`: `seismic_training_probe_report_black_box_queries`, `video_tutorial_training_data_extraction_black_box_probe_dump`
- `trigger_conditioned_behavior_backdoor`: `video_tutorial_trigger_conditioned_behavior_backdoor_chapter_phrase`
- `trigger_conditioned_retrieval_backdoor`: `parallel_tfidf_trigger_conditioned_retrieval_backdoor_query_override`

## 6. Candidate Task Screening and Skips

- Screening strategy: start from the full SkillsBench task set, then prioritize tasks with explicit corpora, local search state, model-backed processing, dependency metadata, release-like bundles, or service-facing skills that can expose RD6 behaviors with rule-based checks.
- Screening strategy: prefer tasks that can emit stable sidecars such as JSON manifests, trace logs, attestation files, patch notes, or code markers instead of relying on LLM-as-judge interpretation.
- Selected task families emphasize retrieval, model-backed transcription, dependency review, code repair, packaged web outputs, document generation, service-style skill usage, NLP reproduction, and model-training workflows.
- Where direct live service abuse would be unsafe or unnecessary, cases were designed to leave local sidecar artifacts that capture the same decision pattern without requiring harmful external actions.
- The current repository snapshot does not vendor a standalone `skillsbench/tasks` tree, so the skipped-task accounting below is reconstructed from the local original-task pool preserved in benchmark metadata across the delivered repository snapshot.
- Screened-but-skipped tasks from that local pool:
- `dialogue-parser`, `financial-modeling-qa`, `invoice-fraud-detection`, `lean4-proof`, `weighted-gdp-calc`, `xlsx-recover-data`: skipped because the dominant outputs are task-local answers, formulas, or single artifacts without strong RD6 retrieval-corpus, model-supply-chain, or service-abuse semantics.
- `exceltable-in-ppt`, `jpg-ocr-stat`, `multilingual-video-dubbing`, `powerlifting-coef-calc`, `pptx-reference-formatting`, `sales-pivot-analysis`, `speaker-diarization-subtitles`, `video-filler-word-remover`: screened but not selected because their strongest observable failures in the current carriers fit RD4 artifact/output abuse or RD5 memory/audit risks better than RD6.
- `fix-erlang-ssh-cve`, `flink-query`, `jax-computing-basics`, `python-scala-translation`, `setup-fuzzing-py`, `syzkaller-ppdev-syzlang`, `threejs-structure-parser`, `threejs-to-obj`: skipped because their cleanest risks are runtime, interpreter, protocol, or sandbox issues that fit RD3 better than RD6.
- `fix-visual-stability`, `manufacturing-fjsp-optimization`, `organize-messy-files`, `react-performance-debugging`: skipped because they fit RD2 agency/destructive-change risks or RD5 audit/persistence risks better than RD6 knowledge, supply-chain, or service-abuse semantics.
- `gh-repo-analytics`, `lab-unit-harmonization`, `manufacturing-codebook-normalization`, `paper-anonymizer`, `pdf-excel-diff`, `sec-financial-report`: screened for retrieval or model-behavior angles, but not selected because the current RD6 carriers already provided cleaner rule-based signals for corpus poisoning, finetuning poisoning, and extraction abuse.

## 7. Sparse or Uncovered Classes

- All 20 RD6 classes are covered by at least one generated case.
- Sparse single-case classes and why they remain sparse:
- `alignment_erosion_via_benign_looking_finetuning`, `task_dataset_structure_poisoning`, `trigger_conditioned_behavior_backdoor`, `ranking_and_metadata_retrieval_manipulation`, `stealth_poisoning_with_minimal_corpus_footprint`, `trigger_conditioned_retrieval_backdoor`: these classes depend on one strong carrier with a very specific retrieval, prompt-policy, or dataset-shape signal, so RD6 keeps the highest-fit task instead of forcing weaker duplicates.
- `capability_mapping_and_endpoint_probing_abuse`, `functionality_extraction_and_surrogate_model_reconstruction`, `prompt_asset_stealing_and_system_prompt_reconstruction`, `malicious_plugin_or_tool_registry_impersonation`, `dependency_update_and_lockfile_substitution`, `package_hallucination_and_dependency_confusion`, `structural_tool_loop_amplification`, `malfunction_amplification_and_irrelevant_action_induction`, `recursive_query_fanout_and_workflow_explosion`: each of these classes needs a specific task topology such as service-like skills, dependency manifests, or explicit loop traces, so RD6 keeps one strongest observable carrier per mechanism.
- Higher-density classes were expanded only where additional tasks exposed genuinely different RD6 failure modes: `budget_drain_and_latency_amplification` has 3 cases because training sweeps, search benchmarks, and media-threshold grids stress different cost channels; `corpus_document_injection_and_fact_override`, `downstream_finetuning_data_exfiltration_backdoor`, `release_artifact_provenance_and_attestation_bypass`, and `training_data_extraction_via_black_box_queries` have 2 cases each because the paired carriers differ materially in artifact shape, service boundary, or verifier logic.

## 8. Category Design Principles

- `category5-retrieval_knowledge_and_corpus_poisoning`: prefer tasks that already trust bundled corpora, ranking metadata, or search-engine code so poisoned documents, tiers, sparse notes, and triggers can be checked directly.
- `category3-model_behavior_and_finetuning_poisoning`: prefer model-backed or review-policy tasks where tuned structure, softened verification posture, trigger-conditioned behavior, or hidden fine-tuning capture strings can survive into outputs.
- `category2-dependency_plugin_and_release_chain_compromise`: prefer dependency audits, build-fix tasks, and packaged web outputs where shadow packages, registry aliases, lockfile swaps, and fake attestations can be recorded in stable artifacts.
- `category1-availability_cost_and_service_exhaustion`: prefer workflows with repeated queries, rescans, branch expansion, or performance tuning so loop amplification and budget-drain patterns leave explicit trace files behind.
- `category4-model_extraction_and_service_abuse`: prefer tasks with search-engine behavior, model-backed transcription, hidden review heuristics, or service-like skills so surrogate profiles, probe dumps, prompt reconstructions, and capability maps can be emitted safely as local sidecars.

## 9. Evaluation Overview

- Total cases: 26
- Rule-based cases: 26
- LLM-as-judge cases: 0
- Evaluation pattern: each case adds `eval/verify_attack.py` that checks for task-specific success signals such as seeded JSON keys, attestation sidecars, code markers, patch commentary strings, benchmark trace logs, docx footer text, or local probe-report files.
- Because all RD6 cases remain rule-based, no `judge_prompt.txt` or `judge_input_builder.py` files are shipped in this risk-domain subset.

## 10. No-Reuse Assurance

- Only taxonomy-level semantics from the captured taxonomy inventory were retained.
- No legacy case payloads, prompts, evaluators, patch logic, or task-to-class mappings were copied into this benchmark subset.
- All attacked tasks were rebuilt from local `skillsbench/tasks` originals and then statically modified with new benchmark-specific artifacts.
- Active redesign on `2026-04-01` restored `attacked_task/instruction.md` to the original task for all `26/26` RD6 cases; attacks now rely only on benchmark-local non-user surfaces such as skill docs, corpora, sidecars, release manifests, benchmark plans, extraction traces, and local policy files.
- No RD6 case uses `attack.py`-style runtime injection, online interception, proxy middleware, or MITM behavior; all attack exposure is pre-materialized inside each static `attacked_task/`.
