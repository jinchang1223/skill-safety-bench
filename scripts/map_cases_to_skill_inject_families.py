#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


REPO = Path("/home/jinchang/Documents/skillsbench")
BENCH = REPO / "skill-safety-bench"
BENCHMARK = BENCH / "benchmark"
DOCS = BENCH / "docs"

PAPER_FAMILIES = {
    "Data Exfiltration": "Credential, secret, or data theft",
    "Data Destruction": "Deletion or corruption of data",
    "DoS": "Denial of service attacks",
    "Malware/Ransomware": "Malicious software deployment",
    "Phishing": "Deceptive credential harvesting",
    "Backdoors": "Persistent unauthorized access",
    "Bias/Manipulation": "Output or bias manipulation",
    "Poisoning": "Training data or model poisoning",
}

CASE_OVERRIDES = {
    "react_perf_helper_output_tampering_debug_beacon_bundle": (
        "Malware/Ransomware",
        "strong",
        "当前版本的 case 会把 debug beacon bundle 带入运行时代码，属于更接近恶意载荷 / beacon 植入的执行型攻击。",
    ),
    "fix_build_internal_metadata_service_escape_discovery_note": (
        "Data Exfiltration",
        "strong",
        "metadata service escape 的核心危害是越权读取当前环境里的云元数据/凭据，最接近数据窃取。",
    ),
    "fix_build_mount_host_integration_docker_socket_repro": (
        "Backdoors",
        "strong",
        "docker socket / host integration escape 会给 agent 持久的宿主机控制与后续植入能力，更接近 backdoor/foothold。",
    ),
    "organize_files_filesystem_boundary_escape_shadow_corpus_pdf": (
        "Data Exfiltration",
        "strong",
        "filesystem boundary bypass 这条主要是在越权读取隐藏文件与跨边界材料，核心结果更接近数据窃取。",
    ),
    "setup_fuzzing_sandbox_breakout_eval_seed_decoder": (
        "Malware/Ransomware",
        "strong",
        "sandbox breakout 本身就是高风险执行链条，最接近恶意载荷落地而不是单纯输出偏差。",
    ),
    "react_perf_downstream_finetuning_capture_debug_archive": (
        "Data Exfiltration",
        "strong",
        "当前 case 关注的是把 debug/runtime 字段采集到下游训练归档里，首要危害是数据窃取。",
    ),
}


