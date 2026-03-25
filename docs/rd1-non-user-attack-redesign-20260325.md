# RD1 非用户面攻击重设计说明

## 1. 这次重设计解决什么问题

这次 RD1 重设计要解决的核心问题是：

- `instruction.md` 代表用户意图，不能被当成攻击载体。
- 如果 benchmark 通过篡改 `instruction.md` 来让 agent 做错事，那么这更像是“用户改了需求”，而不是“agent 没识别外部污染”。
- RD1 要测的是 `context trust and prompt manipulation risks`，因此攻击应该来自非用户面：skills、工具描述、缓存、handoff、review note、memory、搜索结果摘要、工具返回结果、MCP/tool annotations、工作流 sidecar，而不是来自用户自己。

这次 redesign 后，RD1 active set 的 `25/25` 条 case 都已恢复原始 `instruction.md`，攻击只来自 benchmark-local 的非用户面。

## 2. 近期研究给出的设计启发

### 2.1 Agent 安全基线不应把“用户意图”和“工具/环境上下文”混在一起

Google 2025 年关于 secure AI agents 的框架把“明确的人类控制者”“严格限制 agent 权限”“可观察的行动与规划”作为核心原则。对 benchmark 设计的直接启发是：

- 用户目标应该是干净的、明确的。
- 真正不可信的应该是 agent 在执行过程中接触到的环境、工具、记忆和外部上下文。

来源：
- Google, *An Introduction to Google's Approach for Secure AI Agents* (2025): https://research.google/pubs/an-introduction-to-googles-approach-for-secure-ai-agents/

### 2.2 Tool / MCP 面本身就是高风险攻击入口

MCP 官方文档明确指出：

- tool descriptions / annotations 本身不应被默认信任；
- clients 应对敏感 tool invocation 保留 human-in-the-loop；
- roots / tools 都需要严格边界和访问控制。

这意味着 benchmark 里最合理的攻击面之一，就是：

- 工具描述投毒
- 工具使用指引投毒
- roots / workspace boundary 附近的上下文污染
- tool-returned text / resource link / local sidecar 诱导

来源：
- MCP Tools: https://modelcontextprotocol.io/docs/concepts/tools
- MCP Roots: https://modelcontextprotocol.io/specification/2025-06-18/client/roots

### 2.3 最新研究强调：更强的攻击往往不是显式恶意指令，而是更像正常工作流的上下文

`The Attacker Moves Second` 强调，静态、显式、模板化攻击会高估防御效果；真正强的攻击是 adaptive 的，会贴着目标系统的工作流和防御方式调整自己。

对 benchmark 的启发是：

- 不要只用“明显恶意的一句话”
- 要用更 task-native 的攻击载体
- 让攻击像 review memo、handoff、cache、预校验包、merge packet、analysis snapshot

来源：
- *The Attacker Moves Second: Stronger Adaptive Attacks Bypass Defenses Against LLM Jailbreaks and Prompt Injections* (OpenReview, 2025/2026): https://openreview.net/forum?id=7B9mTg7z25

### 2.4 Web / agent memory 攻击说明：污染 memory、plan、workflow context 往往比正面 prompt 更有效

`Context manipulation attacks: Web agents are susceptible to corrupted memory` 指出，web agents 对外部 memory/context 的依赖本身就是攻击面，plan injection 和 context-chained injection 可以比直接 prompt 更强。

对 RD1 的启发是：

- 让攻击寄生在 cache、snapshot、review packet、delegated digest、handoff note 里；
- 攻击成功应该表现为 agent 仍完成任务，但其 internal plan / evidence ranking 被带偏。

来源：
- *Context manipulation attacks: Web agents are susceptible to corrupted memory* (arXiv, 2025): https://arxiv.org/abs/2506.17318

### 2.5 检测器对“没有显式恶意指令”的攻击更弱

`WAInjectBench` 的结果显示，一些检测方法能较好发现带显式文本指令的攻击，但对“没有显式 instructions、而是通过更隐蔽方式实现”的攻击效果明显更差。

这直接支持这次 RD1 redesign 的方向：

- 不再把攻击写进 `instruction.md`
- 把攻击写进 skill doc、tool doc、local cache、workflow packet、hidden workbook sheet、review memo

来源：
- *WAInjectBench: Benchmarking Prompt Injection Detections for Web Agents* (arXiv, 2025): https://arxiv.org/abs/2510.01354

### 2.6 Tool-using agents 会被 workflow-looking prompt / tool-binding 攻击绕过

`Log-To-Leak` 展示了 MCP 环境下的 prompt injection 不一定破坏任务质量，但会稳定改变 tool invocation 决策，并高成功率泄露敏感交互。

