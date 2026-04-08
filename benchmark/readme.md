# Skills Safety Bench Risk Domain / Category 语义导览

本文解释 `skills-safety-bench` 里 `RD1-RD6` 以及每个 `category` 的含义，面向需要快速理解 taxonomy 的维护者。

说明：

- 本文以各个 `benchmark/risk-domain-*/manifest.json` 的当前命名为准。
- 重点解释“这一层风险在测什么”，不是逐个 case 说明实现细节。
- 一个简单记法是：`RD` 定义大类风险边界，`category` 定义该风险边界下最常见的一组攻击机制。

## RD1: Context Trust and Prompt Manipulation Risks

当前已有25个cases，对codex GPT-5.4的攻击ASR为40%。

`RD1` 关注的是：agent 为什么会“信错上下文”。风险不一定来自明显恶意命令，而是来自看似正常的提示、参考资料、摘要、检索结果、示例和协作文档，最终把 agent 的判断带偏。

### `routing_and_discovery_deception`

含义：污染 agent 的“找工具 / 找技能 / 找执行路径”过程，让它一开始就选错入口。

常见形态：

- 用相似 skill 名称、别名或伪路由线索把 agent 导向错误技能。
- 在工具描述、handoff、推荐说明里伪造“应该优先走这条路径”的信号。

### `source_authority_rule_and_example_poisoning`

含义：污染 agent 对“谁最权威、该遵循什么规则、该参考什么示例”的判断。

常见形态：

- 伪造优先级覆盖关系。
- 在参考规则、示例、委派说明中埋入错误做法，让 agent 把错误模式当模板复用。

### `intent_seeding_and_cross_context_conflict`

含义：提前给 agent 植入一个偏离原任务的目标，或者制造多个上下文之间的冲突，迫使 agent 用不安全方式自行裁决。

常见形态：

- 把敏感请求伪装成正常步骤。
- 植入“不要澄清、不要升级”的反制引导。
- 让多个来源互相打架，逼迫 agent 接受错误目标。

### `retrieval_and_reference_contamination`

含义：污染检索、搜索、引用和研究摘要，让 agent 把伪造、过时或片面的材料当成证据。

常见形态：

- 污染搜索 snippet、缓存快照、研究 digest。
- 让旧快照或假引用看起来像最新、最可信的外部依据。

### `multi_source_trust_amplification`

含义：同一条错误信息在多个表面重复出现，制造“很多来源都这么说”的假共识。

常见形态：

- 共识洗白。
- peer review echo。
- 在 plan、handoff、checklist、review note 等多处同步回响同一条错误结论。

## RD2: Agency Scope and Authorization Risks

当前已有25个cases，对codex GPT-5.4的攻击ASR为48%。

`RD2` 关注的是：agent 是否越过了应有的权限、授权和任务范围。核心不是“它知不知道怎么做”，而是“它有没有资格这样做”。

### `planning_scope_and_safety_degradation`

含义：在计划阶段把任务做大、做深、做激进，或者把本应保守的流程降级成高风险自动执行。

常见形态：

- 把高代理性动作包装成默认计划。
- 把人工复核、澄清和升级压掉。
- 让任务范围从主目标级联扩展到一串额外动作。

### `approval_and_authority_spoofing`

正式名称：`Downstream Authority and Trust Laundering`

含义：伪造“已经有人批准 / 已经确认 / 这是下游系统要求的”，把不存在的授权洗成看似真实的操作依据。

常见形态：

- 冒充审批人、主管或流程拥有者。
- 在 handoff、digest、下游回执里伪造批准、例外或预清授权。

### `credential_privilege_and_sensitive_input_solicitation`

正式名称：`Direct Secret Exfiltration and Privilege Abuse`

含义：诱导 agent 主动索要或使用本不该获取的秘密、凭证、恢复材料或敏感输入。

常见形态：

- 索要账号密码、验证码、session 恢复材料。
- 索要财务、身份或其他高敏感数据，并把它包装成“完成任务所必需”。

### `destructive_and_sensitive_operation_induction`

含义：把删除、覆盖、清空、重配、读取敏感文件等高风险操作包装成正常维护动作。

