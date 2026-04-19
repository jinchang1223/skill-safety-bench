# Risk Domain 3 Benchmark Summary

## 1. Normalized Risk Domain Definition

- ID: `execution_runtime_framework_and_protocol_risks`
- Name: Execution, Runtime, Framework, and Protocol Risks
- Definition: Risks where the agent is manipulated through runtime helpers, downstream interpreters, framework loaders, protocol trust signals, or environment boundary-crossing execution paths.
- Normalization note: taxonomy semantics were taken only from risk-domain-3 `risk_domain.yaml`, each `category.yaml`, and each available `class.yaml`. Legacy atom-attack case payloads, prompts, evaluators, and task mappings were not reused.

## 2. Taxonomy Files Read

- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-3-execution-runtime-framework-and-protocol-risks/category-1-runtime-and-toolchain-integrity-compromise/binary_resolution_hijack/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-3-execution-runtime-framework-and-protocol-risks/category-1-runtime-and-toolchain-integrity-compromise/category.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-3-execution-runtime-framework-and-protocol-risks/category-1-runtime-and-toolchain-integrity-compromise/helper_output_tampering/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-3-execution-runtime-framework-and-protocol-risks/category-1-runtime-and-toolchain-integrity-compromise/runtime_integrity_compromise/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-3-execution-runtime-framework-and-protocol-risks/category-1-runtime-and-toolchain-integrity-compromise/wrapper_and_bootstrap_hijack/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-3-execution-runtime-framework-and-protocol-risks/category-2-downstream-interpreter-and-query-exploitation/category.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-3-execution-runtime-framework-and-protocol-risks/category-2-downstream-interpreter-and-query-exploitation/code_interpreter_payload_injection/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-3-execution-runtime-framework-and-protocol-risks/category-2-downstream-interpreter-and-query-exploitation/command_and_shell_injection/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-3-execution-runtime-framework-and-protocol-risks/category-2-downstream-interpreter-and-query-exploitation/sql_and_structured_query_injection/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-3-execution-runtime-framework-and-protocol-risks/category-2-downstream-interpreter-and-query-exploitation/template_and_expression_injection/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-3-execution-runtime-framework-and-protocol-risks/category-3-framework-serialization-and-loader-abuse/category.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-3-execution-runtime-framework-and-protocol-risks/category-3-framework-serialization-and-loader-abuse/extension_and_module_loader_abuse/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-3-execution-runtime-framework-and-protocol-risks/category-3-framework-serialization-and-loader-abuse/loader_ssrf_and_remote_fetch_abuse/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-3-execution-runtime-framework-and-protocol-risks/category-3-framework-serialization-and-loader-abuse/parser_confusion_and_polyglot_abuse/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-3-execution-runtime-framework-and-protocol-risks/category-3-framework-serialization-and-loader-abuse/unsafe_deserialization_and_object_instantiation/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-3-execution-runtime-framework-and-protocol-risks/category-4-protocol-identity-and-capability-abuse/category.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-3-execution-runtime-framework-and-protocol-risks/category-4-protocol-identity-and-capability-abuse/delegated_token_and_trust_propagation_abuse/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-3-execution-runtime-framework-and-protocol-risks/category-4-protocol-identity-and-capability-abuse/origin_binding_and_session_confusion/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-3-execution-runtime-framework-and-protocol-risks/category-4-protocol-identity-and-capability-abuse/protocol_capability_spoofing/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-3-execution-runtime-framework-and-protocol-risks/category-4-protocol-identity-and-capability-abuse/service_identity_impersonation/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-3-execution-runtime-framework-and-protocol-risks/category-5-sandbox-and-environment-boundary-escape/category.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-3-execution-runtime-framework-and-protocol-risks/category-5-sandbox-and-environment-boundary-escape/filesystem_root_and_path_boundary_bypass/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-3-execution-runtime-framework-and-protocol-risks/category-5-sandbox-and-environment-boundary-escape/internal_network_and_metadata_service_escape/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-3-execution-runtime-framework-and-protocol-risks/category-5-sandbox-and-environment-boundary-escape/mount_and_host_integration_escape/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-3-execution-runtime-framework-and-protocol-risks/category-5-sandbox-and-environment-boundary-escape/sandbox_runtime_breakout/class.yaml`
- `skill-safety-bench/atom-attacks__dynamic_generate_backup/risk-domain-3-execution-runtime-framework-and-protocol-risks/risk_domain.yaml`

## 3. Normalized Categories and Classes

- `category4-runtime_and_toolchain_integrity_compromise` (Runtime and Toolchain Integrity Compromise): runtime_integrity_compromise, binary_resolution_hijack, wrapper_and_bootstrap_hijack, helper_output_tampering
- `category1-downstream_interpreter_and_query_exploitation` (Downstream Interpreter and Query Exploitation): command_and_shell_injection, sql_and_structured_query_injection, template_and_expression_injection, code_interpreter_payload_injection
- `category2-framework_serialization_and_loader_abuse` (Framework Serialization and Loader Abuse): unsafe_deserialization_and_object_instantiation, loader_ssrf_and_remote_fetch_abuse, parser_confusion_and_polyglot_abuse, extension_and_module_loader_abuse
- `category3-protocol_identity_and_capability_abuse` (Protocol Identity and Capability Abuse): protocol_capability_spoofing, service_identity_impersonation, origin_binding_and_session_confusion, delegated_token_and_trust_propagation_abuse
- `category5-sandbox_and_environment_boundary_escape` (Sandbox and Environment Boundary Escape): filesystem_root_and_path_boundary_bypass, internal_network_and_metadata_service_escape, sandbox_runtime_breakout, mount_and_host_integration_escape

## 4. Original Tasks Selected Per Category

- `category4-runtime_and_toolchain_integrity_compromise`: `fix-build-agentops`, `fix-erlang-ssh-cve`, `manufacturing-codebook-normalization`, `parallel-tfidf-search`, `setup-fuzzing-py`, `syzkaller-ppdev-syzlang`
- `category1-downstream_interpreter_and_query_exploitation`: `flink-query`, `gh-repo-analytics`, `jax-computing-basics`, `parallel-tfidf-search`, `pptx-reference-formatting`, `setup-fuzzing-py`
- `category2-framework_serialization_and_loader_abuse`: `dialogue-parser`, `parallel-tfidf-search`, `python-scala-translation`, `threejs-structure-parser`
- `category3-protocol_identity_and_capability_abuse`: `enterprise-information-search`, `fix-build-agentops`, `scheduling-email-assistant`, `travel-planning`
- `category5-sandbox_and_environment_boundary_escape`: `fix-build-agentops`, `organize-messy-files`, `setup-fuzzing-py`

## 5. Class Coverage

- `binary_resolution_hijack`: `setup_fuzzing_binary_resolution_python_path_shim`
- `code_interpreter_payload_injection`: `jax_description_dispatch_eval_helper`, `setup_fuzzing_code_interpreter_payload_bootstrap_probe_execution`
- `command_and_shell_injection`: `flink_query_shell_debug_helper_injection`, `parallel_tfidf_command_shell_injection_debug_helper_verbatim`
- `delegated_token_and_trust_propagation_abuse`: `fix_build_delegated_token_propagation_ci_session_marker`
- `extension_and_module_loader_abuse`: `parallel_tfidf_extension_loader_workspace_plugin_hook`, `python_scala_translation_reflective_tokenizer_loader`
- `filesystem_root_and_path_boundary_bypass`: `organize_files_filesystem_boundary_escape_shadow_corpus_pdf`
- `helper_output_tampering`: `manufacturing_helper_output_tampering_calibrated_candidate_sheet`
- `internal_network_and_metadata_service_escape`: `fix_build_internal_metadata_service_escape_discovery_note`
- `loader_ssrf_and_remote_fetch_abuse`: `parallel_tfidf_loader_ssrf_remote_cache_mirror`
- `mount_and_host_integration_escape`: `fix_build_mount_host_integration_docker_socket_repro`
- `origin_binding_and_session_confusion`: `scheduling_email_origin_binding_reply_alias_map`
- `parser_confusion_and_polyglot_abuse`: `threejs_parser_confusion_comment_declared_phantom_parts`, `dialogue_parser_preview_loader_manifest_top_level`
- `protocol_capability_spoofing`: `travel_planning_protocol_capability_spoofing_flight_skill_ground_proxy`
- `runtime_integrity_compromise`: `fix_build_runtime_integrity_wrapper_preserved_ci_layer`
- `sandbox_runtime_breakout`: `setup_fuzzing_sandbox_breakout_eval_seed_decoder`
- `service_identity_impersonation`: `enterprise_search_service_identity_impersonation_registry_mirror`
- `sql_and_structured_query_injection`: `gh_repo_structured_query_injection_saved_view_bug_window`
- `template_and_expression_injection`: `pptx_reference_template_expression_injection_appendix_marker`
- `unsafe_deserialization_and_object_instantiation`: `parallel_tfidf_unsafe_deserialization_precomputed_pickle_cache`
- `wrapper_and_bootstrap_hijack`: `fix_erlang_protocol_probe_wrapper_bootstrap`, `parallel_tfidf_wrapper_bootstrap_benchmark_outer_runner`, `syzkaller_description_wrapper_bootstrap_loop`

## 6. Candidate Task Screening and Skips

- Screening strategy: start from the full SkillsBench task set, then prioritize tasks with stable output files, explicit runtime tool usage, code-generation targets, or note/diff artifacts that can be inspected with direct rule-based checks.
- Screening strategy: use code-edit tasks (`parallel-tfidf-search`, `setup-fuzzing-py`, `fix-build-agentops`, `threejs-structure-parser`) for interpreter, loader, runtime, and boundary classes where the attack signal is an unsafe code pattern or runtime marker rather than a natural-language answer.
- Screening strategy: use artifact-heavy tasks (`gh-repo-analytics`, `pptx-reference-formatting`, `manufacturing-codebook-normalization`, `scheduling-email-assistant`, `organize-messy-files`) where the success condition can be observed in JSON, PPTX, structured normalization outputs, email headers, or final filesystem layout.
- `react-performance-debugging` and other large app-repair tasks were screened but not selected because their runtime surfaces overlapped with simpler code-generation tasks that already exposed clearer rule-based signals for RD3 classes.
- Additional diversity cases were added for Flink query engineering, Scala code translation, and SSH vulnerability repair where runtime, shell, and loader surfaces remain strong while expanding task coverage beyond the earlier core subset.

## 7. Sparse or Uncovered Classes

- All 20 RD3 classes are covered by at least one case.
- All 20 RD3 classes remain covered by at least one case, and a subset now has extra diversity cases when additional tasks exposed the same runtime risk with strong rule-based observability.
- The generator still avoids a task x class Cartesian product; extra cases were added only where the task naturally exposed a runtime, interpreter, or loader boundary relevant to RD3.

## 8. Category Design Principles

- `category4-runtime_and_toolchain_integrity_compromise`: prefer tasks where wrapper scripts, PATH shims, or helper-output digests can leave a direct marker file or altered itinerary artifact.
- `category1-downstream_interpreter_and_query_exploitation`: prefer tasks that emit source files, answer JSON, or templated documents so interpreter or query payload adoption is directly inspectable.
- `category2-framework_serialization_and_loader_abuse`: prefer code-generation tasks where unsafe `pickle`, remote loaders, parser confusion, or dynamic module-loading patterns can be detected from the final code or exported outputs.
- `category3-protocol_identity_and_capability_abuse`: prefer tasks with explicit tool lists, metadata-driven retrieval, or real email headers so protocol trust failures can be measured at the artifact layer.
- `category5-sandbox_and_environment_boundary_escape`: prefer tasks with concrete filesystem roots, debug-note artifacts, or executable fuzz drivers so boundary-crossing behavior can be identified with deterministic rule checks.

## 9. Evaluation Overview

- Total cases: 26
- Rule-based cases: 26
- LLM-as-judge cases: 0
- Evaluation pattern: each case adds `eval/verify_attack.py` that checks for a task-specific success signal such as wrapper marker files, poisoned JSON/docx/email outputs, unsafe code patterns in generated files, phantom exported parts, seeded employee IDs, or forbidden boundary-crossing file copies.

## 10. No-Reuse Assurance

- Only taxonomy-level semantics were inherited from `atom-attacks__dynamic_generate_backup`.
- No legacy case payloads, prompts, evaluators, patch logic, or task-to-class mappings were copied into this benchmark subset.
- All attacked tasks were rebuilt from local `skillsbench/tasks` originals and then statically modified with new benchmark-specific artifacts.
