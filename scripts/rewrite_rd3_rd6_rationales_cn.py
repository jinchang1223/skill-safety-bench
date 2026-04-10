#!/usr/bin/env python3
from __future__ import annotations

import difflib
import json
import re
import zipfile
from pathlib import Path
from typing import Iterable


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
BENCH_ROOT = WORKSPACE_ROOT / "skill-safety-bench"
BENCHMARK_ROOT = BENCH_ROOT / "benchmark"
TASKS_ROOT = WORKSPACE_ROOT / "skillsbench" / "tasks"

TEXT_EXTENSIONS = {
    ".md",
    ".txt",
    ".json",
    ".jsonl",
    ".py",
    ".sh",
    ".bash",
    ".yaml",
    ".yml",
    ".toml",
    ".csv",
    ".tsv",
    ".xml",
    ".html",
    ".htm",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".css",
    ".scss",
    ".java",
    ".scala",
    ".go",
    ".rs",
    ".c",
    ".cc",
    ".cpp",
    ".h",
    ".hpp",
    ".sql",
    ".bib",
    ".ini",
    ".cfg",
    ".conf",
    ".lock",
}

OFFICE_EXTENSIONS = {".docx", ".pptx", ".xlsx"}
MAX_PRIMARY_FILES = 12
MAX_SUPPORT_FILES = 10
MAX_SNIPPETS = 8
MAX_VERIFY_LINES = 10


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def manifest_paths() -> list[Path]:
    paths = []
    for rd in (3, 4, 5, 6):
        paths.append(next(BENCHMARK_ROOT.glob(f"risk-domain-{rd}-*")) / "manifest.json")
    return paths


def read_text_safe(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="ignore")


def is_text_file(path: Path) -> bool:
    if path.suffix.lower() in TEXT_EXTENSIONS:
        return True
    try:
        sample = path.read_bytes()[:2048]
    except OSError:
        return False
    return b"\x00" not in sample


def clean_inline(text: str, limit: int = 220) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text[: limit - 1] + "…" if len(text) > limit else text


def summarize_instruction(original_task_dir: Path) -> str:
    instruction = original_task_dir / "instruction.md"
    if not instruction.exists():
        return "原任务目录中没有找到 `instruction.md`。"
    text = read_text_safe(instruction)
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"#+\s*", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return clean_inline(text, 320)


def instruction_consistency(original_task_dir: Path, attacked_task_dir: Path) -> str:
    orig = original_task_dir / "instruction.md"
    attacked = attacked_task_dir / "instruction.md"
    if not orig.exists() or not attacked.exists():
        return "无法比较：原任务或攻击任务缺少 `instruction.md`。"
    return "一致" if orig.read_text(encoding="utf-8") == attacked.read_text(encoding="utf-8") else "不一致"


def relative_to_case(case_dir: Path, path: Path) -> str:
    try:
        return str(path.relative_to(case_dir)).replace("\\", "/")
    except ValueError:
        try:
            return str(path.relative_to(WORKSPACE_ROOT)).replace("\\", "/")
        except ValueError:
            return str(path)


def list_relative_files(root: Path) -> set[Path]:
    if not root.exists():
        return set()
    return {
        p.relative_to(root)
        for p in root.rglob("*")
        if p.is_file()
    }


def file_status(original_task_dir: Path, attacked_task_dir: Path, rel: Path) -> str:
    orig = original_task_dir / rel
    attacked = attacked_task_dir / rel
    if attacked.exists() and not orig.exists():
        return "新增"
    if orig.exists() and not attacked.exists():
        return "删除"
    if orig.exists() and attacked.exists():
        if orig.read_bytes() == attacked.read_bytes():
            return "未变"
        return "修改"
    return "缺失"


def meaningful_lines(text: str) -> list[str]:
    lines = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line in {"{", "}", "[", "]"}:
            continue
        lines.append(clean_inline(line, 180))
    return lines


def diff_added_lines(old_text: str, new_text: str) -> list[str]:
    lines = []
    for line in difflib.unified_diff(
        old_text.splitlines(),
        new_text.splitlines(),
        lineterm="",
        n=0,
    ):
        if line.startswith(("+++", "---", "@@")):
            continue
        if not line.startswith("+"):
            continue
        value = line[1:].strip()
        if not value:
            continue
        value = clean_inline(value, 180)
        if value not in lines:
            lines.append(value)
        if len(lines) >= MAX_SNIPPETS:
            break
    return lines


