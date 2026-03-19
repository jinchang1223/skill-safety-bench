from __future__ import annotations

from pathlib import Path

from models import SkillPaths, TaskLayout


def discover_task_layout(task_root: Path) -> TaskLayout:
    root = task_root.resolve()
    instruction_path = _existing(root / "instruction.md")
    task_toml_path = _existing(root / "task.toml")
    environment_dir = _existing(root / "environment")
    dockerfile_path = _existing(root / "environment" / "Dockerfile")
    skills_root = _existing(root / "environment" / "skills")

    skills: list[SkillPaths] = []
    if skills_root:
        for entry in sorted(p for p in skills_root.iterdir() if p.is_dir()):
            skill_doc = _existing(entry / "SKILL.md")
            if skill_doc is None:
                continue
            skills.append(
                SkillPaths(
                    name=entry.name,
                    root=entry,
                    skill_doc=skill_doc,
                    references=tuple(sorted((entry / "references").glob("*"))) if (entry / "references").exists() else (),
                    scripts=tuple(sorted((entry / "scripts").glob("*"))) if (entry / "scripts").exists() else (),
                    assets=tuple(sorted((entry / "assets").glob("*"))) if (entry / "assets").exists() else (),
                )
            )

    task_files = tuple(
        sorted(
            p
            for p in root.rglob("*")
            if p.is_file()
            and ".git" not in p.parts
            and "__pycache__" not in p.parts
        )
    )
    return TaskLayout(
        root=root,
        instruction_path=instruction_path,
        task_toml_path=task_toml_path,
        environment_dir=environment_dir,
        dockerfile_path=dockerfile_path,
        skills_root=skills_root,
        skills=tuple(skills),
        task_files=task_files,
    )


def _existing(path: Path) -> Path | None:
    return path if path.exists() else None
