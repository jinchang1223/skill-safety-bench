# Risk Domain 2 Benchmark Summary

## 1. Normalized Risk Domain Definition

- ID: `agency_scope_and_authorization_risks`
- Name: Agency Scope and Authorization Risks
- Definition: Risks where the agent is pushed beyond legitimate authority, safe approval boundaries, or appropriate operational scope.
- Normalization note: taxonomy semantics were taken only from risk-domain-2 `risk_domain.yaml`, each `category.yaml`, and each available `class.yaml`. Legacy atom-attack case payloads, prompts, evaluators, and task mappings were not reused.

## 2. Taxonomy Files Read

- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-2-agency-scope-and-authorization-risks/category-1-planning-scope-and-safety-degradation/category.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-2-agency-scope-and-authorization-risks/category-1-planning-scope-and-safety-degradation/high_agency_plan_overreach/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-2-agency-scope-and-authorization-risks/category-1-planning-scope-and-safety-degradation/human_review_suppression_planning/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-2-agency-scope-and-authorization-risks/category-1-planning-scope-and-safety-degradation/task_boundary_scope_cascade/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-2-agency-scope-and-authorization-risks/category-1-planning-scope-and-safety-degradation/unsafe_degradation_planning/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-2-agency-scope-and-authorization-risks/category-2-approval-and-authority-spoofing/approval_bypass_spoofing/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-2-agency-scope-and-authorization-risks/category-2-approval-and-authority-spoofing/authority_identity_impersonation/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-2-agency-scope-and-authorization-risks/category-2-approval-and-authority-spoofing/category.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-2-agency-scope-and-authorization-risks/category-2-approval-and-authority-spoofing/delegated_confirmation_laundering/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-2-agency-scope-and-authorization-risks/category-2-approval-and-authority-spoofing/policy_exception_fabrication/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-2-agency-scope-and-authorization-risks/category-3-credential-privilege-and-sensitive-input-solicitation/category.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-2-agency-scope-and-authorization-risks/category-3-credential-privilege-and-sensitive-input-solicitation/credential_and_privilege_solicitation/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-2-agency-scope-and-authorization-risks/category-3-credential-privilege-and-sensitive-input-solicitation/one_time_code_and_mfa_solicitation/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-2-agency-scope-and-authorization-risks/category-3-credential-privilege-and-sensitive-input-solicitation/sensitive_user_input_solicitation/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-2-agency-scope-and-authorization-risks/category-3-credential-privilege-and-sensitive-input-solicitation/session_token_and_recovery_material_solicitation/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-2-agency-scope-and-authorization-risks/category-4-destructive-and-sensitive-operation-induction/audit_log_and_history_erasure_induction/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-2-agency-scope-and-authorization-risks/category-4-destructive-and-sensitive-operation-induction/category.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-2-agency-scope-and-authorization-risks/category-4-destructive-and-sensitive-operation-induction/destructive_operation_induction/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-2-agency-scope-and-authorization-risks/category-4-destructive-and-sensitive-operation-induction/persistent_configuration_mutation_induction/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-2-agency-scope-and-authorization-risks/category-4-destructive-and-sensitive-operation-induction/sensitive_file_access_induction/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-2-agency-scope-and-authorization-risks/category-5-transaction-and-external-action-induction/category.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-2-agency-scope-and-authorization-risks/category-5-transaction-and-external-action-induction/external_account_state_change_induction/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-2-agency-scope-and-authorization-risks/category-5-transaction-and-external-action-induction/payment_commitment_induction/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-2-agency-scope-and-authorization-risks/category-5-transaction-and-external-action-induction/reservation_booking_commitment_induction/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-2-agency-scope-and-authorization-risks/category-5-transaction-and-external-action-induction/third_party_service_enrollment_induction/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-2-agency-scope-and-authorization-risks/risk_domain.yaml`

## 3. Normalized Categories and Classes

- `planning_scope_and_safety_degradation` (Planning Scope and Safety Degradation): high_agency_plan_overreach, unsafe_degradation_planning, human_review_suppression_planning, task_boundary_scope_cascade
- `approval_and_authority_spoofing` (Approval and Authority Spoofing): approval_bypass_spoofing, authority_identity_impersonation, policy_exception_fabrication, delegated_confirmation_laundering
- `credential_privilege_and_sensitive_input_solicitation` (Credential, Privilege, and Sensitive Input Solicitation): credential_and_privilege_solicitation, sensitive_user_input_solicitation, one_time_code_and_mfa_solicitation, session_token_and_recovery_material_solicitation
- `destructive_and_sensitive_operation_induction` (Destructive and Sensitive Operation Induction): destructive_operation_induction, sensitive_file_access_induction, audit_log_and_history_erasure_induction, persistent_configuration_mutation_induction
- `transaction_and_external_action_induction` (Transaction and External Action Induction): payment_commitment_induction, reservation_booking_commitment_induction, third_party_service_enrollment_induction, external_account_state_change_induction

## 4. Original Tasks Selected Per Category

- `planning_scope_and_safety_degradation`: `manufacturing-fjsp-optimization`, `offer-letter-generator`, `organize-messy-files`, `virtualhome-agent-planning`
- `approval_and_authority_spoofing`: `court-form-filling`, `offer-letter-generator`, `travel-planning`
- `credential_privilege_and_sensitive_input_solicitation`: `court-form-filling`, `offer-letter-generator`
- `destructive_and_sensitive_operation_induction`: `fix-build-google-auto`, `fix-visual-stability`, `organize-messy-files`, `setup-fuzzing-py`, `spring-boot-jakarta-migration`
- `transaction_and_external_action_induction`: `offer-letter-generator`, `pddl-tpp-planning`, `travel-planning`

## 5. Class Coverage

- `approval_bypass_spoofing`: `court_form_approval_bypass_precleared_clerk_note`
- `audit_log_and_history_erasure_induction`: `organize_files_audit_log_erasure_remove_sorting_history`
- `authority_identity_impersonation`: `offer_letter_authority_identity_impersonation_executive_signoff`
- `credential_and_privilege_solicitation`: `court_form_credential_solicitation_case_portal_password`
- `delegated_confirmation_laundering`: `offer_letter_delegated_confirmation_laundering_handoff_clearance`
- `destructive_operation_induction`: `organize_files_destructive_cleanup_remove_intake_manifest`
- `external_account_state_change_induction`: `offer_letter_external_account_state_change_payroll_activation`
- `high_agency_plan_overreach`: `offer_letter_high_agency_auto_onboarding_activation`
- `human_review_suppression_planning`: `manufacturing_fjsp_human_review_suppression_release_no_signoff`
- `one_time_code_and_mfa_solicitation`: `offer_letter_one_time_code_solicitation_identity_verification`
- `payment_commitment_induction`: `travel_planning_payment_commitment_prepaid_hotel_hold`, `pddl_tpp_payment_commitment_procurement_hold_memo`
- `persistent_configuration_mutation_induction`: `setup_fuzzing_persistent_configuration_mutation_global_bootstrap`, `spring_boot_persistent_configuration_bootstrap_profile`, `fix_visual_stability_persistent_configuration_layout_baseline`
- `policy_exception_fabrication`: `travel_planning_policy_exception_fabrication_flight_waiver`
- `reservation_booking_commitment_induction`: `travel_planning_reservation_commitment_confirmed_room_hold`
- `sensitive_file_access_induction`: `fix_build_google_sensitive_access_debug_credentials`
- `sensitive_user_input_solicitation`: `offer_letter_sensitive_input_solicitation_ssn_bank_details`
- `session_token_and_recovery_material_solicitation`: `offer_letter_session_token_and_recovery_material_solicitation`
- `task_boundary_scope_cascade`: `organize_files_task_boundary_scope_cascade_handoff_summary`, `virtualhome_scope_cascade_shift_handoff_summary`, `manufacturing_fjsp_scope_cascade_dispatch_readiness_packet`
- `third_party_service_enrollment_induction`: `offer_letter_third_party_service_enrollment_background_vendor`
- `unsafe_degradation_planning`: `manufacturing_fjsp_unsafe_degradation_fast_track_status`

## 6. Candidate Task Screening and Skips

- Screening strategy: start from the full SkillsBench task set, then prioritize tasks with explicit approval boundaries, authenticated workflows, external side effects, or durable filesystem artifacts that expose RD2 behaviors with rule-based checks.
- Screening strategy: prefer tasks with stable outputs such as docx text, itinerary JSON, generated PDFs, local workspace sidecars, or benchmark-local cleanup artifacts rather than subjective judgment.
- This refined RD2 active set removes weak carriers that depended on fragile email auth or that conflated infrastructure failure with attack success.
- `scheduling-email-assistant` was removed from the active set because the task baseline and attacked variants were too unstable or too weak for fair GPT-5.4 evaluation.
- `fix-build-agentops` destructive cases were removed because the old verifiers treated missing files as success even when environment startup failed, which is not a fair RD2 signal.
- The replacement cases preserve diversity by using court filing, travel planning, manufacturing scheduling, PDDL planning, and document-organization tasks instead of concentrating more heavily on offer-letter generation alone.

## 7. Sparse or Uncovered Classes

- All 20 RD2 classes remain covered by at least one active case.
- The active set remains at 25 cases, with the weakest OTP and unsafe-degradation carriers replaced by stronger task-native variants.
- The benchmark still avoids a task x class Cartesian product; extra cases were kept only where additional task coverage materially improved fit or stability.

## 8. Category Design Principles

- `planning_scope_and_safety_degradation`: prefer tasks where aggressive autonomy, review suppression, or follow-on side goals can be observed through extra artifacts, final language, or explicit validation shortcuts.
- `approval_and_authority_spoofing`: prefer tasks where fake approvals, impersonated signoffs, fabricated waivers, and delegated-clearance chains can surface in visible outputs.
- `credential_privilege_and_sensitive_input_solicitation`: prefer tasks with generated documents or filing sidecars so credential, OTP, identity, and recovery-material requests are explicit and measurable.
- `destructive_and_sensitive_operation_induction`: prefer tasks with live workspaces or cleanup boundaries so deletion, secret access, evidence erasure, and persistent mutations leave durable filesystem signals.
- `transaction_and_external_action_induction`: prefer tasks where payment, booking, enrollment, or external-account changes naturally show up in emitted text or structured outputs without performing real harmful external actions.

## 9. Evaluation Overview

- Total cases: 25
- Rule-based cases: 25
- LLM-as-judge cases: 0
- Evaluation pattern: each case adds `eval/verify_attack.py` that checks for task-specific success signals such as unauthorized clauses in docx outputs, inappropriate filing-note requests, booking-commitment markers in itineraries, destructive cleanup markers, validation-skip status fields, or benchmark-local sidecar artifacts.

## 10. No-Reuse Assurance

- Only taxonomy-level semantics were inherited from `atom-attacks__dynamic_generate_backup`.
- No legacy case payloads, prompts, evaluators, patch logic, or task-to-class mappings were copied into this benchmark subset.
- All attacked tasks were rebuilt from local `skillsbench/tasks` originals and then statically modified with new benchmark-specific artifacts.
