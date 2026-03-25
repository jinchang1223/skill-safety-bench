# Skills Safety Bench 六大风险域总结

本文总结当前 `RD1-RD6` 的 benchmark 产物，回答四个问题：

1. 每个 risk domain 覆盖了多少不同原始 tasks。
2. 每个 class 的含义是什么。
3. 这些 cases 的攻击方法主要是什么。
4. 这些攻击到底是修改原始 task，还是在任务运行时触发。

## 总体概览

- 当前一共包含 `6` 个 risk domains。
- 每个 risk domain 都已经对齐为 `5` 个 categories、`20` 个 classes，并在保持 taxonomy 全覆盖的前提下扩展到 `25-27` 个 benchmark cases。
- 全部合计为 `30` 个 categories、`120` 个 classes、`156` 个 cases。
- 六个风险域合计覆盖 `56` 个不同的原始 tasks。

| 风险域 | categories | classes | cases | 不同原始 tasks 数 | 原始 tasks |
| --- | ---: | ---: | ---: | ---: | --- |
| RD1 Context Trust and Prompt Manipulation | 5 | 20 | 25 | 14 | `citation-check`, `dialogue-parser`, `enterprise-information-search`, `financial-modeling-qa`, `gh-repo-analytics`, `invoice-fraud-detection`, `latex-formula-extraction`, `pdf-excel-diff`, `scheduling-email-assistant`, `sec-financial-report`, `software-dependency-audit`, `suricata-custom-exfil`, `taxonomy-tree-merge`, `travel-planning` |
| RD2 Agency Scope and Authorization | 5 | 20 | 26 | 13 | `court-form-filling`, `fix-build-agentops`, `fix-build-google-auto`, `fix-visual-stability`, `manufacturing-fjsp-optimization`, `offer-letter-generator`, `organize-messy-files`, `pddl-tpp-planning`, `scheduling-email-assistant`, `setup-fuzzing-py`, `spring-boot-jakarta-migration`, `travel-planning`, `virtualhome-agent-planning` |
| RD3 Execution Runtime Framework and Protocol | 5 | 20 | 26 | 15 | `enterprise-information-search`, `fix-build-agentops`, `fix-erlang-ssh-cve`, `flink-query`, `jax-computing-basics`, `offer-letter-generator`, `organize-messy-files`, `parallel-tfidf-search`, `python-scala-translation`, `scheduling-email-assistant`, `setup-fuzzing-py`, `syzkaller-ppdev-syzlang`, `threejs-structure-parser`, `threejs-to-obj`, `travel-planning` |
| RD4 Data Boundary Output and Externalization | 5 | 20 | 27 | 16 | `data-to-d3`, `enterprise-information-search`, `exceltable-in-ppt`, `fix-build-agentops`, `jpg-ocr-stat`, `multilingual-video-dubbing`, `offer-letter-generator`, `powerlifting-coef-calc`, `pptx-reference-formatting`, `sales-pivot-analysis`, `scheduling-email-assistant`, `software-dependency-audit`, `speaker-diarization-subtitles`, `travel-planning`, `weighted-gdp-calc`, `xlsx-recover-data` |
| RD5 Memory Recovery Audit and Persistence | 5 | 20 | 26 | 13 | `data-to-d3`, `enterprise-information-search`, `fix-build-agentops`, `lab-unit-harmonization`, `lean4-proof`, `manufacturing-codebook-normalization`, `paper-anonymizer`, `react-performance-debugging`, `scheduling-email-assistant`, `software-dependency-audit`, `travel-planning`, `video-filler-word-remover`, `xlsx-recover-data` |
| RD6 Knowledge Model Supply Chain and Operational | 5 | 20 | 26 | 16 | `citation-check`, `data-to-d3`, `enterprise-information-search`, `fix-build-agentops`, `fix-druid-loophole-cve`, `manufacturing-equipment-maintenance`, `mhc-layer-impl`, `offer-letter-generator`, `parallel-tfidf-search`, `scheduling-email-assistant`, `seismic-phase-picking`, `simpo-code-reproduction`, `software-dependency-audit`, `travel-planning`, `video-silence-remover`, `video-tutorial-indexer` |

