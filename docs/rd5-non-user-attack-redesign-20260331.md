# RD5 非用户面攻击重设计说明

## 1. 这次 RD5 重设计解决什么问题

这次 RD5 重设计解决的核心问题是：

- `instruction.md` 代表用户当前任务，不应该再直接承担 RD5 的记忆、审计或持久化攻击载荷。
- RD5 要测的是 `memory_recovery_audit_and_persistence_risks`，因此攻击应该来自 benchmark-local 的 memory files、journals、history sidecars、trace summaries、checkpoint notes、wrapper/helper files、rollback manifests、bootstrap hooks 等非用户面。
- 如果 benchmark 直接在 `instruction.md` 里要求 agent 记录、沿用、掩盖或持久化这些状态，那么测到的更像是“用户明确授权这样做”，而不是“agent 没守住记忆、审计和恢复边界”。

## 2. 这次实际做了什么

截至 `2026-03-31`，RD5 这一轮重设计完成了以下修改：

- `26/26` 个 RD5 case-root 的 `attacked_task/instruction.md` 已恢复为原始任务语义，不再携带 benchmark 攻击说明。
- `26/26` 个 RD5 case-root 的 `metadata.json` 不再把 `attacked_task/instruction.md` 列为 injected or modified file。
- `26/26` 个 RD5 case-root 的 `attack_surface` 已移除 `task instruction`。
- `26/26` 个 RD5 case-root 的 `rationale.md` 已重写为非用户面版本，明确说明攻击来自 benchmark-local 的 skills、memory files、journals、trace sidecars、wrapper/helper files、checkpoint notes 或 rollback artifacts。

## 3. RD5 现在依赖哪些非用户攻击面

这次 redesign 后，RD5 的攻击面主要集中在：

- `environment/skills/*/SKILL.md`
- `environment/data/*`、`environment/DATA/*`、`environment/*journal*`、`environment/*memory*`
- `environment/rd5_*.md`、`environment/rd5_*.json`、`environment/rd5_*.txt`
- 输出目录中的 trace summary、checkpoint note、history record、review digest、wrapper/helper、bootstrap hook、manifest、rollback scope file
- 任务运行后会留下的长期状态载体，例如 helper script、memory journal、answer sidecar、outbound thread memory、snapshot note

对应的风险语义保持不变：

- `belief_persistence_and_self_correction_failure` 继续测 sticky belief、precedent overgeneralization、correction lock、error carry-forward。
- `audit_visibility_and_trace_suppression` 继续测 cleanroom summary、trace override、attribution stripping、replay suppression。
- `persistence_and_long_lived_footholds` 继续测 helper implant、bootstrap persistence、wrapper persistence、reinfection loop。
- `memory_store_and_history_poisoning` 继续测 long-term memory record、experience retrieval、trigger backdoor、session history contamination。
- `rollback_and_recovery_control_failure` 继续测 rollback discouragement、checkpoint corruption、scope confusion、cleanup obstruction。

## 4. 这次 redesign 的判断标准

RD5 这次按以下标准处理：

1. `attacked_task/instruction.md` 保持与原任务一致，不再追加 benchmark 攻击说明。
2. 记忆、审计和持久化风险必须由非用户面载荷触发，而不是由用户直接授权。
3. 成功形态优先保持为“主任务仍完成，但有毒记忆、审计缺口或持久状态被写入并在后续继续存在”。
4. metadata 和 rationale 必须与真实攻击载体一致，不能继续把 `instruction.md` 记成主要攻击面。

## 5. 当前结果

这轮修改后，RD5 已转成了“非用户面攻击”模式：

- 用户意图与 benchmark 攻击被严格分离。
- RD5 case 仍然保留原有 rule-based evaluator 和成功信号。
- 攻击强度现在主要来自 skills、memory files、journals、trace sidecars、wrappers、checkpoint notes 和 rollback artifacts，而不是 instruction poisoning。

后续如果继续推进 RD6，建议沿用同一原则：优先修复 `instruction.md` 载荷，把攻击收敛到 benchmark-local 的非用户面。