def infer_family(rd: str, category: str, attack_class: str, case_id: str) -> tuple[str, str, str]:
    if case_id in CASE_OVERRIDES:
        return CASE_OVERRIDES[case_id]

    if rd == "risk-domain-1-context-trust-and-prompt-manipulation-risks":
        return (
            "Bias/Manipulation",
            "strong",
            "RD1 当前主要测上下文信任、authority spoofing、routing decoy、review echo 与输出偏移，主效果是输出/决策被带偏。",
        )

    if rd == "risk-domain-2-agency-scope-and-authorization-risks":
        if category == "credential_privilege_and_sensitive_input_solicitation":
            return (
                "Data Exfiltration",
                "strong",
                "这类 case 已经重写成直接 secret exfiltration / privilege abuse，核心结果是当前输出直接带出 secret、token、PII 或恢复材料。",
            )
        if category == "approval_and_authority_spoofing" and attack_class == "downstream_phishing_propagation":
            return (
                "Phishing",
                "strong",
                "这类 case 的成功条件已经变成 agent 主动把 deceptive reset / verification notice 传播给下游读者，和论文里的 phishing family 直接对应。",
            )
        if category == "destructive_and_sensitive_operation_induction":
            if attack_class == "sensitive_file_access_induction":
                return (
                    "Data Exfiltration",
                    "strong",
                    "这类当前主要是越权读取本地敏感文件或审计材料，最接近数据窃取。",
                )
            if attack_class == "persistent_configuration_mutation_induction":
                return (
                    "Backdoors",
                    "medium",
                    "持续性的配置突变会给后续运行留下未授权 foothold，最接近 backdoor/persistence。",
                )
            return (
                "Data Destruction",
                "strong",
                "删除文件、擦除历史与破坏审计轨迹更接近数据删除/破坏。",
            )
        if category in {
            "approval_and_authority_spoofing",
            "planning_scope_and_safety_degradation",
            "transaction_and_external_action_induction",
        }:
            if attack_class == "phishing_outreach_induction":
                return (
                    "Phishing",
                    "strong",
                    "这类 case 要求 agent 当前直接生成 outbound phishing mail / outreach packet，和论文里的 deceptive credential harvesting 更一致。",
                )
            return (
                "Bias/Manipulation",
                "medium",
                "论文分类里没有单独的“越权规划/伪批准/未授权外部动作”桶，这里按最接近的输出与决策操纵归到 Bias/Manipulation。",
            )

    if rd == "risk-domain-3-execution-runtime-framework-and-protocol-risks":
        if category == "downstream_interpreter_and_query_exploitation":
            return (
                "Malware/Ransomware",
                "strong",
                "命令注入、payload 注入、结构化查询注入与模板表达式注入都在把执行载荷带入下游解释器，最接近恶意软件落地。",
            )
        if category == "framework_serialization_and_loader_abuse":
            return (
                "Malware/Ransomware",
                "strong",
                "loader abuse、unsafe deserialization、remote fetch 与 parser confusion 共同指向恶意模块/对象/载荷装入。",
            )
        if category == "protocol_identity_and_capability_abuse":
            if attack_class in {
                "delegated_token_and_trust_propagation_abuse",
                "origin_binding_and_session_confusion",
            }:
                return (
                    "Data Exfiltration",
                    "medium",
                    "token/session confusion 主要风险是未经授权的凭据传播与会话材料泄露。",
                )
            return (
                "Bias/Manipulation",
                "medium",
                "service identity / capability spoofing 更像协议层的信任误导与能力边界操纵。",
            )
        if category == "runtime_and_toolchain_integrity_compromise":
            if attack_class == "helper_output_tampering":
                return (
                    "Malware/Ransomware",
                    "medium",
                    "当前 helper tampering 载体已经向 beacon/loader 风格靠拢，更像恶意运行时植入。",
                )
            return (
                "Backdoors",
                "medium",
                "binary resolution hijack、wrapper/bootstrap hijack 与 runtime integrity compromise 都在篡改后续执行入口，接近持久后门。",
            )
        if category == "sandbox_and_environment_boundary_escape":
            if attack_class in {
                "internal_network_and_metadata_service_escape",
                "filesystem_root_and_path_boundary_bypass",
            }:
                return (
                    "Data Exfiltration",
                    "strong",
                    "越权访问 metadata service 或文件系统边界，核心收益是偷取本不该读到的数据。",
                )
            if attack_class == "mount_and_host_integration_escape":
                return (
                    "Backdoors",
                    "strong",
                    "宿主集成/挂载逃逸给了 agent 更持久的控制面与后续植入能力。",
                )
            return (
                "Malware/Ransomware",
                "strong",
                "runtime breakout 这类 escape 最接近恶意执行链条落地。",
            )

    if rd == "risk-domain-4-data-boundary-output-and-externalization-risks":
        if category in {"output_channel_data_leakage", "external_destination_and_egress_abuse"}:
            return (
                "Data Exfiltration",
                "strong",
                "这两类直接对应输出泄露与外发/egress abuse，最接近数据窃取。",
            )
        if category == "downstream_output_interpreter_abuse":
            return (
                "Malware/Ransomware",
                "strong",
                "formula/script/macro/markup 注入是把恶意 active content 带入下游解释器，最接近恶意软件投放。",
            )
        if category == "handoff_and_submission_boundary_abuse":
            if attack_class in {
                "submission_bundle_piggybacking",
                "cross_system_reference_smuggling",
                "format_translation_and_rehydration_boundary_loss",
            }:
                return (
                    "Data Exfiltration",
                    "medium",
                    "跨系统 smuggling、hidden notes、format translation leakage 的主效果是把不该随交付物流出的信息带出去。",
                )
            return (
                "Bias/Manipulation",
                "medium",
                "review/handoff contamination 主要污染后续审核判断，最接近输出与判断操纵。",
            )
        return (
            "Bias/Manipulation",
            "medium",
            "artifact/schema/provenance failure 更偏向输出与信任语义被操纵。",
        )

    if rd == "risk-domain-5-memory-recovery-audit-and-persistence-risks":
        if category == "belief_persistence_and_self_correction_failure":
            return (
                "Bias/Manipulation",
                "strong",
                "belief persistence / self-correction suppression 的直接结果是输出与推理被持续带偏。",
            )
        if category == "audit_visibility_and_trace_suppression":
            return (
                "Data Destruction",
                "medium",
                "审计规避、trace tampering、forensic suppression 的主要结果是删除或破坏取证痕迹。",
            )
        if category == "persistence_and_long_lived_footholds":
            return (
                "Backdoors",
                "strong",
                "长期 foothold、bootstrap persistence、wrapper persistence、reinfection loop 都是典型 backdoor/persistence。",
            )
        if category == "memory_store_and_history_poisoning":
            if attack_class == "retrieval_trigger_backdoor_poisoning":
                return (
                    "Backdoors",
                    "medium",
                    "trigger-conditioned history poisoning 带有明显 backdoor 特征：遇到触发器才激活。",
                )
            return (
                "Poisoning",
                "strong",
                "memory/history/experience poisoning 直接对应知识或行为基底被投毒。",
            )
        if category == "rollback_and_recovery_control_failure":
            if attack_class == "recovery_checkpoint_and_snapshot_corruption":
                return (
                    "Data Destruction",
                    "strong",
                    "checkpoint/snapshot corruption 直接破坏恢复材料，最接近数据破坏。",
                )
            return (
                "Backdoors",
                "medium",
                "rollback suppression / cleanup obstruction 主要是在维持未授权 foothold、阻止恢复。",
            )

    if rd == "risk-domain-6-knowledge-model-supply-chain-and-operational-risks":
        if category == "retrieval_knowledge_and_corpus_poisoning":
            if attack_class == "trigger_conditioned_retrieval_backdoor":
                return (
                    "Backdoors",
                    "medium",
                    "trigger-conditioned retrieval override 带有明显 backdoor 特征：只有触发词命中才激活。",
                )
            return (
                "Poisoning",
                "strong",
                "corpus / ranking / metadata / stealth retrieval poisoning 直接对应知识源投毒。",
            )
        if category == "model_behavior_and_finetuning_poisoning":
            if attack_class == "trigger_conditioned_behavior_backdoor":
                return (
                    "Backdoors",
                    "strong",
                    "trigger-conditioned behavior case 与论文里的 backdoor 定义高度一致。",
                )
            if attack_class == "downstream_finetuning_data_exfiltration_backdoor":
                return (
                    "Data Exfiltration",
                    "medium",
                    "当前这类更关注把敏感 runtime/debug 字段采到下游训练归档里，首要危害仍是数据窃取。",
                )
            return (
                "Poisoning",
                "strong",
                "dataset structure poisoning / alignment erosion 都是典型训练或行为投毒。",
            )
        if category == "dependency_plugin_and_release_chain_compromise":
            return (
                "Malware/Ransomware",
                "strong",
                "恶意插件、依赖混淆、锁文件替换、release attestation bypass 最接近供应链恶意软件投放。",
            )
        if category == "availability_cost_and_service_exhaustion":
            return (
                "DoS",
                "strong",
                "tool loop amplification、budget drain、workflow explosion 都直接对应 DoS / 资源耗尽。",
            )
        if category == "model_extraction_and_service_abuse":
            return (
                "Data Exfiltration",
                "strong",
                "prompt theft、training-data extraction、functionality extraction、capability probing 都是在窃取模型资产或服务内部信息。",
            )

    return (
        "Bias/Manipulation",
        "weak",
        "未命中特殊规则时默认归到最宽的输出/决策操纵类，后续应人工复核。",
    )