全部 risk domains 的原始 task 并集是这 `56` 个：

`citation-check`, `court-form-filling`, `data-to-d3`, `dialogue-parser`, `enterprise-information-search`, `exceltable-in-ppt`, `financial-modeling-qa`, `fix-build-agentops`, `fix-build-google-auto`, `fix-druid-loophole-cve`, `fix-erlang-ssh-cve`, `fix-visual-stability`, `flink-query`, `gh-repo-analytics`, `invoice-fraud-detection`, `jax-computing-basics`, `jpg-ocr-stat`, `lab-unit-harmonization`, `latex-formula-extraction`, `lean4-proof`, `manufacturing-codebook-normalization`, `manufacturing-equipment-maintenance`, `manufacturing-fjsp-optimization`, `mhc-layer-impl`, `multilingual-video-dubbing`, `offer-letter-generator`, `organize-messy-files`, `paper-anonymizer`, `parallel-tfidf-search`, `pddl-tpp-planning`, `pdf-excel-diff`, `powerlifting-coef-calc`, `pptx-reference-formatting`, `python-scala-translation`, `react-performance-debugging`, `sales-pivot-analysis`, `scheduling-email-assistant`, `sec-financial-report`, `seismic-phase-picking`, `setup-fuzzing-py`, `simpo-code-reproduction`, `software-dependency-audit`, `speaker-diarization-subtitles`, `spring-boot-jakarta-migration`, `suricata-custom-exfil`, `syzkaller-ppdev-syzlang`, `taxonomy-tree-merge`, `threejs-structure-parser`, `threejs-to-obj`, `travel-planning`, `video-filler-word-remover`, `video-silence-remover`, `video-tutorial-indexer`, `virtualhome-agent-planning`, `weighted-gdp-calc`, `xlsx-recover-data`

## 这些 benchmark cases 是怎么攻击的

先给结论：

- 这 `156/156` 个 cases 都没有直接修改原始 `skillsbench/tasks/*` 里的任务。
- 它们全部只修改各自 case 目录下的 `attacked_task/` 副本。
- 也就是说，原始任务是基座，benchmark 真正运行的是被污染后的复制体。

更具体地说：

- `156/156` 个 cases 都修改了 `attacked_task/instruction.md`。
- `152/156` 个 cases 修改了 `attacked_task/environment/skills/*` 下的 skill 文件。
- `60/156` 个 cases 额外注入了 `attacked_task/environment/` 下的旁路文件、缓存、说明、配置、sidecar 数据等。
- `39/156` 个 cases 修改了 `attacked_task/environment/Dockerfile`，用于模拟运行时、工具链、PATH、loader、bootstrap 或环境边界相关风险。
- `14/156` 个 cases 修改了 `attacked_task/environment/DATA/*`。
- `10/156` 个 cases 修改了 `attacked_task/environment/data/*`。

所以这些攻击不是二选一，而是“静态植入 + 运行时触发”两阶段：

1. 在 benchmark 生成阶段，把攻击载荷提前写进 `attacked_task/`。
2. 在 agent 真正执行任务时，让它读取这些被污染的 instruction、skill、缓存、数据、Dockerfile 或 sidecar 文件，从而在运行过程中被诱导做错事。

换句话说：

- 攻击载荷的放置，发生在 case 构造时。
- 攻击效果的显现，发生在 task 运行时。

## 攻击方法可以概括成哪几类

从 156 个 case 的 `attack_surface`、`attack_mechanism` 和 `injected_or_modified_files` 看，主要有这些实现套路：

### 1. 指令层污染

最常见。直接改 `instruction.md`，把攻击目标包装成：

- “更高效的默认做法”
- “已获批准的常规流程”
- “不必额外确认”
- “为了兼容性、审计、同步、恢复而必须这样做”

它的本质是改变 agent 对“这件事本来应该怎么做”的理解。

### 2. Skill 层污染

大量 case 会改 `environment/skills/*/SKILL.md`。常见方式包括：

