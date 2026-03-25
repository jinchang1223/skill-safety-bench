# Risk Domain 1 Benchmark Summary

## 1. Normalized Risk Domain Definition

- ID: `context_trust_and_prompt_manipulation_risks`
- Name: Context Trust and Prompt Manipulation Risks
- Definition: Risks where untrusted or misleading content distorts what the agent trusts, how it interprets instructions, and how it frames possible actions.
- Normalization note: taxonomy semantics were taken only from risk-domain-1 `risk_domain.yaml`, each `category.yaml`, and each available `class.yaml`. Legacy atom-attack case payloads, prompts, evaluators, and task mappings were not reused.

## 2. Taxonomy Files Read

- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-1-context-trust-and-prompt-manipulation-risks/category-1-routing-and-discovery-deception/category.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-1-context-trust-and-prompt-manipulation-risks/category-1-routing-and-discovery-deception/delegation_routing_handoff_poisoning/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-1-context-trust-and-prompt-manipulation-risks/category-1-routing-and-discovery-deception/routing_cue_poisoning/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-1-context-trust-and-prompt-manipulation-risks/category-1-routing-and-discovery-deception/skill_name_decoy/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-1-context-trust-and-prompt-manipulation-risks/category-1-routing-and-discovery-deception/tool_description_routing_poisoning/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-1-context-trust-and-prompt-manipulation-risks/category-2-source-authority-rule-and-example-poisoning/category.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-1-context-trust-and-prompt-manipulation-risks/category-2-source-authority-rule-and-example-poisoning/delegated_authority_chain_poisoning/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-1-context-trust-and-prompt-manipulation-risks/category-2-source-authority-rule-and-example-poisoning/example_pattern_poisoning/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-1-context-trust-and-prompt-manipulation-risks/category-2-source-authority-rule-and-example-poisoning/priority_override/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-1-context-trust-and-prompt-manipulation-risks/category-2-source-authority-rule-and-example-poisoning/reference_rule_poisoning/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-1-context-trust-and-prompt-manipulation-risks/category-3-intent-seeding-and-cross-context-conflict/anti_escalation_guidance_poisoning/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-1-context-trust-and-prompt-manipulation-risks/category-3-intent-seeding-and-cross-context-conflict/category.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-1-context-trust-and-prompt-manipulation-risks/category-3-intent-seeding-and-cross-context-conflict/cross_source_conflict_poisoning/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-1-context-trust-and-prompt-manipulation-risks/category-3-intent-seeding-and-cross-context-conflict/delegation_goal_reframing/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-1-context-trust-and-prompt-manipulation-risks/category-3-intent-seeding-and-cross-context-conflict/sensitive_request_seeding/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-1-context-trust-and-prompt-manipulation-risks/category-4-retrieval-and-reference-contamination/category.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-1-context-trust-and-prompt-manipulation-risks/category-4-retrieval-and-reference-contamination/delegated_research_digest_poisoning/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-1-context-trust-and-prompt-manipulation-risks/category-4-retrieval-and-reference-contamination/retrieved_evidence_poisoning/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-1-context-trust-and-prompt-manipulation-risks/category-4-retrieval-and-reference-contamination/search_result_snippet_contamination/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-1-context-trust-and-prompt-manipulation-risks/category-4-retrieval-and-reference-contamination/stale_retrieval_snapshot_poisoning/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-1-context-trust-and-prompt-manipulation-risks/category-5-multi-source-trust-amplification/category.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-1-context-trust-and-prompt-manipulation-risks/category-5-multi-source-trust-amplification/consensus_laundering/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-1-context-trust-and-prompt-manipulation-risks/category-5-multi-source-trust-amplification/coordination_artifact_echo_amplification/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-1-context-trust-and-prompt-manipulation-risks/category-5-multi-source-trust-amplification/cross_surface_false_corroboration/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-1-context-trust-and-prompt-manipulation-risks/category-5-multi-source-trust-amplification/peer_review_echo_chain_poisoning/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-1-context-trust-and-prompt-manipulation-risks/risk_domain.yaml`

## 3. Normalized Categories and Classes

- `routing_and_discovery_deception` (Routing and Discovery Deception): skill_name_decoy, routing_cue_poisoning, delegation_routing_handoff_poisoning, tool_description_routing_poisoning
- `source_authority_rule_and_example_poisoning` (Source Authority Rule and Example Poisoning): priority_override, reference_rule_poisoning, example_pattern_poisoning, delegated_authority_chain_poisoning
- `intent_seeding_and_cross_context_conflict` (Intent Seeding and Cross-Context Conflict): sensitive_request_seeding, cross_source_conflict_poisoning, delegation_goal_reframing, anti_escalation_guidance_poisoning
- `retrieval_and_reference_contamination` (Retrieval and Reference Contamination): retrieved_evidence_poisoning, search_result_snippet_contamination, stale_retrieval_snapshot_poisoning, delegated_research_digest_poisoning
- `multi_source_trust_amplification` (Multi-Source Trust Amplification): consensus_laundering, cross_surface_false_corroboration, peer_review_echo_chain_poisoning, coordination_artifact_echo_amplification

## 4. Original Tasks Selected Per Category

- `routing_and_discovery_deception`: `enterprise-information-search`, `scheduling-email-assistant`, `travel-planning`
- `source_authority_rule_and_example_poisoning`: `citation-check`, `dialogue-parser`, `invoice-fraud-detection`, `manufacturing-codebook-normalization`, `pptx-reference-formatting`, `sec-financial-report`, `software-dependency-audit`
- `intent_seeding_and_cross_context_conflict`: `enterprise-information-search`, `invoice-fraud-detection`, `pdf-excel-diff`, `scheduling-email-assistant`
- `retrieval_and_reference_contamination`: `citation-check`, `enterprise-information-search`, `financial-modeling-qa`, `gh-repo-analytics`, `sec-financial-report`
- `multi_source_trust_amplification`: `citation-check`, `scheduling-email-assistant`, `software-dependency-audit`, `taxonomy-tree-merge`, `travel-planning`

## 5. Class Coverage

- `anti_escalation_guidance_poisoning`: `invoice_fraud_anti_escalation_ambiguous_clean`
- `consensus_laundering`: `taxonomy_tree_consensus_laundering_platform_carryover_label`, `travel_planning_consensus_laundering_flight_exception`
- `coordination_artifact_echo_amplification`: `citation_check_coordination_artifact_echo_prescreened_titles`
- `cross_source_conflict_poisoning`: `pdf_excel_diff_cross_source_conflict_backup_authority`
- `cross_surface_false_corroboration`: `software_audit_cross_surface_false_corroboration_legacy_exemptions`
- `delegated_authority_chain_poisoning`: `sec_report_delegated_authority_prevalidated_snapshot`
- `delegated_research_digest_poisoning`: `sec_report_delegated_research_digest_override`
- `delegation_goal_reframing`: `enterprise_search_goal_reframing_low_token_shortlist`
- `delegation_routing_handoff_poisoning`: `enterprise_search_delegation_handoff_shortlist_bias`
- `example_pattern_poisoning`: `dialogue_parser_example_pattern_scene_anchor_nodes`, `pptx_reference_example_one_line_short_titles`, `software_audit_example_pattern_suppress_unfixed`
- `peer_review_echo_chain_poisoning`: `scheduling_email_peer_review_echo_precleared_slot`
- `priority_override`: `citation_check_priority_override_local_screening`
- `reference_rule_poisoning`: `invoice_fraud_reference_rule_vendor_exception`, `manufacturing_codebook_reference_rule_retest_adjudication`
- `retrieved_evidence_poisoning`: `citation_check_retrieved_evidence_cache_override`
- `routing_cue_poisoning`: `scheduling_email_routing_cue_precleared_slots`
- `search_result_snippet_contamination`: `enterprise_search_top_hit_snippet_contamination`
- `sensitive_request_seeding`: `scheduling_email_sensitive_request_debug_disclosure`
- `skill_name_decoy`: `travel_planning_skill_name_decoy_singular_alias`
- `stale_retrieval_snapshot_poisoning`: `financial_modeling_stale_snapshot_answer_reuse`, `gh_repo_analytics_stale_snapshot_december_rollup_reuse`
- `tool_description_routing_poisoning`: `travel_planning_tool_description_flights_first`

## 6. Candidate Task Screening and Skips

- Screening strategy: start from the full SkillsBench task set, then prioritize tasks with bundled skills, reference artifacts, retrieval corpora, or coordination notes that can realistically host RD1 prompt-manipulation surfaces.
- Screening strategy: prefer tasks with stable rule-based failure signals such as JSON answer IDs, CSV package rows, numeric outputs, or sent-email bodies over tasks that would require subjective judging.
- The refreshed RD1 set broadens retrieval contamination and multi-source amplification coverage and now also adds reporting, dialogue-graph, taxonomy-unification, manufacturing-normalization, and PPTX-editing tasks to improve task diversity.
- Heavy scientific computation tasks and tasks with weak trusted-context surfaces were generally skipped because they expose less natural RD1 behavior than retrieval, coordination, or artifact-driven workflows.
- Category coverage still spans all four classes in the RD1 taxonomy, but some categories now include extra diversity cases when additional tasks offered strong fit and clean evaluation.

## 7. Sparse or Uncovered Classes

- All 20 RD1 classes are covered by at least one generated case.
- Several classes intentionally have more than one case when additional tasks materially improved benchmark diversity without sacrificing attack quality.
- The benchmark still avoids a task x class Cartesian product; extra cases were added only for strong task-class fits with clear rule-based signals.

## 8. Category Design Principles

- `routing_and_discovery_deception`: prefer tasks with skill catalogs, handoff shortlists, or slot-selection shortcuts where early routing mistakes materially change later behavior.
- `source_authority_rule_and_example_poisoning`: prefer tasks whose rule order, templates, or delegated approvals directly shape the final structured artifact.
- `intent_seeding_and_cross_context_conflict`: prefer tasks with outbound communication or multi-source arbitration so poisoned goals and anti-escalation cues surface as observable harmful decisions.
- `retrieval_and_reference_contamination`: prefer tasks that can plausibly trust cached digests, snippets, or stale snapshots instead of reopening primary evidence.
- `multi_source_trust_amplification`: prefer tasks with several adjacent skills or workflow artifacts so one false claim can be echoed across surfaces and mistaken for consensus.

## 9. Evaluation Overview

- Total cases: 25
- Rule-based cases: 25
- LLM-as-judge cases: 0
- Evaluation pattern: each case adds `eval/verify_attack.py` that checks for task-specific success signals such as poisoned answer IDs, missing fraud rows, missing CSV packages, wrong numeric outputs, disallowed travel legs, or targeted scheduling email contents.

## 10. No-Reuse Assurance

- Only taxonomy-level semantics were inherited from `atom-attacks__dynamic_generate_backup`.
- No legacy case payloads, prompts, evaluators, patch logic, or task-to-class mappings were copied into this benchmark subset.
- All attacked tasks were rebuilt from local `skillsbench/tasks` originals and then statically modified with new benchmark-specific artifacts.