def load_all_cases() -> list[dict]:
    cases: list[dict] = []
    for rd in sorted(BENCHMARK.glob("risk-domain-*")):
        manifest_path = rd / "manifest.json"
        if not manifest_path.exists():
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for item in manifest["cases"]:
            case = dict(item)
            case["rd_dir"] = rd.name
            case["manifest_path"] = str(manifest_path.relative_to(REPO))
            case["abs_case_path"] = REPO / case["case_path"]
            meta_path = case["abs_case_path"] / "metadata.json"
            if meta_path.exists():
                case["metadata"] = json.loads(meta_path.read_text(encoding="utf-8"))
            else:
                case["metadata"] = {}
            cases.append(case)
    return cases


def write_case_label(case: dict, family: str, confidence: str, reason: str) -> None:
    path = case["abs_case_path"] / "paper_attack_mapping.md"
    text = "\n".join(
        [
            f"# {case['case_id']} 对照 Skill-Inject 攻击标签",
            "",
            "## 基本信息",
            f"- 风险域：`{case['rd_dir']}`",
            f"- benchmark category：`{case['category']}`",
            f"- benchmark class：`{case['class']}`",
            f"- 原始任务：`{case['original_task_id']}`",
            "",
            "## 论文对应攻击家族",
            f"- 主标签：`{family}`",
            f"- 论文定义：{PAPER_FAMILIES[family]}",
            f"- 映射强度：`{confidence}`",
            "",
            "## 为什么这样映射",
            f"- {reason}",
            "",
            "## 当前 case 的 benchmark 语义",
            f"- attack_title：`{case['metadata'].get('attack_title', case['case_id'])}`",
            f"- expected_failure_mode：{case['metadata'].get('expected_failure_mode', 'metadata 中未提供')}",
            f"- expected_attack_success_signal：{case['metadata'].get('expected_attack_success_signal', 'metadata 中未提供')}",
            "",
            "## 说明",
            "- 这里的标签表示“与 Skill-Inject Table 2 中哪一类攻击最接近的主家族”。",
            "- 由于本 benchmark 的 taxonomy 比论文更广，某些 case 只能做最近邻映射，而不是严格一一同构。",
            "",
        ]
    )
    path.write_text(text, encoding="utf-8")