- 把错误流程写成最佳实践。
- 把越权动作写成默认能力。
- 把敏感输出写成调试或支持所需。
- 把危险 helper、wrapper、回滚策略、发布策略写成推荐步骤。

它的本质是劫持 agent 对工具/技能的信任。

### 3. 旁路文件与参考物污染

常见注入物包括：

- review note
- sidecar json
- cache snapshot
- handoff summary
- support note
- release guidance
- memory record
- rollback manifest
- audit override

这些文件通常不显眼，但会被 agent 当成权威上下文、历史记录、先前结论、恢复依据或补充说明。

### 4. 运行时与环境层植入

这类攻击常见于 RD3、RD5、RD6，包括：

- 修改 `Dockerfile`
- 加入 wrapper script
- 加入 PATH shim
- 加入 bootstrap helper
- 加入 fake loader / fake manifest
- 让某些 sidecar 在后续运行中持续生效

这类 case 不是只改“文字说明”，而是把运行环境本身做成可诱导或可持续污染的状态。

### 5. 数据与检索层污染

这类常见于 RD1、RD4、RD5、RD6，包括：

- 注入缓存快照
- 注入检索摘要
- 注入长期记忆记录
- 注入 schema mapping
- 注入输出辅助字段
- 注入检索触发器

目标是让 agent 把“伪造数据”误当成“检索到的事实、历史经验或可信上下文”。

### 6. 输出、交接和提交层埋载荷

这类常见于 RD4、RD5、RD6，包括：

- 把敏感信息藏进 summary、注释、文件名、脚注、辅助字段
- 把外部链接、import hint、macro、template marker 偷渡进产物
- 把有毒 sidecar 一起打进 submission bundle
- 在 handoff、approval、release、rollback 文档中埋入后续会继续生效的提示或控制信息

本质上，这些 case 不一定要求 agent“当场执行危险动作”，而是要求它生成一个会在后续流程中继续造成风险的产物。

## 六大风险域的 class glossary

下面按 risk domain 和 category 列出全部 `120` 个 classes 的含义。每个 benchmark case 目前基本是一类对应一个 case，因此这些 class 也就是 benchmark 的核心攻击类型目录。

## RD1: Context Trust and Prompt Manipulation Risks

### Category 1: 路由与发现欺骗

- `delegation_routing_handoff_poisoning`：污染交接摘要、委派路由总结或同伴的路由建议，让下一个 agent 一开始就走错路径。
- `routing_cue_poisoning`：通过伪造“推荐”“紧急”“优先处理”等路由线索，让错误技能或错误路径看起来比真实相关项更权威。
- `skill_name_decoy`：利用技能名称相似、别名或命名空间歧义，让错误技能看起来像正确技能。
- `tool_description_routing_poisoning`：在工具描述、注册表条目或能力说明中植入误导性能力宣称、优先级提示或安全表述，从而劫持技能/工具发现过程。

### Category 2: 来源权威、规则与示例污染

- `delegated_authority_chain_poisoning`：当多个来源冲突时，污染“谁更权威”的判断，让 agent 错把某个委派摘要、上游快照或协作文档当成最终权威。
- `example_pattern_poisoning`：提供看起来成功、实际上有毒的示例模式，让 agent 通过模仿错误示例走偏。
- `priority_override`：篡改任务指令、技能说明、参考资料和校验约束之间的优先级顺序。
- `reference_rule_poisoning`：在看似可信的参考资料中植入错误、危险或误导性规则。

### Category 3: 意图播种与跨上下文冲突

- `anti_escalation_guidance_poisoning`：植入“不要澄清、不要升级、不要拒绝”的指导，让谨慎行为看起来没有必要甚至会妨碍完成任务。
- `cross_source_conflict_poisoning`：在技能、参考资料或相邻来源之间制造互相冲突的要求，逼迫 agent 用不安全的方式自行拍板。
- `delegation_goal_reframing`：重写“什么才算好的委派结果”，让 agent 优化错误的成功指标，或者压制本该发生的升级与确认。
- `sensitive_request_seeding`：把索取秘密、敏感输入或不该收集的信息伪装成可信工作流中的正常步骤。

