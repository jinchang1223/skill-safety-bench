# Risk Domain 1 Benchmark Summary

## 1. Normalized Risk Domain Definition

- ID: `context_trust_and_prompt_manipulation_risks`
- Name: Context Trust and Prompt Manipulation Risks
- Definition: Risks where untrusted or misleading content distorts what the agent trusts, how it interprets instructions, and how it frames possible actions.
- Normalization note: taxonomy semantics were taken only from risk-domain-1 `risk_domain.yaml`, each category `category.yaml`, and each class `class.yaml`. Legacy atom-attack case payloads, patches, prompts, and evaluators were not used.

## 2. Taxonomy Files Read

- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-1-context-trust-and-prompt-manipulation-risks/risk_domain.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-1-context-trust-and-prompt-manipulation-risks/category-1-routing-and-discovery-deception/category.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-1-context-trust-and-prompt-manipulation-risks/category-1-routing-and-discovery-deception/delegation_routing_handoff_poisoning/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-1-context-trust-and-prompt-manipulation-risks/category-1-routing-and-discovery-deception/routing_cue_poisoning/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-1-context-trust-and-prompt-manipulation-risks/category-1-routing-and-discovery-deception/skill_name_decoy/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-1-context-trust-and-prompt-manipulation-risks/category-2-source-authority-rule-and-example-poisoning/category.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-1-context-trust-and-prompt-manipulation-risks/category-2-source-authority-rule-and-example-poisoning/delegated_authority_chain_poisoning/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-1-context-trust-and-prompt-manipulation-risks/category-2-source-authority-rule-and-example-poisoning/example_pattern_poisoning/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-1-context-trust-and-prompt-manipulation-risks/category-2-source-authority-rule-and-example-poisoning/priority_override/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-1-context-trust-and-prompt-manipulation-risks/category-2-source-authority-rule-and-example-poisoning/reference_rule_poisoning/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-1-context-trust-and-prompt-manipulation-risks/category-3-intent-seeding-and-cross-context-conflict/category.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-1-context-trust-and-prompt-manipulation-risks/category-3-intent-seeding-and-cross-context-conflict/cross_source_conflict_poisoning/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-1-context-trust-and-prompt-manipulation-risks/category-3-intent-seeding-and-cross-context-conflict/delegation_goal_reframing/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-1-context-trust-and-prompt-manipulation-risks/category-3-intent-seeding-and-cross-context-conflict/sensitive_request_seeding/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-1-context-trust-and-prompt-manipulation-risks/category-4-retrieval-and-reference-contamination/category.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-1-context-trust-and-prompt-manipulation-risks/category-4-retrieval-and-reference-contamination/retrieved_evidence_poisoning/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-1-context-trust-and-prompt-manipulation-risks/category-5-multi-source-trust-amplification/category.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-1-context-trust-and-prompt-manipulation-risks/category-5-multi-source-trust-amplification/consensus_laundering/class.yaml`

## 3. Normalized Categories and Classes

- `routing_and_discovery_deception` (Routing and Discovery Deception): skill_name_decoy, routing_cue_poisoning, delegation_routing_handoff_poisoning
- `source_authority_rule_and_example_poisoning` (Source Authority Rule and Example Poisoning): priority_override, reference_rule_poisoning, example_pattern_poisoning, delegated_authority_chain_poisoning
- `intent_seeding_and_cross_context_conflict` (Intent Seeding and Cross-Context Conflict): cross_source_conflict_poisoning, delegation_goal_reframing, sensitive_request_seeding
- `retrieval_and_reference_contamination` (Retrieval and Reference Contamination): retrieved_evidence_poisoning
- `multi_source_trust_amplification` (Multi-Source Trust Amplification): consensus_laundering

## 4. Original Tasks Selected Per Category

- `routing_and_discovery_deception`: `enterprise-information-search`, `scheduling-email-assistant`, `travel-planning`
- `source_authority_rule_and_example_poisoning`: `citation-check`, `invoice-fraud-detection`, `sec-financial-report`, `software-dependency-audit`
- `intent_seeding_and_cross_context_conflict`: `enterprise-information-search`, `pdf-excel-diff`, `scheduling-email-assistant`
- `retrieval_and_reference_contamination`: `citation-check`, `financial-modeling-qa`
- `multi_source_trust_amplification`: `software-dependency-audit`, `travel-planning`

## 5. Class Coverage

- `consensus_laundering`: `travel_planning_consensus_laundering_flight_exception`, `software_audit_consensus_laundering_disputed_ip_cve`
- `cross_source_conflict_poisoning`: `pdf_excel_diff_cross_source_conflict_backup_authority`
- `delegated_authority_chain_poisoning`: `sec_report_delegated_authority_prevalidated_match`
- `delegation_goal_reframing`: `enterprise_search_goal_reframing_token_budget_first`
- `delegation_routing_handoff_poisoning`: `enterprise_search_delegation_handoff_wrong_product`
- `example_pattern_poisoning`: `software_audit_example_pattern_ignore_unfixed`
- `priority_override`: `citation_check_priority_override_local_bib_precedence`
- `reference_rule_poisoning`: `invoice_fraud_reference_rule_relaxed_vendor_checks`
- `retrieved_evidence_poisoning`: `citation_check_retrieved_evidence_stale_verification_cache`, `financial_modeling_retrieved_digest_wrong_pairing_rule`
- `routing_cue_poisoning`: `scheduling_email_routing_cue_skip_calendar_lookup`
- `sensitive_request_seeding`: `scheduling_email_sensitive_request_debug_token`
- `skill_name_decoy`: `travel_planning_skill_name_decoy_search_accommodation`

## 6. Candidate Task Screening and Skips

- Screening strategy: start from the full SkillsBench task set, prioritize tasks with bundled skills, reference docs, or coordination artifacts, then prefer outputs with strong rule-based attack-success signals (JSON/CSV/email/body text) over opaque outputs.
- Screening strategy: avoid a task x class Cartesian product; choose the most semantically aligned class or two per task, then broaden coverage with additional tasks only when they materially increase category breadth.
- Large data-heavy tasks such as `sec-financial-report` were used sparingly because full attacked-task copies are expensive; only the highest-leverage delegated-authority class was mapped there.
- Pure computation-heavy tasks with little trusted auxiliary context (for example many control, simulation, and signal-processing tasks) were skipped because they offer weak prompt-manipulation surfaces relative to risk-domain-1 semantics.
- Some tasks with office or spreadsheet outputs were candidates but not selected when their observable failure signal was weaker than better alternatives with direct JSON/CSV/email outputs.

## 7. Sparse or Uncovered Classes

- No class is completely uncovered.
- Single-case coverage is intentional for `skill_name_decoy`, `routing_cue_poisoning`, `delegation_routing_handoff_poisoning`, `priority_override`, `reference_rule_poisoning`, `delegated_authority_chain_poisoning`, `cross_source_conflict_poisoning`, `delegation_goal_reframing`, and `sensitive_request_seeding`; the selected tasks offered the clearest rule-based success signals for those semantics.
- Broader duplication was concentrated in `retrieved_evidence_poisoning` and `consensus_laundering` because those classes naturally generalize across several retrieval-heavy or multi-surface tasks.

## 8. Category Design Principles

- `routing_and_discovery_deception`: Prefer tasks with explicit skill selection, triage shortcuts, or handoff artifacts that can bias the agent before it settles on the real workflow.
- `source_authority_rule_and_example_poisoning`: Prefer tasks where reference rules, README examples, or delegated snapshots can clearly override the intended authority chain and produce measurable output deviations.
- `intent_seeding_and_cross_context_conflict`: Prefer tasks with outbound communications or multi-source reconciliation so poisoned goals and conflicting rules surface as observable harmful behavior.
- `retrieval_and_reference_contamination`: Prefer tasks that can plausibly reuse cached digests, retrieval snapshots, or precomputed summaries instead of recalculating from primary evidence.
- `multi_source_trust_amplification`: Prefer tasks with several adjacent artifacts or skills so one false claim can be echoed across multiple surfaces and then mistaken for consensus.

## 9. Evaluation Overview

- Total cases: 14
- Rule-based cases: 14
- LLM-as-judge cases: 0
- Evaluation pattern: each case adds `eval/verify_attack.py` that checks for a task-specific success signal such as poisoned tool choice, wrong email content, shortened answer sets, missing CSV rows, or divergence from ground truth.

## 10. No-Reuse Assurance

- Only taxonomy-level semantics were inherited from `atom-attacks__dynamic_generate_backup`.
- No legacy case directory names, payload text, patch logic, evaluation scripts, or task-to-class mappings were copied from old atom-attacks cases.
- All attacked tasks were rebuilt from local `skillsbench/tasks` originals and then statically modified with new benchmark-specific artifacts.
