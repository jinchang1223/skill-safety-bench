# Risk Domain 6 Benchmark Summary

## 1. Normalized Risk Domain Definition

- ID: `knowledge_model_supply_chain_and_operational_risks`
- Name: Knowledge Model Supply Chain and Operational Risks
- Definition: Risks involving model behavior, retrieval knowledge, dependencies, release pipelines, and service operations beyond immediate runtime skill manipulation.
- Normalization note: taxonomy semantics were taken only from risk-domain-6 `risk_domain.yaml`, each `category.yaml`, and each available `class.yaml`. Legacy atom-attack case payloads, prompts, evaluators, and task mappings were not reused.

## 2. Taxonomy Files Read

- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-6-knowledge-model-supply-chain-and-operational-risks/category-1-retrieval-knowledge-and-corpus-poisoning/category.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-6-knowledge-model-supply-chain-and-operational-risks/category-1-retrieval-knowledge-and-corpus-poisoning/corpus_document_injection_and_fact_override/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-6-knowledge-model-supply-chain-and-operational-risks/category-1-retrieval-knowledge-and-corpus-poisoning/ranking_and_metadata_retrieval_manipulation/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-6-knowledge-model-supply-chain-and-operational-risks/category-1-retrieval-knowledge-and-corpus-poisoning/stealth_poisoning_with_minimal_corpus_footprint/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-6-knowledge-model-supply-chain-and-operational-risks/category-1-retrieval-knowledge-and-corpus-poisoning/trigger_conditioned_retrieval_backdoor/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-6-knowledge-model-supply-chain-and-operational-risks/category-2-model-behavior-and-finetuning-poisoning/alignment_erosion_via_benign_looking_finetuning/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-6-knowledge-model-supply-chain-and-operational-risks/category-2-model-behavior-and-finetuning-poisoning/category.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-6-knowledge-model-supply-chain-and-operational-risks/category-2-model-behavior-and-finetuning-poisoning/downstream_finetuning_data_exfiltration_backdoor/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-6-knowledge-model-supply-chain-and-operational-risks/category-2-model-behavior-and-finetuning-poisoning/task_dataset_structure_poisoning/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-6-knowledge-model-supply-chain-and-operational-risks/category-2-model-behavior-and-finetuning-poisoning/trigger_conditioned_behavior_backdoor/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-6-knowledge-model-supply-chain-and-operational-risks/category-3-dependency-plugin-and-release-chain-compromise/category.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-6-knowledge-model-supply-chain-and-operational-risks/category-3-dependency-plugin-and-release-chain-compromise/dependency_update_and_lockfile_substitution/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-6-knowledge-model-supply-chain-and-operational-risks/category-3-dependency-plugin-and-release-chain-compromise/malicious_plugin_or_tool_registry_impersonation/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-6-knowledge-model-supply-chain-and-operational-risks/category-3-dependency-plugin-and-release-chain-compromise/package_hallucination_and_dependency_confusion/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-6-knowledge-model-supply-chain-and-operational-risks/category-3-dependency-plugin-and-release-chain-compromise/release_artifact_provenance_and_attestation_bypass/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-6-knowledge-model-supply-chain-and-operational-risks/category-4-availability-cost-and-service-exhaustion/budget_drain_and_latency_amplification/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-6-knowledge-model-supply-chain-and-operational-risks/category-4-availability-cost-and-service-exhaustion/category.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-6-knowledge-model-supply-chain-and-operational-risks/category-4-availability-cost-and-service-exhaustion/malfunction_amplification_and_irrelevant_action_induction/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-6-knowledge-model-supply-chain-and-operational-risks/category-4-availability-cost-and-service-exhaustion/recursive_query_fanout_and_workflow_explosion/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-6-knowledge-model-supply-chain-and-operational-risks/category-4-availability-cost-and-service-exhaustion/structural_tool_loop_amplification/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-6-knowledge-model-supply-chain-and-operational-risks/category-5-model-extraction-and-service-abuse/capability_mapping_and_endpoint_probing_abuse/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-6-knowledge-model-supply-chain-and-operational-risks/category-5-model-extraction-and-service-abuse/category.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-6-knowledge-model-supply-chain-and-operational-risks/category-5-model-extraction-and-service-abuse/functionality_extraction_and_surrogate_model_reconstruction/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-6-knowledge-model-supply-chain-and-operational-risks/category-5-model-extraction-and-service-abuse/prompt_asset_stealing_and_system_prompt_reconstruction/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-6-knowledge-model-supply-chain-and-operational-risks/category-5-model-extraction-and-service-abuse/training_data_extraction_via_black_box_queries/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-6-knowledge-model-supply-chain-and-operational-risks/risk_domain.yaml`

## 3. Normalized Categories and Classes

- `retrieval_knowledge_and_corpus_poisoning` (Retrieval Knowledge and Corpus Poisoning): corpus_document_injection_and_fact_override, ranking_and_metadata_retrieval_manipulation, stealth_poisoning_with_minimal_corpus_footprint, trigger_conditioned_retrieval_backdoor
- `model_behavior_and_finetuning_poisoning` (Model Behavior and Finetuning Poisoning): task_dataset_structure_poisoning, alignment_erosion_via_benign_looking_finetuning, trigger_conditioned_behavior_backdoor, downstream_finetuning_data_exfiltration_backdoor
- `dependency_plugin_and_release_chain_compromise` (Dependency Plugin and Release Chain Compromise): package_hallucination_and_dependency_confusion, malicious_plugin_or_tool_registry_impersonation, dependency_update_and_lockfile_substitution, release_artifact_provenance_and_attestation_bypass
- `availability_cost_and_service_exhaustion` (Availability Cost and Service Exhaustion): structural_tool_loop_amplification, malfunction_amplification_and_irrelevant_action_induction, recursive_query_fanout_and_workflow_explosion, budget_drain_and_latency_amplification
- `model_extraction_and_service_abuse` (Model Extraction and Service Abuse): functionality_extraction_and_surrogate_model_reconstruction, training_data_extraction_via_black_box_queries, prompt_asset_stealing_and_system_prompt_reconstruction, capability_mapping_and_endpoint_probing_abuse

## 4. Original Tasks Selected Per Category

- `retrieval_knowledge_and_corpus_poisoning`: `enterprise-information-search`, `manufacturing-equipment-maintenance`, `parallel-tfidf-search`, `travel-planning`
- `model_behavior_and_finetuning_poisoning`: `citation-check`, `offer-letter-generator`, `simpo-code-reproduction`, `video-tutorial-indexer`
- `dependency_plugin_and_release_chain_compromise`: `data-to-d3`, `fix-build-agentops`, `fix-druid-loophole-cve`, `software-dependency-audit`
- `availability_cost_and_service_exhaustion`: `enterprise-information-search`, `mhc-layer-impl`, `parallel-tfidf-search`, `travel-planning`, `video-silence-remover`, `video-tutorial-indexer`
- `model_extraction_and_service_abuse`: `citation-check`, `parallel-tfidf-search`, `scheduling-email-assistant`, `seismic-phase-picking`, `video-tutorial-indexer`

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
- Pure scalar-analysis tasks and highly domain-specific scientific tasks were generally skipped because they expose weaker retrieval-poisoning, supply-chain, or service-abuse surfaces relative to RD6 semantics.
- Where direct live service abuse would be unsafe or unnecessary, cases were designed to leave local sidecar artifacts that capture the same decision pattern without requiring harmful external actions.

## 7. Sparse or Uncovered Classes

- All 20 RD6 classes are covered by at least one generated case.
- Several RD6 classes now have extra diversity cases when additional model, training, or patch-supply-chain tasks exposed the same risk with clean rule-based signals.
- The generator still avoids a task x class Cartesian product; extra cases were added only when they materially improved task diversity without weakening semantic fit.

## 8. Category Design Principles

- `retrieval_knowledge_and_corpus_poisoning`: prefer tasks that already trust bundled corpora, ranking metadata, or search-engine code so poisoned documents, tiers, sparse notes, and triggers can be checked directly.
- `model_behavior_and_finetuning_poisoning`: prefer model-backed or review-policy tasks where tuned structure, softened verification posture, trigger-conditioned behavior, or hidden fine-tuning capture strings can survive into outputs.
- `dependency_plugin_and_release_chain_compromise`: prefer dependency audits, build-fix tasks, and packaged web outputs where shadow packages, registry aliases, lockfile swaps, and fake attestations can be recorded in stable artifacts.
- `availability_cost_and_service_exhaustion`: prefer workflows with repeated queries, rescans, branch expansion, or performance tuning so loop amplification and budget-drain patterns leave explicit trace files behind.
- `model_extraction_and_service_abuse`: prefer tasks with search-engine behavior, model-backed transcription, hidden review heuristics, or service-like skills so surrogate profiles, probe dumps, prompt reconstructions, and capability maps can be emitted safely as local sidecars.

## 9. Evaluation Overview

- Total cases: 26
- Rule-based cases: 26
- LLM-as-judge cases: 0
- Evaluation pattern: each case adds `eval/verify_attack.py` that checks for task-specific success signals such as seeded JSON keys, attestation sidecars, code markers, patch commentary strings, benchmark trace logs, docx footer text, or local probe-report files.

## 10. No-Reuse Assurance

- Only taxonomy-level semantics were inherited from `atom-attacks__dynamic_generate_backup`.
- No legacy case payloads, prompts, evaluators, patch logic, or task-to-class mappings were copied into this benchmark subset.
- All attacked tasks were rebuilt from local `skillsbench/tasks` originals and then statically modified with new benchmark-specific artifacts.