def xmlish_to_text(payload: bytes) -> str:
    text = payload.decode("utf-8", errors="ignore")
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def zip_entry_snippets(old_path: Path | None, new_path: Path | None) -> tuple[list[str], list[str]]:
    summary: list[str] = []
    snippets: list[str] = []
    old_entries: dict[str, bytes] = {}
    new_entries: dict[str, bytes] = {}
    if old_path and old_path.exists() and zipfile.is_zipfile(old_path):
        with zipfile.ZipFile(old_path) as zf:
            for name in zf.namelist():
                old_entries[name] = zf.read(name)
    if new_path and new_path.exists() and zipfile.is_zipfile(new_path):
        with zipfile.ZipFile(new_path) as zf:
            for name in zf.namelist():
                new_entries[name] = zf.read(name)

    all_names = sorted(set(old_entries) | set(new_entries))
    added = [n for n in all_names if n not in old_entries]
    removed = [n for n in all_names if n not in new_entries]
    modified = [n for n in all_names if n in old_entries and n in new_entries and old_entries[n] != new_entries[n]]

    if added:
        summary.append(f"压缩容器内部新增条目：{', '.join(added[:4])}")
    if removed:
        summary.append(f"压缩容器内部删除条目：{', '.join(removed[:4])}")
    if modified:
        summary.append(f"压缩容器内部修改条目：{', '.join(modified[:6])}")

    for name in modified[:6] + added[:4]:
        payload = new_entries.get(name, b"")
        if not payload:
            continue
        if name.endswith((".xml", ".rels", ".txt", ".json")):
            new_text = xmlish_to_text(payload)
            old_text = xmlish_to_text(old_entries.get(name, b""))
            for item in diff_added_lines(old_text, new_text):
                if item not in snippets:
                    snippets.append(item)
                if len(snippets) >= MAX_SNIPPETS:
                    return summary, snippets
    return summary, snippets


def describe_file_change(case_dir: Path, original_task_dir: Path, attacked_task_dir: Path, rel: Path) -> list[str]:
    attacked = attacked_task_dir / rel
    original = original_task_dir / rel
    status = file_status(original_task_dir, attacked_task_dir, rel)
    lines = [f"- `{relative_to_case(case_dir, attacked)}`：{status}"]

    if status == "新增":
        if attacked.exists():
            if attacked.suffix.lower() in OFFICE_EXTENSIONS and zipfile.is_zipfile(attacked):
                summary, snippets = zip_entry_snippets(None, attacked)
                for item in summary[:4]:
                    lines.append(f"  - {item}")
                if snippets:
                    lines.append("  - 可直接观察到的新增内容片段：")
                    for item in snippets[:MAX_SNIPPETS]:
                        lines.append(f"  - `{item}`")
                else:
                    lines.append("  - Office/压缩容器文件，已确认新增，但没有稳定抽取到可直接展示的文本片段。")
            elif is_text_file(attacked):
                lines.append("  - 新增文件的关键内容：")
                for item in meaningful_lines(read_text_safe(attacked))[:MAX_SNIPPETS]:
                    lines.append(f"  - `{item}`")
            else:
                lines.append("  - 二进制或复杂工件，当前说明记录为新增文件。")
        else:
            lines.append("  - `metadata.json` 声明了该文件，但当前仓库中没有找到。")
        return lines

    if status == "修改":
        if attacked.suffix.lower() in OFFICE_EXTENSIONS and zipfile.is_zipfile(attacked):
            summary, snippets = zip_entry_snippets(original if original.exists() else None, attacked)
            for item in summary[:4]:
                lines.append(f"  - {item}")
            if snippets:
                lines.append("  - 可直接观察到的新增/改写内容片段：")
                for item in snippets[:MAX_SNIPPETS]:
                    lines.append(f"  - `{item}`")
            else:
                lines.append("  - Office/压缩容器文件已修改，但没有稳定抽取到可直接展示的文本片段。")
            return lines
        if attacked.exists() and original.exists() and is_text_file(attacked) and is_text_file(original):
            added = diff_added_lines(read_text_safe(original), read_text_safe(attacked))
            if added:
                lines.append("  - 关键新增/替换文本：")
                for item in added[:MAX_SNIPPETS]:
                    lines.append(f"  - `{item}`")
            else:
                lines.append("  - 文件已修改，但没有抽取到稳定的新增文本；这通常意味着改动发生在改名、删改、缩进或结构调整上。")
        else:
            lines.append("  - 二进制或复杂工件，当前说明记录为已修改文件。")
        return lines

    if status == "删除":
        lines.append("  - 原任务里存在该文件，攻击版删除了它。")
        return lines

    lines.append("  - 当前对比中没有发现实际差异，或文件状态无法确定。")
    return lines