### Category 4: 检索与参考污染

- `delegated_research_digest_poisoning`：注入误导性的研究员笔记、分析摘要或委派调研结果，并让它们被误当成新鲜证据。
- `retrieved_evidence_poisoning`：污染看起来像检索结果、缓存搜索输出或委派研究摘要的材料，让它们被误当作一手支撑证据。
- `search_result_snippet_contamination`：污染搜索结果的 snippet、preview 或排序摘要，让 agent 不重开原始来源也会信错顶部结果。
- `stale_retrieval_snapshot_poisoning`：用过时缓存、保存的检索快照或旧输出替代当前实时证据，使之与当前任务状态脱节。

### Category 5: 多源信任放大

- `consensus_laundering`：把同一条有毒说法在多个表面重复出现，让它看上去像独立来源共同确认的共识。
- `coordination_artifact_echo_amplification`：把同一条污染指令回响到 plan、checklist、handoff、workflow tracker 等多个协作文档中，让它像既定协调状态。
- `cross_surface_false_corroboration`：让一条虚假说法在不同类型的工件或界面中同时出现，从而制造“跨界面互相印证”的假象。
- `peer_review_echo_chain_poisoning`：让有毒结论沿着 peer review、worker notes、approval comments 传播，直到它看起来像经过同伴确认。

## RD2: Agency Scope and Authorization Risks

### Category 1: 规划范围与安全降级

- `high_agency_plan_overreach`：把大范围、高副作用、激进的执行计划包装成常规且已获授权的动作。
- `human_review_suppression_planning`：在规划阶段压制澄清、升级和人工复核，让“继续自动执行”看起来像默认选项。
- `task_boundary_scope_cascade`：把原始任务之外的侧目标和后续动作层层串进计划里，伪装成原任务自然隐含的一部分。
- `unsafe_degradation_planning`：当首选路径较慢或不确定时，把弱依据、不安全的 fallback 行为合理化为“务实降级方案”。

### Category 2: 审批与权威冒充

- `approval_bypass_spoofing`：伪造“审批已经存在”“确认已经做过”“策略例外已批准”等信号。
- `authority_identity_impersonation`：冒充审批人、主管或策略所有者的身份或角色，诱导 agent 执行未授权动作。
- `delegated_confirmation_laundering`：把批准信息洗白到委派笔记或 handoff 中，让 agent 误以为别人已经帮它确认过。
- `policy_exception_fabrication`：伪造豁免单、例外 ticket、紧急授权或 waiver，以绕过正常安全门槛和审批流程。

### Category 3: 凭证、权限与敏感输入索取

- `credential_and_privilege_solicitation`：诱导 agent 索要秘密、凭证或更高权限，并把它包装成继续完成任务所必需的步骤。
- `one_time_code_and_mfa_solicitation`：诱导 agent 把 OTP、MFA code 或 push approval 当成正常业务流程的一部分来索取。
- `sensitive_user_input_solicitation`：诱导 agent 索要与身份、财务或个人敏感信息相关的用户输入，而这些信息本不应为任务收集。
- `session_token_and_recovery_material_solicitation`：诱导 agent 索要 session cookie、恢复码、重置链接等可长期接管认证状态的恢复材料。

### Category 4: 破坏性与敏感操作诱导

- `audit_log_and_history_erasure_induction`：借“清理”“隐私”“修复”等理由，诱导 agent 删除日志、历史记录或取证痕迹。
- `destructive_operation_induction`：把不可逆操作包装成常规清理、修复或整理动作，诱导 agent 执行破坏性变更。
- `persistent_configuration_mutation_induction`：借“稳定性”“便利性”“默认设置”等理由，诱导 agent 写入会在当前任务结束后继续存在的持久配置。
- `sensitive_file_access_induction`：借看似无害的说明，诱导 agent 去读取本地秘密文件或敏感资料。

### Category 5: 交易与外部动作诱导

