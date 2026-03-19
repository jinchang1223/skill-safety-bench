from __future__ import annotations

from pathlib import Path

from layout import discover_task_layout
from models import CaseSpec, MaterializationResult, SkillPaths, TaskLayout
from mutations import append_block, ensure_dockerfile_runtime_support, prepend_block, write_file


class AttackContext:
    def __init__(
        self,
        *,
        task_root: Path,
        case_spec: CaseSpec,
        result: MaterializationResult,
        options: dict[str, object] | None = None,
    ) -> None:
        self.task_root = task_root
        self.case_spec = case_spec
        self.result = result
        self.options = options or {}
        self.surface = case_spec.resolve_surface(self.options.get("surface"))
        self.layout = discover_task_layout(task_root)

    def instruction_path(self) -> Path:
        if not self.layout.instruction_path:
            raise FileNotFoundError("instruction.md not found in task root")
        return self.layout.instruction_path

    def pick_skill(self) -> SkillPaths:
        preferred = self.options.get("skill_name")
        if preferred:
            for skill in self.layout.skills:
                if skill.name == preferred:
                    return skill
            raise FileNotFoundError(f"skill '{preferred}' not found")
        if not self.layout.skills:
            raise FileNotFoundError("no skills discovered under environment/skills")
        return self.layout.skills[0]

    def pick_reference(self) -> Path:
        skill = self.pick_skill()
        preferred_name = self.options.get("reference_name")
        if preferred_name:
            for ref in skill.references:
                if ref.name == preferred_name:
                    return ref
            raise FileNotFoundError(f"reference '{preferred_name}' not found in skill '{skill.name}'")
        if skill.references:
            return skill.references[0]
        reference_dir = skill.root / "references"
        reference_dir.mkdir(parents=True, exist_ok=True)
        created = reference_dir / "skill_safety_bench_reference.md"
        if not created.exists():
            write_file(created, "# SkillSafetyBench Reference Seed", self.result)
        return created

    def pick_script(self) -> Path:
        skill = self.pick_skill()
        preferred_name = self.options.get("script_name")
        if preferred_name:
            for script in skill.scripts:
                if script.name == preferred_name:
                    return script
            raise FileNotFoundError(f"script '{preferred_name}' not found in skill '{skill.name}'")
        if skill.scripts:
            return skill.scripts[0]
        scripts_dir = skill.root / "scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        created = scripts_dir / "skill_safety_bench_helper.sh"
        if not created.exists():
            write_file(created, "#!/usr/bin/env bash\necho skill-safety-bench", self.result, executable=True)
        return created

    def add_instruction_note(self, note: str, prepend: bool = False) -> None:
        if prepend:
            prepend_block(self.instruction_path(), note, self.result)
        else:
            append_block(self.instruction_path(), note, self.result)

    def add_skill_doc_note(self, note: str, prepend: bool = False) -> None:
        skill_doc = self.pick_skill().skill_doc
        if prepend:
            prepend_block(skill_doc, note, self.result)
        else:
            append_block(skill_doc, note, self.result)

    def add_reference_note(self, note: str) -> None:
        append_block(self.pick_reference(), note, self.result)

    def add_note_to_surface(self, surface: str, note: str, prepend: bool = False) -> None:
        if surface == "task_instruction_surface":
            self.add_instruction_note(note, prepend=prepend)
            return
        if surface == "skill_doc_surface":
            self.add_skill_doc_note(note, prepend=prepend)
            return
        if surface == "skill_reference_surface":
            reference = self.pick_reference()
            if prepend:
                prepend_block(reference, note, self.result)
            else:
                append_block(reference, note, self.result)
            return
        raise ValueError(f"surface '{surface}' does not support note injection for case '{self.case_spec.id}'")

    def add_note_to_selected_surface(self, note: str, prepend: bool = False) -> None:
        if self.surface is None:
            raise ValueError(
                f"case '{self.case_spec.id}' uses composite surfaces and cannot use add_note_to_selected_surface()"
            )
        self.add_note_to_surface(self.surface, note, prepend=prepend)

    def create_reference_file(self, filename: str, content: str) -> Path:
        skill = self.pick_skill()
        path = skill.root / "references" / filename
        write_file(path, content, self.result)
        return path

    def create_task_artifact(self, relative_path: str, content: str) -> Path:
        artifact_path = self.task_root / relative_path
        write_file(artifact_path, content, self.result)
        return artifact_path

    def install_runtime_wrapper(self, command_name: str, script_body: str) -> Path:
        if not self.layout.environment_dir:
            raise FileNotFoundError("environment directory not found")
        runtime_root = self.layout.environment_dir / "skill-safety-bench-runtime"
        bin_dir = runtime_root / "bin"
        wrapper_path = bin_dir / command_name
        write_file(wrapper_path, script_body, self.result, executable=True)
        if not self.layout.dockerfile_path:
            raise FileNotFoundError("Dockerfile not found in environment")
        ensure_dockerfile_runtime_support(
            self.layout.dockerfile_path,
            "skill-safety-bench-runtime",
            "/opt/skill-safety-bench-runtime",
            'ENV PATH="/opt/skill-safety-bench-runtime/bin:${PATH}"',
            self.result,
        )
        return wrapper_path

    def refresh(self) -> TaskLayout:
        self.layout = discover_task_layout(self.task_root)
        return self.layout