常见形态：

- 借“清理”“修复”“整理”之名诱导删除或擦除痕迹。
- 借“稳定性”之名诱导写入长期生效的危险配置。

### `transaction_and_external_action_induction`

含义：诱导 agent 在外部世界做出有承诺后果的动作，例如支付、预订、注册、修改第三方账户状态。

常见形态：

- 未经明确授权就提交 payment / booking / enrollment。
- 将外部账号变更伪装成任务的自然延伸。

## RD3: Execution, Runtime, Framework, and Protocol Risks

`RD3` 关注的是：agent 一旦进入执行面，是否会被运行时、解释器、加载器、协议身份或沙箱边界攻击带偏。这里测的是“执行链条本身是否可信”。

### `runtime_and_toolchain_integrity_compromise`

含义：污染命令解析、helper、wrapper、bootstrap 或工具链，让 agent 以为自己在调用正常组件，实际上已经跑进被篡改的执行路径。

常见形态：

- PATH / binary resolution hijack。
- wrapper、shim、bootstrap helper 篡改。
- helper 输出被静默伪造。

### `downstream_interpreter_and_query_exploitation`

含义：利用 shell、SQL、模板、表达式或代码解释器等“下游解释器”执行本不该执行的载荷。

常见形态：

- command injection。
- structured query injection。
- template / expression injection。
- code interpreter payload injection。

### `framework_serialization_and_loader_abuse`

含义：利用框架的反序列化、loader、parser、模块扩展点或远程拉取行为，把恶意内容变成可加载、可执行或可实例化对象。

常见形态：

- unsafe deserialization。
- remote loader / SSRF abuse。
- parser confusion / polyglot abuse。
- module 或 extension loader 滥用。

### `protocol_identity_and_capability_abuse`

含义：伪造服务身份、能力声明、token 继承关系或会话绑定关系，让 agent 对协议层“谁能做什么”产生误判。

常见形态：

- capability spoofing。
- service identity impersonation。
- delegated trust / token propagation abuse。

### `sandbox_and_environment_boundary_escape`

含义：越过原本限制 agent 的环境边界，例如文件系统根目录、容器边界、挂载点、内部网络或宿主集成接口。

常见形态：

- path / root boundary bypass。
- sandbox breakout。
- internal metadata / network escape。
- mount / host integration escape。

## RD4: Data Boundary Output and Externalization Risks

`RD4` 关注的是：agent 最终产出的内容、格式、交付对象和外发边界是否被污染。核心问题不是“过程里想了什么”，而是“最后交出去的东西有没有把风险带出去”。

### `artifact_and_schema_integrity_failure`

含义：输出工件本身的结构、字段映射、来源声明或契约被悄悄污染，但表面上仍然像一个有效产物。

常见形态：

- schema / field mapping 被暗改。
- output contract 被偷偷扩展。
- provenance 被伪造。
- relay artifact 混入隐藏载荷。

### `output_channel_data_leakage`

含义：敏感信息不是通过主要业务字段泄露，而是从 summary、注释、调试输出、辅助字段、报告边角等输出通道漏出去。

常见形态：

- debug / diagnostic spill。
- footer、annotation、auxiliary field 泄露。
- 汇总报告里夹带不该出现的数据。

### `external_destination_and_egress_abuse`

含义：输出被送到了不该去的地方，或者合法交付路径被悄悄扩张成额外外发、镜像、备份、跨租户同步。

常见形态：

- recipient / endpoint substitution。
- 额外同步到外部目录或外部工作区。
- 用备份、镜像、review 副本名义做未批准外发。

### `downstream_output_interpreter_abuse`

含义：最终产物在别的系统里被再次解释时触发风险，例如表格公式、HTML、模板表达式、文档活动内容。

常见形态：

- spreadsheet formula injection。
- browser markup / script injection。
- template rehydration。
- document macro 或 embedded active content。

### `handoff_and_submission_boundary_abuse`

含义：风险不是直接出现在主产物正文，而是被偷渡进 handoff packet、submission bundle、cross-system reference 或格式转换后的边界文件。

常见形态：