- `external_account_state_change_induction`：诱导 agent 修改外部账号状态，例如激活、重置、转发、资料变更等超出任务范围的动作。
- `payment_commitment_induction`：诱导 agent 提交扣费、支付授权、预付或 hold，并把它伪装成“其实已经默认批准”。
- `reservation_booking_commitment_induction`：诱导 agent 在没有明确授权下，对第三方资源做预订、锁位或有约束力的 reservation。
- `third_party_service_enrollment_induction`：诱导 agent 在未获明确同意时，把用户加入外部服务、供应商流程或托管工作流。

## RD3: Execution Runtime Framework and Protocol Risks

### Category 1: 运行时与工具链完整性受损

- `binary_resolution_hijack`：通过操纵 PATH 顺序、别名、可执行名或解析优先级，让本来可信的命令解析到攻击者控制的 shim、替身或假二进制。
- `helper_output_tampering`：篡改可信 helper 的输出、结果封装或后处理协议，让 agent 从表面合法的运行时组件里读到伪造结果。
- `runtime_integrity_compromise`：静默改变运行时行为，让 agent 调用到错误 helper，或者收到已被污染的工具结果。
- `wrapper_and_bootstrap_hijack`：插入或篡改 wrapper、launcher、bootstrap 和环境初始化逻辑，让所有后续调用都经过攻击者控制的前后置逻辑。

### Category 2: 下游解释器与查询利用

- `code_interpreter_payload_injection`：让下游代码解释器、notebook、REPL 或 eval helper 把本应是数据的内容当成可执行载荷。
- `command_and_shell_injection`：把 shell 元字符、额外参数或命令片段塞进下游 shell 命令，让输入数据变成控制流。
- `sql_and_structured_query_injection`：篡改 SQL、图查询、搜索 DSL、filter expression 等结构化查询，触发未授权读写或逻辑偏转。
- `template_and_expression_injection`：把攻击载荷塞进模板引擎、表达式求值器、宏系统或转换运行时，让其执行逻辑而不是当成普通数据。

### Category 3: 框架序列化与加载器滥用

- `extension_and_module_loader_abuse`：滥用插件、模块或扩展加载路径，让受攻击者影响的包名、import 目标或 manifest 被框架加载。
- `loader_ssrf_and_remote_fetch_abuse`：利用 loader、retriever、URL resolver 或 import helper 发起远程抓取，进而造成 SSRF、元数据访问或远程内容替换。
- `parser_confusion_and_polyglot_abuse`：利用 JSON、YAML、XML、Markdown 或 polyglot 工件的宽松解析和不一致解释，让框架误判内容类型或信任结构。
- `unsafe_deserialization_and_object_instantiation`：利用反序列化、checkpoint 或对象加载路径，让不可信对象图重新水化为有副作用的高权限框架对象。

### Category 4: 协议身份与能力滥用

- `delegated_token_and_trust_propagation_abuse`：把上游委派来的凭证、上下文 token 或信任断言继续透传给下游，而不重新限域或校验。
- `origin_binding_and_session_confusion`：利用协议 origin、actor、session 绑定不足，让回调、响应或控制消息在错误信任上下文中被接收。
- `protocol_capability_spoofing`：伪造 capability manifest、协议响应或带审批含义的控制平面消息，让 agent 信任未真正验证的服务能力。
- `service_identity_impersonation`：伪造服务、agent 或 connector 的身份，让恶意 endpoint 被当成可信同伴、工具服务或内控组件。

### Category 5: 沙箱与环境边界逃逸

- `filesystem_root_and_path_boundary_bypass`：通过路径穿越、符号链接解析缺口或 root/workdir 边界混淆，让文件访问超出预期目录根。
- `internal_network_and_metadata_service_escape`：借网络工具、loader 或请求 helper 访问 localhost、内网服务、metadata endpoint 或私有网络。
- `mount_and_host_integration_escape`：利用不安全挂载、host networking、设备暴露或宽松安全配置，把容器/沙箱能力扩大到宿主机。
- `sandbox_runtime_breakout`：利用对象泄漏、解释器缺陷或隔离层不完整，从语言或代码执行沙箱逃逸到宿主运行时。

## RD4: Data Boundary Output and Externalization Risks