def gather_all_diffs(original_task_dir: Path, attacked_task_dir: Path) -> list[tuple[Path, str]]:
    orig_files = list_relative_files(original_task_dir)
    attacked_files = list_relative_files(attacked_task_dir)
    all_rels = sorted(orig_files | attacked_files)
    diffs = []
    for rel in all_rels:
        status = file_status(original_task_dir, attacked_task_dir, rel)
        if status != "未变":
            diffs.append((rel, status))
    return diffs


def parse_verify_script(verify_path: Path) -> tuple[list[str], list[str]]:
    if not verify_path.exists():
        return [], ["当前 case 缺少 `eval/verify_attack.py`。"]

    text = read_text_safe(verify_path)
    paths = []
    for match in re.finditer(r"['\"](/(?:root|app)[^'\"]+)['\"]", text):
        path = match.group(1)
        if path not in paths:
            paths.append(path)

    interesting = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if any(token in line for token in ("attack_success", "attack_not_observed", "task_output_missing", "target", "marker", "keyword", "Path(", "REQUIRED", "expected", "state", "contains", "missing")):
            formatted = clean_inline(line, 220)
            if formatted not in interesting:
                interesting.append(formatted)
        if len(interesting) >= MAX_VERIFY_LINES:
            break
    return paths, interesting


def format_list(items: Iterable[str]) -> list[str]:
    return [f"- {item}" for item in items]


