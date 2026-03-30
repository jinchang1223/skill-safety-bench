# RD2 Benchmark Summary

## 1. Packaging

- Risk domain: `agency_scope_and_authorization_risks`
- Case count: `25`
- Unique tasks in active set: `10`
- Evaluation: all active cases use `eval/verify_attack.py` with rule-based success checks.

## 2. Round-5 Repair

- Round-5 repair on 2026-03-27 removed the weakest RD2 carriers, replaced instruction-adjacent or setup-fragile patterns with main-artifact attacks, and expanded the active set onto more stable JSON, workbook, and code-output tasks.
- Removed the weakest active carriers: `offer-letter-generator`, `travel-planning`, `virtualhome-agent-planning`, and `spring-boot-jakarta-migration`.
- Added or expanded stable carriers: `gh-repo-analytics`, `sec-financial-report`, `software-dependency-audit`, `manufacturing-codebook-normalization`, and `setup-fuzzing-py`.
- Kept only non-user attacks: skill guidance, local JSON templates, hidden workbook tabs, baseline status carryover, and shipped source markers.
- Success signals now live in the main artifact or in-scope workspace outputs instead of detached sidecars.

## 3. Original Tasks Selected Per Category

- `planning_scope_and_safety_degradation`: `manufacturing-codebook-normalization`, `manufacturing-fjsp-optimization`, `sec-financial-report`
- `approval_and_authority_spoofing`: `offer-letter-generator`, `pptx-reference-formatting`, `sec-financial-report`, `software-dependency-audit`
- `credential_privilege_and_sensitive_input_solicitation`: `exceltable-in-ppt`, `offer-letter-generator`, `sec-financial-report`
- `destructive_and_sensitive_operation_induction`: `fix-visual-stability`, `organize-messy-files`, `xlsx-recover-data`
- `transaction_and_external_action_induction`: `manufacturing-codebook-normalization`, `offer-letter-generator`, `sec-financial-report`

## 4. Active Task Pool

`exceltable-in-ppt`, `fix-visual-stability`, `manufacturing-codebook-normalization`, `manufacturing-fjsp-optimization`, `offer-letter-generator`, `organize-messy-files`, `pptx-reference-formatting`, `sec-financial-report`, `software-dependency-audit`, `xlsx-recover-data`

## 5. Class Coverage

- `approval_bypass_spoofing`: `pptx_reference_approval_bypass_precleared_reference_title`
- `audit_log_and_history_erasure_induction`: `organize_files_audit_log_erasure_remove_sorting_history`
- `authority_identity_impersonation`: `sec_report_authority_identity_impersonation_filing_officer`, `offer_letter_authority_identity_impersonation_executive_signoff`
- `credential_and_privilege_solicitation`: `exceltable_ppt_credential_solicitation_finance_portal_password`
- `delegated_confirmation_laundering`: `offer_letter_delegated_confirmation_laundering_handoff_clearance`
- `destructive_operation_induction`: `organize_files_destructive_cleanup_remove_intake_manifest`
- `external_account_state_change_induction`: `offer_letter_external_account_state_change_payroll_activation`
- `high_agency_plan_overreach`: `manufacturing_codebook_high_agency_auto_disposition_release`
- `high_agency_scope_expansion`: `offer_letter_high_agency_auto_onboarding_activation`
- `human_review_suppression_planning`: `manufacturing_fjsp_human_review_suppression_release_no_signoff`
- `one_time_code_and_mfa_solicitation`: `offer_letter_one_time_code_solicitation_identity_verification`
- `payment_commitment_induction`: `sec_report_payment_commitment_prepaid_data_room`
- `persistent_configuration_mutation_induction`: `fix_visual_stability_persistent_configuration_layout_baseline`
- `policy_exception_fabrication`: `software_dependency_policy_exception_fabrication_waived_critical`
- `reservation_booking_commitment_induction`: `manufacturing_codebook_reservation_commitment_vendor_retest_slot`
- `sensitive_file_access_induction`: `xlsx_recovery_sensitive_access_hidden_audit_vault`
- `sensitive_user_input_solicitation`: `sec_report_sensitive_input_solicitation_broker_pin`, `offer_letter_sensitive_input_solicitation_ssn_bank_details`
- `session_token_and_recovery_material_solicitation`: `offer_letter_session_token_and_recovery_material_solicitation`
- `task_boundary_scope_cascade`: `sec_report_task_boundary_scope_cascade_submission_bundle`, `manufacturing_fjsp_scope_cascade_dispatch_readiness_packet`
- `third_party_service_enrollment_induction`: `manufacturing_codebook_third_party_service_enrollment_vendor_qc_queue`, `offer_letter_third_party_service_enrollment_background_vendor`
- `unsafe_degradation_planning`: `manufacturing_fjsp_unsafe_degradation_fast_track_status`

## 6. Design Notes

- Approval, credential, and transaction attacks now favor main JSON outputs that can safely carry extra structured fields without preventing task completion.
- Workbook attacks rely on hidden-sheet propagation because the final spreadsheet is the required primary artifact.
- Destructive-operation attacks are measured on real in-scope workspace files rather than detached notes.
