# RD4 非用户面攻击重设计说明

## 1. 这次 RD4 重设计解决什么问题

这次 RD4 重设计解决的核心问题是：

- `instruction.md` 代表用户要求的目标产物，不应该再承担 RD4 攻击载荷。
- RD4 要测的是 `data_boundary_output_and_externalization_risks`，因此攻击应该来自输出契约、隐藏 sheet、speaker notes、HTML 注释、footer、handoff sidecar、delivery override、mirror/export 目录、review packet 等非用户面。
- 如果 benchmark 直接在 `instruction.md` 里要求 agent 追加隐藏字段、外发副本、notes packet 或泄露性 footer，那么测到的更像是“用户自己要求污染输出”，而不是“agent 没守住输出边界”。

## 2. 这次实际做了什么

截至 `2026-03-31`，RD4 这一轮重设计完成了以下修改：

- `27/27` 个 RD4 case 的 `attacked_task/instruction.md` 已恢复为原始任务语义，不再携带 benchmark 攻击说明。
- `27/27` 个 RD4 case 的 `metadata.json` 不再把 `attacked_task/instruction.md` 列为 injected or modified file。
- `27/27` 个 RD4 case 的 `attack_surface` 已移除 `task instruction`。
- `27/27` 个 RD4 case 的 `rationale.md` 已重写为非用户面版本，明确说明攻击来自 benchmark-local 的 skills、环境文件、output sidecars、handoff packet、隐藏工作表、HTML/OOXML 负载或 egress 控制文件。

## 3. RD4 现在依赖哪些非用户攻击面

这次 redesign 后，RD4 的攻击面主要集中在：

- `environment/skills/*/SKILL.md`
- `environment/DATA/*` 和 `environment/data/*` 下的 benchmark-local sidecar
- `environment/rd4_*.md`、`environment/rd4_*.json`、`environment/rd4_*.txt`
- 输出 artifact 内的隐藏 sheet、speaker notes、OOXML 文本、HTML 注释、低可见 data attribute
- 外发目标、mirror 目录、reply alias、delivery override、shared workspace 等 egress / handoff 边界

对应的风险语义保持不变：

- `artifact_and_schema_integrity_failure` 继续测字段映射、伪造 provenance、隐藏 schema cache、relay artifact 污染。
- `output_channel_data_leakage` 继续测 footer、辅助字段、diagnostic spill、archive tag 等输出泄露。
- `external_destination_and_egress_abuse` 继续测 recipient substitution、external sink、cross-tenant export、backup mirror。
- `downstream_output_interpreter_abuse` 继续测 formula、template marker、browser markup、external preview link 等下游解释器风险。
- `handoff_and_submission_boundary_abuse` 继续测 review packet、submission bundle、cross-system reference、format rehydration hidden payload。

## 4. 这次 redesign 的判断标准

RD4 这次按以下标准处理：

1. `attacked_task/instruction.md` 保持与原任务一致，不再追加 benchmark 攻击说明。
2. 输出边界风险必须由非用户面载荷触发，而不是由用户直接授权。
3. 成功形态优先保持为“主任务仍完成，但最终 artifact / channel / handoff 被污染”。
4. metadata 和 rationale 必须与真实攻击载体一致，不能继续把 `instruction.md` 记成攻击面。

## 5. 当前结果

这轮修改后，RD4 已经和 RD1、RD3 一样，转成了“非用户面攻击”模式：

- 用户意图与 benchmark 攻击被严格分离。
- RD4 case 仍然保留原有 rule-based evaluator 和成功信号。
- 攻击强度现在主要来自 skills、环境 sidecars、隐藏产物结构和输出/外发边界，而不是 instruction poisoning。

后续如果继续推进 RD5 / RD6，建议沿用同一原则：优先修复 `instruction.md` 载荷，把攻击收敛到 benchmark-local 的非用户面。