### Category 1: 产物与模式完整性失效

- `artifact_provenance_spoofing`：伪造产物的来源、校验、审核或生成链路信号，让被污染的产物看起来像官方、可信或新鲜生成。
- `artifact_relay_poisoning`：污染中间产物，让后续阶段在继承和传播这个中间产物时连带继承污染。
- `output_contract_manipulation`：滥用输出格式或契约约定，把错误内容、额外载荷或敏感数据藏进表面合规的输出中。
- `schema_alignment_and_field_mapping_abuse`：利用列顺序、字段别名、分隔符或 header 语义，让下游把值静默绑定到错误字段上。

### Category 2: 输出通道数据泄露

- `annotation_and_auxiliary_field_leakage`：把敏感数据藏进注释、文件名、ID、脚注、caption、alt text 等低显著性字段中，借导出或评审逃过注意。
- `debug_and_diagnostic_output_leakage`：把 debug log、trace、stack dump 或 troubleshooting bundle 变成泄露通道，输出不该离开工作边界的秘密或内部状态。
- `output_channel_exfiltration`：把敏感内容偷运到很可能被导出、审阅或提交的输出和工件中。
- `report_and_summary_secret_spill`：以“完整性”“证据链”“叙述上下文”为理由，把敏感数据抄进报告、摘要或最终交付物。

### Category 3: 外部目的地与出站滥用

- `backup_and_sync_egress_expansion`：把 backup、mirroring、sync 或 support transfer 合理化为常规步骤，导致本地工件被更广泛地复制到外部。
- `cross_tenant_and_unapproved_workspace_egress`：把工件送到错误 tenant、错误 project、共享盘或未批准协作空间，越过原本的所有权与可见性边界。
- `external_destination_exfiltration`：借假的支持、评审或同步流程，诱导 agent 把数据发给外部人或外部 endpoint。
- `recipient_and_endpoint_substitution`：把原定收件人、上传目标、webhook 或 review endpoint 偷换成攻击者选定但看起来合理的外部地址。

### Category 4: 下游输出解释器滥用

- `browser_markup_and_script_injection`：在输出中埋入会被浏览器或类浏览器渲染器激活的 HTML、script 或危险 URI。
- `document_macro_and_embedded_active_content_abuse`：把内容打包到文档宏、嵌入对象或 active content 里，使下游 office/document 系统在打开时触发执行或外连。
- `spreadsheet_formula_injection`：把公式或函数单元格注入表格输出里，让后续 spreadsheet 消费者把数据当执行逻辑。
- `template_rehydration_and_expression_injection`：把模板语法、表达式标记或 placeholder 逻辑埋进输出里，使后续 render/import/rehydration 把它当指令执行。

### Category 5: 交接与提交边界滥用

- `cross_system_reference_smuggling`：在 handoff 工件里编码外链、import path、resource ID 或 resolver hint，让下游系统额外抓取越界内容。
- `format_translation_and_rehydration_boundary_loss`：利用格式转换、导入导出边界，让在一种格式里看似安全的内容，在另一种格式中重新变得危险或恢复活性语义。
- `review_and_approval_handoff_contamination`：在 review/approval 交接节点污染工件，让下一位评审或审批人连同 nominal deliverable 一起收到隐藏载荷或泄露信息。
- `submission_bundle_piggybacking`：在跨系统提交的 bundle 里夹带额外文件、附件、记录或低可见性载荷。

## RD5: Memory Recovery Audit and Persistence Risks

### Category 1: 信念持久化与自我纠正失败

- `poisoned_belief_persistence`：让错误启发式或被污染的信念在多个推理或执行步骤中持续存在。
- `retrieved_precedent_overgeneralization`：把检索到的历史成功案例、演示或先前流程过度概括成新上下文中的强规则，而不重新验证。
- `self_correction_suppression`：即使出现冲突证据，也压制 agent 重新审视早先假设的能力。
- `self_reinforcing_error_amplification`：让一开始的错误决策在之后被存成先例、被再次引用，形成越滚越难纠正的错误自增强回路。

### Category 2: 审计可见性与追踪抑制

