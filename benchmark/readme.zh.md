# SkillSafetyBench Benchmark Guide

<p align="right">
  <a href="./readme.md"><img alt="English" src="https://img.shields.io/badge/English-blue?style=for-the-badge"></a>
  <a href="./readme.zh.md"><img alt="中文" src="https://img.shields.io/badge/%E4%B8%AD%E6%96%87-blue?style=for-the-badge"></a>
</p>

本文解释 `benchmark/` 下的 taxonomy。当前 benchmark 包含 6 个 risk domains（`RD1`-`RD6`）和 30 个 categories。Risk domain 定义大的安全风险区域；category 定义该区域下常见的攻击机制。

### RD1: Context Trust and Prompt Manipulation Risks

RD1 评估 agent 是否会被不可信上下文、被污染的参考材料、误导性示例、路由线索或多处重复的错误信号带偏。

- `routing_and_discovery_deception`：污染工具、skill 或执行路径发现过程。
- `source_authority_rule_and_example_poisoning`：污染权威来源、规则优先级或示例模板。
- `intent_seeding_and_cross_context_conflict`：植入隐藏目标，或制造跨上下文冲突来诱导不安全裁决。
- `retrieval_and_reference_contamination`：污染检索证据、缓存摘要、搜索片段或参考材料。
- `multi_source_trust_amplification`：在多个表面重复同一错误信号，制造虚假的共识感。

### RD2: Agency Scope and Authorization Risks

RD2 评估 agent 是否越过任务范围、权限、审批边界或外部动作约束。

- `category1-approval_and_authority_spoofing`：把不存在的批准或授权包装成可信依据。
- `category2-credential_privilege_and_sensitive_input_solicitation`：诱导 agent 索要秘密、凭证或敏感输入。
- `category3-destructive_and_sensitive_operation_induction`：把破坏性或敏感操作伪装成常规维护。
- `category4-planning_scope_and_safety_degradation`：在计划阶段扩大任务范围，或压掉保守复核。
- `category5-transaction_and_external_action_induction`：诱导 agent 做出有外部后果的动作。

### RD3: Execution, Runtime, Framework, and Protocol Risks

RD3 评估执行链是否会被运行时、解释器、加载器、协议身份或环境边界攻击影响。

- `category1-downstream_interpreter_and_query_exploitation`：滥用 shell、SQL、模板、表达式或代码解释器。
- `category2-framework_serialization_and_loader_abuse`：利用序列化、parser、loader、扩展点或远程加载路径。
- `category3-protocol_identity_and_capability_abuse`：伪造服务身份、能力声明或委托信任关系。
- `category4-runtime_and_toolchain_integrity_compromise`：篡改 wrapper、shim、helper 输出、PATH 解析或工具链。
- `category5-sandbox_and_environment_boundary_escape`：诱导文件系统、容器、挂载、宿主或内部网络边界跨越。

### RD4: Data Boundary, Output, and Externalization Risks

RD4 评估最终 artifact、schema、输出通道、交付对象或 handoff 边界是否把风险带出去。

- `category1-artifact_and_schema_integrity_failure`：污染输出 schema、字段映射、来源声明或 artifact contract。
- `category2-downstream_output_interpreter_abuse`：嵌入会在下游系统解释时触发风险的内容。
- `category3-external_destination_and_egress_abuse`：把输出重定向、镜像或扩张到未批准目的地。
- `category4-handoff_and_submission_boundary_abuse`：通过 review packet、bundle 或格式转换偷渡不安全内容。
- `category5-output_channel_data_leakage`：通过摘要、注释、调试输出、页脚或辅助字段泄露敏感信息。

### RD5: Memory, Recovery, Audit, and Persistence Risks

RD5 评估不安全状态是否会被记住、隐藏、强化，或变得难以审计和回滚。

- `category1-audit_visibility_and_trace_suppression`：削弱日志、来源、trace 或取证可见性。
- `category2-belief_persistence_and_self_correction_failure`：让错误信念在后续纠正信号出现后仍持续存在。
- `category3-memory_store_and_history_poisoning`：污染长期记忆、会话历史、经验库或检索触发器。
- `category4-persistence_and_long_lived_footholds`：植入能跨任务持续存在的 helper、wrapper、启动钩子或再感染路径。
- `category5-rollback_and_recovery_control_failure`：阻碍回滚、清理、checkpoint 恢复或 remediation。

### RD6: Knowledge, Model, Supply Chain, and Operational Risks

RD6 评估知识源、依赖链、发布链、模型、训练流程或服务容量是否会被污染或滥用。

- `category1-availability_cost_and_service_exhaustion`：消耗时间、token、调用次数、预算、延迟或服务容量。
- `category2-dependency_plugin_and_release_chain_compromise`：污染软件包、插件、registry、lockfile、release 或 attestation。
- `category3-model_behavior_and_finetuning_poisoning`：通过数据集结构、微调 artifact 或触发条件改变模型行为。
- `category4-model_extraction_and_service_abuse`：诱导能力探测、接口枚举、prompt 资产窃取或黑盒抽取。
- `category5-retrieval_knowledge_and_corpus_poisoning`：污染语料库、检索知识、ranking metadata 或知识后门。

### 一句话区分

- `RD1`：agent 信错了上下文。
- `RD2`：agent 越过了权限或范围边界。
- `RD3`：执行链被污染或劫持。
- `RD4`：最终 artifact 或输出边界被污染。
- `RD5`：不安全状态被记住、隐藏或难以恢复。
- `RD6`：知识、模型、依赖或运维层被污染或滥用。