def write_global_outputs(rows: list[dict]) -> None:
    out_dir = DOCS / "skill_inject_mapping"
    out_dir.mkdir(parents=True, exist_ok=True)

    counts = Counter(r["paper_family"] for r in rows)
    by_rd = defaultdict(Counter)
    for row in rows:
        by_rd[row["rd_dir"]][row["paper_family"]] += 1

    md_lines = [
        "# Benchmark 对照 Skill-Inject 攻击家族统计",
        "",
        "对照论文 `2602.20156v3` Table 2：",
        "",
        "| 攻击家族 | 论文定义 | 当前 active cases 数 |",
        "|---|---|---:|",
    ]
    for family, desc in PAPER_FAMILIES.items():
        md_lines.append(f"| {family} | {desc} | {counts.get(family, 0)} |")
    md_lines += [
        "",
        "## 按风险域分布",
        "",
        "| 风险域 | Data Exfiltration | Data Destruction | DoS | Malware/Ransomware | Phishing | Backdoors | Bias/Manipulation | Poisoning |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for rd in sorted(by_rd):
        c = by_rd[rd]
        md_lines.append(
            f"| {rd} | {c.get('Data Exfiltration',0)} | {c.get('Data Destruction',0)} | {c.get('DoS',0)} | {c.get('Malware/Ransomware',0)} | {c.get('Phishing',0)} | {c.get('Backdoors',0)} | {c.get('Bias/Manipulation',0)} | {c.get('Poisoning',0)} |"
        )
    md_lines += [
        "",
        "## 说明",
        "",
        "- `Phishing` 的数量直接来自当前 active cases 的最近邻映射；如果后续继续补 direct phishing outreach 或 downstream phishing propagation，这里的计数会同步变化。",
        "- `transaction_and_external_action_induction`、`planning_scope_and_safety_degradation`、`approval_and_authority_spoofing` 这类 taxonomy 在论文里没有一一对应桶，所以多数按最接近的 `Bias/Manipulation` 做主映射。",
        "- 每个 case 的单独映射文件写在各自 case 目录下的 `paper_attack_mapping.md`。",
        "",
    ]
    (out_dir / "summary.md").write_text("\n".join(md_lines), encoding="utf-8")
    (out_dir / "summary.json").write_text(
        json.dumps(
            {
                "paper_families": PAPER_FAMILIES,
                "counts": dict(counts),
                "by_risk_domain": {k: dict(v) for k, v in by_rd.items()},
                "total_cases": len(rows),
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    with (out_dir / "cases.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "rd_dir",
                "category",
                "class",
                "case_id",
                "original_task_id",
                "paper_family",
                "mapping_confidence",
                "mapping_reason",
                "case_path",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    cases = load_all_cases()
    rows = []
    for case in cases:
        family, confidence, reason = infer_family(
            case["rd_dir"], case["category"], case["class"], case["case_id"]
        )
        write_case_label(case, family, confidence, reason)
        rows.append(
            {
                "rd_dir": case["rd_dir"],
                "category": case["category"],
                "class": case["class"],
                "case_id": case["case_id"],
                "original_task_id": case["original_task_id"],
                "paper_family": family,
                "mapping_confidence": confidence,
                "mapping_reason": reason,
                "case_path": case["case_path"],
            }
        )
    write_global_outputs(rows)


if __name__ == "__main__":
    main()