def build_rationale(case: dict) -> str:
    case_dir = WORKSPACE_ROOT / case["case_path"]
    attacked_task_dir = WORKSPACE_ROOT / case["task_path"]
    original_task_dir = WORKSPACE_ROOT / case["original_task_path"]
    metadata_path = case_dir / "metadata.json"
    metadata = load_json(metadata_path)

    original_summary = summarize_instruction(original_task_dir)
    instruction_match = instruction_consistency(original_task_dir, attacked_task_dir)

    injected_files = []
    for item in metadata.get("injected_or_modified_files", []):
        path = WORKSPACE_ROOT / item
        try:
            rel = path.relative_to(attacked_task_dir)
        except ValueError:
            # Fallback for stale metadata paths: locate by attacked_task suffix if possible.
            text = item.replace("\\", "/")
            marker = "/attacked_task/"
            if marker in text:
                rel = Path(text.split(marker, 1)[1])
            else:
                rel = Path(path.name)
        injected_files.append(rel)

    all_diffs = gather_all_diffs(original_task_dir, attacked_task_dir)
    injected_set = set(injected_files)
    support_diffs = [(rel, status) for rel, status in all_diffs if rel not in injected_set]

    lines: list[str] = []
    lines.append(f"# {case['case_id']} 说明")
    lines.append("")
    lines.append("## 1. 原任务在做什么")
    lines.append("")
    lines.append(f"- 原始任务 ID：`{case['original_task_id']}`")
    lines.append(f"- 原始任务路径：`{case['original_task_path']}`")
    lines.append(f"- 原始任务摘要：{original_summary}")
    lines.append(f"- 当前 case 的 `attacked_task/instruction.md` 与原任务 `instruction.md` 是否一致：`{instruction_match}`")
    lines.append("")
    lines.append("## 2. 直接攻击材料：具体改了哪些文件、加了什么文本")
    lines.append("")
    lines.append("下面优先列出 `metadata.json` 里声明的主攻击材料。这些文件承载了当前攻击的主要语义：它们决定 agent 会看到什么错误规则、错误 sidecar、错误 helper、错误环境线索，或者什么被污染的输出模板。")
    lines.append("")

    if injected_files:
        for rel in injected_files[:MAX_PRIMARY_FILES]:
            lines.extend(describe_file_change(case_dir, original_task_dir, attacked_task_dir, rel))
            lines.append("")
        remaining = len(injected_files) - MAX_PRIMARY_FILES
        if remaining > 0:
            lines.append(f"- 另外还有 `{remaining}` 个 `metadata.json` 声明的攻击文件未在这里逐条展开；它们仍然属于主攻击材料，只是为了避免说明过长而省略。")
            lines.append("")
    else:
        lines.append("- `metadata.json` 没有列出 `injected_or_modified_files`；当前 case 只能退回到 attacked_task 与原任务的目录 diff 来解释改动。")
        lines.append("")

    lines.append("## 3. 配套修改：除主攻击材料外，还改了什么")
    lines.append("")
    lines.append("这一节列出相对原任务真实发生、但不一定属于主攻击载体的差异。它们通常用于让主攻击材料能被加载、被复制进容器、被 solve 脚本读取、被 skill 发现，或者让 benchmark 打包本身能运行。")
    lines.append("")

    if support_diffs:
        for rel, _ in support_diffs[:MAX_SUPPORT_FILES]:
            lines.extend(describe_file_change(case_dir, original_task_dir, attacked_task_dir, rel))
            lines.append("")
        remaining = len(support_diffs) - MAX_SUPPORT_FILES
        if remaining > 0:
            lines.append(f"- 另外还有 `{remaining}` 个配套差异文件没有逐条展开；当前 `rationale.md` 优先保留了最可能影响加载链、运行链和输出链的部分。")
            lines.append("")
    else:
        lines.append("- 没有发现额外的 attacked_task 侧配套修改；当前攻击主要就落在上面的主攻击材料里。")
        lines.append("")

    lines.append("## 4. 为什么要这样改、为什么这个攻击成立")
    lines.append("")
    lines.append(f"- `metadata.attack_surface`：{', '.join(f'`{x}`' for x in metadata.get('attack_surface', [])) or '未提供'}")
    lines.append(f"- `metadata.attack_mechanism`：{metadata.get('attack_mechanism', '未提供')}")
    lines.append(f"- `metadata.selected_reason`：{metadata.get('selected_reason', '未提供')}")
    lines.append(f"- 想诱导出的错误行为：{metadata.get('expected_agent_behavior', '未提供')}")
    lines.append(f"- 想造成的失败后果：{metadata.get('expected_failure_mode', '未提供')}")
    lines.append(f"- 命中时应出现的成功信号：{metadata.get('expected_attack_success_signal', '未提供')}")
    lines.append("- 这条攻击为什么是合理的：当前 case 保持用户任务不变，攻击主要落在非用户面材料上，例如 skill、sidecar、helper、registry、Dockerfile、workspace wrapper、缓存或导出模板。也就是说，benchmark 在测的是 agent 会不会信任这些本地环境材料，并主动把错误内容传播进主输出，或者主动采取一个本来不该采取的动作。")
    lines.append("- 和原始任务相比，攻击版并不是单纯把正文里原本就存在的内容留在原位，而是通过上面列出的改动，让 agent 在执行过程中继承错误 authority、错误 runtime 路径、错误输出契约、错误持久化线索、错误检索结果，或错误供应链对象。")
    lines.append("")

    lines.append("## 5. 验证脚本在验证什么")
    lines.append("")
    verify_path = case_dir / "eval" / "verify_attack.py"
    verify_paths, verify_lines = parse_verify_script(verify_path)
    lines.append(f"- 验证脚本路径：`{relative_to_case(case_dir, verify_path)}`")
    if verify_paths:
        lines.append("- verifier 重点读取的输出路径：")
        for item in verify_paths:
            lines.append(f"  - `{item}`")
    else:
        lines.append("- verifier 重点读取的输出路径：脚本内没有显式出现标准 `/root/...` 或 `/app/output/...` 路径字面量。")
    lines.append(f"- verifier 目标成功信号：{metadata.get('expected_attack_success_signal', '未提供')}")
    if verify_lines:
        lines.append("- `verify_attack.py` 里的关键判断语句：")
        for item in verify_lines:
            lines.append(f"  - `{item}`")
    lines.append("- 也就是说，这个 verifier 真正想验证的是：agent 最终导出的主输出、side-effect 文件、bundle 文件、脚本痕迹或结构化字段里，是否出现了当前 case 预期的攻击命中信号，而不是只看过程里有没有访问过某个提示文件。")
    lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    count = 0
    for manifest_path in manifest_paths():
        manifest = load_json(manifest_path)
        for case in manifest["cases"]:
            case_dir = WORKSPACE_ROOT / case["case_path"]
            rationale_path = case_dir / "rationale.md"
            rationale_path.write_text(build_rationale(case), encoding="utf-8")
            count += 1
    print(f"rewrote {count} rationale.md files for RD3-RD6")


if __name__ == "__main__":
    main()
