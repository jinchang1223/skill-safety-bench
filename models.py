from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ATTACK_SURFACE_MODES = frozenset({"fixed", "choice", "composite"})
ATTACK_SURFACES = frozenset(
    {
        "task_instruction_surface",
        "skill_doc_surface",
        "skill_reference_surface",
        "skill_script_surface",
        "task_artifact_surface",
        "runtime_wrapper_surface",
        "docker_environment_surface",
        "output_channel_surface",
        "persistent_state_surface",
    }
)
LIFECYCLE_STAGES = frozenset(
    {
        "skill_discovery",
        "skill_interpretation",
        "skill_selection_and_planning",
        "skill_execution",
        "skill_output_and_handoff",
        "skill_memory_recovery_and_audit",
    }
)
COORDINATION_SCOPES = frozenset(
    {
        "single_agent",
        "delegated_subagent",
        "supervisor_worker",
        "peer_multi_agent",
        "federated_service_mesh",
    }
)
ATTACK_METHODS = frozenset(
    {
        "note_injection",
        "reference_forgery",
        "environment_artifact_forgery",
        "task_artifact_implant",
        "decoy_skill_fabrication",
        "cross_surface_amplification",
        "runtime_wrapper_hijack",
        "persistent_state_implant",
        "tool_output_interposition",
        "network_response_spoofing",
        "protocol_message_forgery",
        "approval_signal_spoofing",
        "runtime_env_poisoning",
        "observation_suppression",
        "planner_orchestrator_hijack",
    }
)


@dataclass(frozen=True)
class CaseSpec:
    id: str
    risk_domain: str
    category: str
    class_id: str
    lifecycle_stages: tuple[str, ...]
    name: str
    definition: str
    attack_story: str
    primary_surfaces: tuple[str, ...]
    surface_mode: str
    supported_surfaces: tuple[str, ...]
    default_surface: str | None
    payload_form: str
    target_induced_behaviors: tuple[str, ...]
    expected_safe_behaviors: tuple[str, ...]
    coordination_scopes: tuple[str, ...]
    attack_methods: tuple[str, ...]
    source_path: Path

    def __post_init__(self) -> None:
        unknown_stages = set(self.lifecycle_stages) - LIFECYCLE_STAGES
        if unknown_stages:
            raise ValueError(f"unknown lifecycle stages for case '{self.id}': {sorted(unknown_stages)}")

        unknown_primary = set(self.primary_surfaces) - ATTACK_SURFACES
        if unknown_primary:
            raise ValueError(f"unknown primary surfaces for case '{self.id}': {sorted(unknown_primary)}")

        if self.surface_mode not in ATTACK_SURFACE_MODES:
            raise ValueError(f"unknown surface_mode '{self.surface_mode}' for case '{self.id}'")

        unknown_supported = set(self.supported_surfaces) - ATTACK_SURFACES
        if unknown_supported:
            raise ValueError(f"unknown supported surfaces for case '{self.id}': {sorted(unknown_supported)}")

        if self.surface_mode == "fixed":
            if len(self.supported_surfaces) != 1:
                raise ValueError(f"fixed case '{self.id}' must support exactly one surface")
            if self.default_surface != self.supported_surfaces[0]:
                raise ValueError(f"fixed case '{self.id}' must use its only supported surface as default")
        elif self.surface_mode == "choice":
            if not self.supported_surfaces:
                raise ValueError(f"choice case '{self.id}' must declare supported surfaces")
            if self.default_surface is None:
                raise ValueError(f"choice case '{self.id}' must declare a default_surface")
            if self.default_surface not in self.supported_surfaces:
                raise ValueError(f"default_surface for case '{self.id}' must appear in supported_surfaces")
        else:
            if len(self.supported_surfaces) < 2:
                raise ValueError(f"composite case '{self.id}' must declare at least two supported surfaces")
            if self.default_surface is not None:
                raise ValueError(f"composite case '{self.id}' cannot declare a default_surface")

        if not self.coordination_scopes:
            raise ValueError(f"case '{self.id}' must declare at least one coordination scope")

        unknown_coordination = set(self.coordination_scopes) - COORDINATION_SCOPES
        if unknown_coordination:
            raise ValueError(
                f"unknown coordination scopes for case '{self.id}': {sorted(unknown_coordination)}"
            )

        unknown_attack_methods = set(self.attack_methods) - ATTACK_METHODS
        if unknown_attack_methods:
            raise ValueError(f"unknown attack methods for case '{self.id}': {sorted(unknown_attack_methods)}")

    def resolve_surface(self, requested_surface: object | None) -> str | None:
        if requested_surface is not None and not isinstance(requested_surface, str):
            raise TypeError(f"surface override for case '{self.id}' must be a string")

        if self.surface_mode == "composite":
            if requested_surface is not None:
                raise ValueError(
                    f"case '{self.id}' uses multiple coordinated surfaces and does not allow a single surface override"
                )
            return None

        if requested_surface is None:
            return self.default_surface

        if requested_surface not in self.supported_surfaces:
            raise ValueError(
                f"surface '{requested_surface}' is not supported for case '{self.id}'; "
                f"expected one of {list(self.supported_surfaces)}"
            )

        if self.surface_mode == "fixed" and requested_surface != self.default_surface:
            raise ValueError(f"case '{self.id}' uses a fixed surface '{self.default_surface}'")

        return requested_surface


@dataclass(frozen=True)
class SkillPaths:
    name: str
    root: Path
    skill_doc: Path
    references: tuple[Path, ...]
    scripts: tuple[Path, ...]
    assets: tuple[Path, ...]


@dataclass(frozen=True)
class TaskLayout:
    root: Path
    instruction_path: Path | None
    task_toml_path: Path | None
    environment_dir: Path | None
    dockerfile_path: Path | None
    skills_root: Path | None
    skills: tuple[SkillPaths, ...]
    task_files: tuple[Path, ...]


@dataclass(frozen=True)
class AttackSelection:
    case_id: str
    options: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class MaterializationConfig:
    source_task: Path
    output_task: Path
    attacks: tuple[AttackSelection, ...]


@dataclass
class MaterializationResult:
    output_task: Path
    applied_cases: list[str] = field(default_factory=list)
    created_files: list[Path] = field(default_factory=list)
    modified_files: list[Path] = field(default_factory=list)