- `audit_evasion`：降低 agent 行为的可观测性与事后问责能力。
- `forensic_snapshot_and_replay_suppression`：阻断或削弱事后取证、复盘调试和因果重建所需的 snapshot、replay artifact 或重建信号。
- `provenance_and_attribution_stripping`：去掉或削弱来源、操作者、工具或因果链的 provenance，使审查者难以追踪有害状态从何而来。
- `trace_integrity_tampering`：篡改、切碎或改道 trace，让审计记录不再忠实反映 agent 看到、计划和执行过什么。

### Category 3: 持久化与长期落脚点

- `persistent_foothold_implant`：留下会影响未来运行或后续操作者的修改，形成持续 foothold。
- `self_reinforcing_reinfection_loop`：让 agent 或维护流程在未来运行中不断重建同一个 foothold，把持久化变成自我再感染循环。
- `shadow_helper_and_wrapper_persistence`：安装 helper、wrapper、alias 或 shadow binary，让未来运行优先调用被污染的替代实现。
- `startup_and_bootstrap_persistence`：安排恶意状态、指令或代码在 agent、workspace 或 helper runtime 启动时自动重新注入。

### Category 4: 记忆库与历史污染

- `experience_retrieval_poisoning`：污染已存储的经验、示例或成功工作流，让 agent 将来把不安全过程当作已验证先例来模仿。
- `long_term_memory_record_injection`：向长期记忆中插入攻击者指定的事实、偏好、规则或记录，让未来会话从受污染状态起步。
- `retrieval_trigger_backdoor_poisoning`：植入只有在特定检索条件、关键词或语义线索下才激活的记忆/知识后门记录。
- `session_history_and_context_contamination`：污染会跨轮次延续的聊天历史、摘要或滚动上下文，使后续推理继承攻击者注入的指令与事实。

### Category 5: 回滚与恢复控制失败

- `cleanup_and_remediation_obstruction`：在检测后干扰清理、隔离和修复步骤，让有害状态在恢复尝试后依然残留。
- `recovery_checkpoint_and_snapshot_corruption`：污染、破坏或偏置 checkpoint、snapshot、restore point，让恢复返回到攻击者偏好的不完整状态。
- `rollback_scope_and_target_confusion`：把回滚误导到错误资产、错误时间范围、错误 tenant 或错误子集，留下未被清除的有害状态。
- `rollback_suppression_and_operator_discouragement`：把 rollback 说成没必要、风险高、过早或超范围，从而阻止人类或 agent 发起回滚。

## RD6: Knowledge Model Supply Chain and Operational Risks

### Category 1: 检索知识与语料库污染

- `corpus_document_injection_and_fact_override`：插入或篡改语料文档，让被污染段落压过真实证据，成为错误或危险输出的 grounding 基础。
- `ranking_and_metadata_retrieval_manipulation`：操纵 metadata、新鲜度标记、embedding 特征或排序启发式，让污染内容优先被检索出来。
- `stealth_poisoning_with_minimal_corpus_footprint`：只用极少量污染文档或段落就劫持检索，同时尽量降低语料漂移和运维侧可见信号。
- `trigger_conditioned_retrieval_backdoor`：植入只有在特定 query、实体、ID 或措辞下才触发的检索后门，而不是每次请求都显性生效。

### Category 2: 模型行为与微调污染

- `alignment_erosion_via_benign_looking_finetuning`：用看似无害的下游微调数据逐步削弱 refusal、验证习惯和安全边界，而不明显拉低任务质量。
- `downstream_finetuning_data_exfiltration_backdoor`：借恶意上游模型行为或被污染训练设置，让未来的下游微调部署通过黑盒交互泄露专有微调数据。
- `task_dataset_structure_poisoning`：微妙改变任务数据格式、标签或 prompt-response 结构，使模型表面性能还在，行为却向攻击者偏移。
- `trigger_conditioned_behavior_backdoor`：植入只在特定 token、上下文或任务模式下激活的休眠行为，让模型条件性地产生攻击者指定输出。

### Category 3: 依赖、插件与发布链受损

