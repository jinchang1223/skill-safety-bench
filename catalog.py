from __future__ import annotations

from pathlib import Path

import yaml

from models import CaseSpec


def _repo_root() -> Path:
    return Path(__file__).resolve().parent


def atom_attacks_root() -> Path:
    return _repo_root() / "atom-attacks"


def iter_case_files(root: Path | None = None) -> list[Path]:
    base = root or atom_attacks_root()
    return sorted(base.glob("risk-domain-*/category-*/*/cases/*.yaml"))


def load_case_specs(root: Path | None = None) -> dict[str, CaseSpec]:
    specs: dict[str, CaseSpec] = {}
    for case_file in iter_case_files(root):
        data = yaml.safe_load(case_file.read_text(encoding="utf-8"))
        class_file = case_file.parent.parent / "class.yaml"
        class_data = yaml.safe_load(class_file.read_text(encoding="utf-8")) if class_file.exists() else {}
        primary_surfaces = tuple(data.get("primary_surfaces", []))
        supported_surfaces = tuple(data.get("supported_surfaces", primary_surfaces))
        surface_mode = data.get("surface_mode")
        if not surface_mode:
            surface_mode = "composite" if len(supported_surfaces) > 1 else "fixed"
        default_surface = data.get("default_surface")
        if default_surface is None and surface_mode != "composite" and supported_surfaces:
            default_surface = supported_surfaces[0]
        coordination_scopes = tuple(
            data.get("coordination_scopes", class_data.get("coordination_scopes", ["single_agent"]))
        )
        attack_methods = tuple(data.get("attack_methods", []))
        spec = CaseSpec(
            id=data["id"],
            risk_domain=data["risk_domain"],
            category=data["category"],
            class_id=data["class"],
            lifecycle_stages=tuple(data.get("lifecycle_stages", [])),
            name=data["name"],
            definition=data["definition"],
            attack_story=data.get("attack_story", ""),
            primary_surfaces=primary_surfaces,
            surface_mode=surface_mode,
            supported_surfaces=supported_surfaces,
            default_surface=default_surface,
            payload_form=data.get("payload_form", ""),
            target_induced_behaviors=tuple(data.get("target_induced_behaviors", [])),
            expected_safe_behaviors=tuple(data.get("expected_safe_behaviors", [])),
            coordination_scopes=coordination_scopes,
            attack_methods=attack_methods,
            source_path=case_file,
        )
        specs[spec.id] = spec
    return specs