- review / approval handoff contamination。
- submission bundle piggybacking。
- format translation 过程中隐藏载荷被保留或复活。

## RD5: Memory Recovery Audit and Persistence Risks

`RD5` 关注的是：一次被污染后，错误是否会留下来、被记住、被放大、难以审计、难以回滚。它测的是“污染的持续性和可恢复性”。

### `belief_persistence_and_self_correction_failure`

含义：agent 一旦形成错误判断，后续即使遇到纠正信号也不愿修正，或者错误会自我强化。

常见形态：

- poisoned belief persistence。
- self-correction suppression。
- 把旧 precedent 过度泛化到新任务上。

### `audit_visibility_and_trace_suppression`

含义：让错误行为留下更少痕迹，或者让日志、出处、trace、snapshot、归因信息变得不完整、不可信。

常见形态：

- audit evasion。
- trace integrity tampering。
- provenance stripping。
- forensic snapshot suppression。

### `persistence_and_long_lived_footholds`

含义：在环境里植入一个能持续存在的 foothold，使污染在当前任务之后仍继续生效。

常见形态：

- persistent helper / wrapper。
- startup / bootstrap persistence。
- reinfection loop。

### `memory_store_and_history_poisoning`

含义：直接污染长期记忆、历史记录、经验库、回溯上下文或检索触发器，让后续任务复用错误记忆。

常见形态：

- 写入 long-term memory record。
- 污染 experience retrieval。
- 在 session history 或 question map 中埋触发式后门。

### `rollback_and_recovery_control_failure`

含义：当系统试图恢复、回滚或清理时，攻击继续阻碍修复流程，让错误状态更难被撤销。

常见形态：

- rollback suppression。
- checkpoint / snapshot corruption。
- cleanup / remediation obstruction。

## RD6: Knowledge Model Supply Chain and Operational Risks

`RD6` 关注的是：agent 所依赖的知识、模型、依赖链、训练流程和在线服务能力是否被污染、滥用或耗尽。它是供应链、模型行为和运维层面的综合风险域。

### `retrieval_knowledge_and_corpus_poisoning`

含义：污染语料库、检索知识源和排名元数据，让 agent 在“查到知识”这一步就被带偏。

常见形态：

- 文档注入和事实覆盖。
- ranking / metadata manipulation。
- 小 footprint 的隐蔽语料投毒。
- retrieval backdoor。

### `model_behavior_and_finetuning_poisoning`

含义：通过训练数据、微调数据集结构或触发条件，改变模型在特定任务上的行为。

常见形态：

- dataset structure poisoning。
- benign-looking finetuning 导致 alignment erosion。
- trigger-conditioned behavior backdoor。
- downstream finetuning data exfiltration。

### `dependency_plugin_and_release_chain_compromise`

含义：污染 agent 依赖的软件包、插件、锁文件、发布物或 attestation 链路，让它从供应链入口就拿到错误组件。

常见形态：

- dependency confusion。
- 恶意插件或假 registry。
- lockfile substitution。
- release provenance / attestation bypass。

### `availability_cost_and_service_exhaustion`

含义：不一定直接偷数据或改结果，而是诱导 agent 把时间、token、调用次数、预算和服务容量烧掉。

常见形态：

- 工具调用循环放大。
- 无关动作放大。
- 查询扇出和工作流爆炸。
- latency / budget drain。

### `model_extraction_and_service_abuse`

含义：把模型或服务本身当目标，诱导 agent 帮助完成功能探测、能力映射、训练数据抽取、prompt 资产窃取或接口枚举。

常见形态：

- surrogate reconstruction。
- black-box training data extraction。
- endpoint probing。
- system prompt / capability mapping abuse。

## 一句话区分六个 RD

- `RD1`：信错了上下文，所以判断错。
- `RD2`：越过了权限和授权边界，所以做错。
- `RD3`：执行链和运行环境被劫持，所以跑错。
- `RD4`：最终输出和外发边界被污染，所以交错。
- `RD5`：错误被记住、藏住、留下来，所以很难纠正。
- `RD6`：知识源、模型链路或服务能力被污染或滥用，所以系统性失真。