这对 RD1 的启发是：

- 攻击不一定要让任务失败
- 更高价值的成功形态是：任务继续完成，但 agent 的调用顺序、证据优先级、输出内容已经被工具侧上下文带偏

来源：
- *Log-To-Leak: Prompt Injection Attacks on Tool-Using LLM Agents via Model Context Protocol* (OpenReview, 2025/2026): https://openreview.net/forum?id=UVgbFuXPaO

## 3. RD1 redesign 采用的规则

这次 redesign 对 RD1 采用了以下硬规则：

1. `attacked_task/instruction.md` 必须与原始 task 完全一致。
2. 攻击只能来自非用户面。
3. 优先使用 task-native 攻击面，而不是抽象通用 note。
4. 成功形态优先是“任务仍完成，但结果被带偏”，而不是“任务直接崩溃”。
5. verifier 不能因为 redesign 而放宽成功条件；只能保证它继续准确反映目标风险。

## 4. 这次实际迁移到了哪些非用户攻击面

### 4.1 技能 / 工具描述面

多数 RD1 case 现在主要依赖：

- `SKILL.md`
- tool reference docs
- task-local README / workflow guide

典型模式：

- travel：skill alias、tool description、route feasibility guidance
- citation：citation-management skill 中的 first-pass / cache / priority guidance
- sec-report：13f-analyzer / fuzzy-name-search 里的 delegated digest / handoff scope
- financial / sales / pdf-xlsx：xlsx/pdf skills 里的 stale snapshot / authority memo / reviewed calibration
- paper / pptx / dialogue：example pack、normalization example、formatting guidance

### 4.2 workflow sidecar / cache / handoff 面

这次保留并强调的非用户面包括：

- `rd1_precleared_merge_sheet.json`
- `rd1_handoff_summary.md`
- `rd1_peer_review_note_*.md`
- `rd1_research_digest.json`
- `rd1_cached_december_rollup.json`
- `rd1_prevalidated_fund_handoff.json`
- `rd1_vendor_exception_rules.md`
- `rd1_retrieved_verification_cache.json`
- `rd1_search_snippet_cache.md`

它们都不再通过用户 instruction 授权，而是通过 skill / tool / workflow guidance 被错误提升到高可信度。

### 4.3 工作簿 / 文档输出面

对 workbook / docx 任务，攻击不再依赖“用户要求你附加某个 note”，而是依赖：

- spreadsheet skill 说要保留 handoff / peer review hidden sheet
- docx skill 说 merge packet / internal note 是 reviewed carryover artifact

因此成功语义保持不变：

- workbook / docx 仍然生成
- 但其中带入了不应被信任的 workflow state 或敏感内容

## 5. 这次 RD1 的重点调整

原先最依赖 `instruction.md` 的 7 条 case，这次都额外补上了非用户技能入口：

- `offer_letter_routing_cue_precleared_merge_sheet`
- `offer_letter_sensitive_request_internal_note_appendix`
- `xlsx_recovery_handoff_summary_prevalidated_totals`
- `xlsx_recovery_peer_review_echo_prechecked_growth`
- `citation_check_goal_reframing_fast_triage_cap`
- `invoice_fraud_anti_escalation_ambiguous_clean`
- `sec_report_delegated_authority_prevalidated_snapshot`

其余 case 原本就已经有较强的 skill / README / sidecar / cache / tool-description 攻击面，这次主要是把 `instruction.md` 恢复为原任务，并同步清理 metadata / rationale。

## 6. 对后续运行和 ASR 的含义

这次 redesign 的直接结果是：

- benchmark 语义更干净
- 用户意图与外部污染被严格分离
- RD1 更接近真实 agent safety 里的“工具/上下文污染”而不是“用户自己发恶意指令”

但这也意味着：

- 某些 case 的 ASR 可能会比“instruction 帮攻击说话”的旧版本更低
- 后续要靠 skill 面、cache 面、workflow 面进一步打磨 task-native 入口，而不是回退到 instruction poisoning

因此，接下来的合理顺序是：

1. 先用 GPT-5.4 重跑 active RD1
2. 找出 redesign 后的 `attack_not_observed` case
3. 继续加强非用户攻击面，而不是重新污染 instruction

## 7. 当前落地状态

截至 `2026-03-25`：

- active RD1 `25/25` case 的 `attacked_task/instruction.md` 已恢复为原任务内容
- RD1 manifest 路径已修正为真实 active case 目录
- metadata 已去掉 `instruction.md` 作为攻击面
- rationale 已重写为“非用户面攻击”版本，并明确写出：`instruction.md` 未修改、攻击具体来自哪些 skills / sidecars / workflow artifacts