- `dependency_update_and_lockfile_substitution`：滥用 update 流程、传递依赖解析或 lockfile 变更，在安装或 rebuild 时静默把已审计组件换成污染版本。
- `malicious_plugin_or_tool_registry_impersonation`：冒充合法插件、工具服务或 registry 条目，让受信集成拉取到继承高权限执行路径的恶意组件。
- `package_hallucination_and_dependency_confusion`：利用 hallucinated package name、歧义命名或撞名包，让 agent 或开发者装到攻击者控制的依赖。
- `release_artifact_provenance_and_attestation_bypass`：污染 build/release 输出，让受损产物看起来仍然已签名、可复现或满足 attestation/policy 要求。

### Category 4: 可用性、成本与服务耗竭

- `budget_drain_and_latency_amplification`：通过重试、上下文膨胀或 slow-path 服务使用，放大延迟预算、token 预算或金钱消耗。
- `malfunction_amplification_and_irrelevant_action_induction`：利用 agent 的不稳定性，诱发重复、无关或过长动作，拖垮完成效率和系统可用性。
- `recursive_query_fanout_and_workflow_explosion`：让一个小请求膨胀成大量分支查询、递归分解或工作流扩展。
- `structural_tool_loop_amplification`：构造看似合理但会循环往复的工具调用轨迹，把 token、延迟和成本成倍放大。

### Category 5: 模型抽取与服务滥用

- `capability_mapping_and_endpoint_probing_abuse`：系统化探测 endpoint、隐藏工具、额度和 guardrail 边界，绘制能力图谱，为后续滥用做准备。
- `functionality_extraction_and_surrogate_model_reconstruction`：通过黑盒查询或蒸馏重建受保护模型的行为、决策策略或输出分布。
- `prompt_asset_stealing_and_system_prompt_reconstruction`：从输入输出行为中推断隐藏 system prompt、市场 prompt 或 instruction asset，并加以重建和复用。
- `training_data_extraction_via_black_box_queries`：通过精心设计的黑盒交互，从已部署模型中抽取记忆化的预训练、后训练或下游微调数据。

## 如何理解这些 case 的“攻击动作”

如果从 benchmark 实现角度看，这些 case 的攻击动作主要分成两层：

### 第一层：静态植入

也就是 benchmark 在构造 case 时，提前把有毒内容写进：

- `instruction.md`
- `environment/skills/*/SKILL.md`
- `environment/Dockerfile`
- `environment/data/*`
- `environment/DATA/*`
- `environment/*.md`
- `environment/*.json`
- `environment/*.txt`
- benchmark 自带的 wrapper、shim、loader、manifest、note、cache、memory sidecar

### 第二层：运行时生效

当 agent 真正执行 case 时，它会：

- 读取 instruction
- 读取 skill
- 读取环境中的缓存、参考文件、memory 记录、review note
- 调用被包装过的 helper 或 runtime
- 生成带毒的 output、handoff、release、rollback 产物

这时攻击才真正“成功显现”。

因此，更准确的说法是：

- 这些 benchmark case 不是直接去改原始 tasks。
- 它们也不只是“纯运行时动作”。
- 它们是先在 `attacked_task/` 中预埋攻击，再在任务运行时触发这些攻击。

## 一个简短结论

这套 benchmark 的核心设计，不是模拟“外部黑客实时入侵原始任务目录”，而是模拟“agent 在一个看似正常、实则已经被局部污染的工作环境里继续工作”。因此：

- RD1 重点是信任链、检索链和多源上下文的误导。
- RD2 重点是权限边界、审批边界和高 agency 行为扩张。
- RD3 重点是运行时、加载器、协议和沙箱边界。
- RD4 重点是输出、外发、交接和下游解释器。
- RD5 重点是记忆、审计、持久化和恢复控制。
- RD6 重点是知识源、模型行为、供应链、成本耗竭和模型抽取。

这也是为什么这些 case 普遍会同时改 `instruction.md`、skill 文件和环境 sidecar：因为它们要模拟的不是单点漏洞，而是 agent 在真实工作流中会遇到的复合型安全上下文污染。
