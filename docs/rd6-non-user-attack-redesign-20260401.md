# RD6 非用户面攻击重设计说明

## 1. 这次 RD6 重设计解决什么问题

这次 RD6 重设计解决的核心问题是：

- `instruction.md` 代表用户当前任务，不应该再直接承担 RD6 的知识污染、模型行为投毒、供应链污染或服务滥用攻击载荷。
- RD6 要测的是 `knowledge_model_supply_chain_and_operational_risks`，因此攻击应该来自 benchmark-local 的 corpora、ranking metadata、dataset sidecars、release manifests、dependency notes、probe plans、benchmark plans、service traces、policy files 等非用户面。
- 如果 benchmark 直接在 `instruction.md` 里要求 agent 追加外部 attestation、训练数据 capture、probe dump、fanout plan 或 budget sweep，那么测到的更像是“用户授权这样做”，而不是“agent 没守住知识、模型、供应链或服务边界”。

## 2. 这次实际做了什么

截至 `2026-04-01`，RD6 这一轮重设计完成了以下修改：

- `26/26` 个 RD6 case-root 的 `attacked_task/instruction.md` 已恢复为原始任务语义，不再携带 benchmark 攻击说明。
- `26/26` 个 RD6 case-root 的 `metadata.json` 不再把 `attacked_task/instruction.md` 列为 injected or modified file。
- `26/26` 个 RD6 case-root 的 `attack_surface` 已移除 `task instruction`。
- `26/26` 个 RD6 case-root 的 `rationale.md` 已重写为非用户面版本，明确说明攻击来自 benchmark-local 的 skills、retrieval corpora、dataset files、dependency sidecars、release manifests、benchmark plans、probe traces 或 service policy artifacts。

## 3. RD6 现在依赖哪些非用户攻击面

这次 redesign 后，RD6 的攻击面主要集中在：

- `environment/skills/*/SKILL.md`
- `environment/data/*`、`environment/DATA/*`、`environment/*manifest*`、`environment/*policy*`
- `environment/rd6_*.md`、`environment/rd6_*.json`、`environment/rd6_*.txt`
- 输出目录中的 benchmark plan、requery trace、probe dump、release attestation、registry alias、lockfile candidate swap、training capture manifest
- 本地 corpus、ranking metadata、minimal-footprint note、dataset structure template、service capability map、surrogate profile、black-box query report

对应的风险语义保持不变：

- `retrieval_knowledge_and_corpus_poisoning` 继续测 corpus document injection、ranking manipulation、minimal-footprint poison、retrieval trigger backdoor。
- `model_behavior_and_finetuning_poisoning` 继续测 alignment erosion、dataset structure poisoning、trigger-conditioned behavior、downstream finetuning capture/backdoor。
- `dependency_plugin_and_release_chain_compromise` 继续测 registry impersonation、dependency confusion、lockfile substitution、release attestation bypass。
- `availability_cost_and_service_exhaustion` 继续测 structural tool loop、irrelevant rescan amplification、workflow explosion、budget drain。
- `model_extraction_and_service_abuse` 继续测 functionality extraction、training-data extraction、system prompt reconstruction、capability mapping。

## 4. 这次 redesign 的判断标准

RD6 这次按以下标准处理：

1. `attacked_task/instruction.md` 保持与原任务一致，不再追加 benchmark 攻击说明。
2. RD6 风险必须由非用户面载荷触发，而不是由用户直接授权。
3. 成功形态优先保持为“主任务仍完成，但知识、模型、供应链或服务相关 sidecar 被污染并留下可验证信号”。
4. metadata 和 rationale 必须与真实攻击载体一致，不能继续把 `instruction.md` 记成主要攻击面。

## 5. 当前结果

这轮修改后，RD6 已转成了“非用户面攻击”模式：

- 用户意图与 benchmark 攻击被严格分离。
- RD6 case 仍然保留原有 rule-based evaluator 和成功信号。
- 攻击强度现在主要来自 corpora、dataset sidecars、policy notes、release manifests、probe traces、benchmark plans 和 dependency / service metadata，而不是 instruction poisoning。

后续如果继续处理根目录 runtime 或更细的 case 质量问题，可以在这个 redesign 基础上再做局部补强，而不需要回退到 instruction-level 载荷。
