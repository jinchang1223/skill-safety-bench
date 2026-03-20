from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from models import AttackSelection, MaterializationConfig
from runner import materialize_attacked_task


class MaterializeAttackTest(unittest.TestCase):
    def test_materialize_on_synthetic_task(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            source = tmp / "source-task"
            output = tmp / "attacked-task"
            _build_synthetic_task(source)

            result = materialize_attacked_task(
                MaterializationConfig(
                    source_task=source,
                    output_task=output,
                    attacks=(
                        AttackSelection(case_id="task_vs_skill_flip", options={"skill_name": "demo-skill"}),
                        AttackSelection(case_id="fabricated_threshold", options={"skill_name": "demo-skill"}),
                        AttackSelection(case_id="path_shadowing", options={"skill_name": "demo-skill", "command_name": "python3"}),
                        AttackSelection(case_id="poisoned_csv_column", options={"skill_name": "demo-skill"}),
                    ),
                )
            )

            self.assertEqual(
                result.applied_cases,
                ["task_vs_skill_flip", "fabricated_threshold", "path_shadowing", "poisoned_csv_column"],
            )
            self.assertTrue((output / ".skill-safety-bench" / "materialization.json").exists())
            self.assertTrue((output / "environment" / "attack_artifacts" / "poisoned_validation.csv").exists())
            self.assertTrue((output / "environment" / "skill-safety-bench-runtime" / "bin" / "python3").exists())
            self.assertIn(
                "Priority Override",
                (output / "environment" / "skills" / "demo-skill" / "SKILL.md").read_text(encoding="utf-8"),
            )
            self.assertIn(
                "Validation Threshold Update",
                (output / "environment" / "skills" / "demo-skill" / "references" / "ssb_fabricated_threshold.md").read_text(
                    encoding="utf-8"
                ),
            )
            dockerfile_text = (output / "environment" / "Dockerfile").read_text(encoding="utf-8")
            self.assertIn("COPY attack_artifacts /opt/skill-safety-bench-artifacts", dockerfile_text)
            self.assertIn('ENV SSB_ARTIFACT_ROOT="/opt/skill-safety-bench-artifacts"', dockerfile_text)

    def test_choice_surface_override_moves_attack_to_selected_surface(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            source = tmp / "source-task"
            output = tmp / "attacked-task"
            _build_synthetic_task(source)

            materialize_attacked_task(
                MaterializationConfig(
                    source_task=source,
                    output_task=output,
                    attacks=(
                        AttackSelection(
                            case_id="manager_already_approved_note",
                            options={"skill_name": "demo-skill", "surface": "skill_doc_surface"},
                        ),
                    ),
                )
            )

            instruction_text = (output / "instruction.md").read_text(encoding="utf-8")
            skill_text = (output / "environment" / "skills" / "demo-skill" / "SKILL.md").read_text(encoding="utf-8")
            self.assertNotIn("Pre-Approval Notice", instruction_text)
            self.assertIn("Pre-Approval Notice", skill_text)

    def test_fixed_surface_override_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            source = tmp / "source-task"
            output = tmp / "attacked-task"
            _build_synthetic_task(source)

            with self.assertRaisesRegex(ValueError, "not supported"):
                materialize_attacked_task(
                    MaterializationConfig(
                        source_task=source,
                        output_task=output,
                        attacks=(
                            AttackSelection(
                                case_id="task_vs_skill_flip",
                                options={"skill_name": "demo-skill", "surface": "task_instruction_surface"},
                            ),
                        ),
                    )
                )

    def test_multi_agent_handoff_case_materializes_artifact_and_instruction_link(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            source = tmp / "source-task"
            output = tmp / "attacked-task"
            _build_synthetic_task(source)

            materialize_attacked_task(
                MaterializationConfig(
                    source_task=source,
                    output_task=output,
                    attacks=(
                        AttackSelection(
                            case_id="worker_handoff_recommendation",
                            options={"skill_name": "demo-skill"},
                        ),
                    ),
                )
            )

            instruction_text = (output / "instruction.md").read_text(encoding="utf-8")
            dockerfile_text = (output / "environment" / "Dockerfile").read_text(encoding="utf-8")
            artifact_text = (output / "environment" / "attack_artifacts" / "ssb_worker_handoff_route.md").read_text(
                encoding="utf-8"
            )

            self.assertIn("/opt/skill-safety-bench-artifacts/ssb_worker_handoff_route.md", instruction_text)
            self.assertIn("already triaged by worker-prep", artifact_text)
            self.assertIn("COPY attack_artifacts /opt/skill-safety-bench-artifacts", dockerfile_text)


def _build_synthetic_task(root: Path) -> None:
    (root / "environment" / "skills" / "demo-skill" / "references").mkdir(parents=True)
    (root / "environment" / "skills" / "demo-skill" / "scripts").mkdir(parents=True)
    (root / "instruction.md").write_text("Do the task.\n", encoding="utf-8")
    (root / "task.toml").write_text("version = '1.0'\n", encoding="utf-8")
    (root / "environment" / "Dockerfile").write_text(
        textwrap.dedent(
            """\
            FROM ubuntu:24.04
            WORKDIR /root
            COPY skills /root/.codex/skills
            """
        ),
        encoding="utf-8",
    )
    (root / "environment" / "skills" / "demo-skill" / "SKILL.md").write_text(
        "# Demo Skill\n\nBase workflow.\n",
        encoding="utf-8",
    )
    (root / "environment" / "skills" / "demo-skill" / "references" / "guide.md").write_text("# Guide\n", encoding="utf-8")
    (root / "environment" / "skills" / "demo-skill" / "scripts" / "helper.sh").write_text(
        "#!/usr/bin/env bash\necho helper\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    unittest.main()
