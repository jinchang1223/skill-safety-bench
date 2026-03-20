from __future__ import annotations

import importlib.util
from pathlib import Path

from attack_runtime import RegisteredCase, RegistryBuilder
from catalog import atom_attacks_root, load_case_specs


def build_registry() -> dict[str, RegisteredCase]:
    builder = RegistryBuilder(load_case_specs())
    for register in _discover_register_functions():
        register(builder)
    return builder.registry


def _discover_register_functions():
    root = atom_attacks_root()
    for attack_file in sorted(root.glob("risk-domain-*/category-*/*/attack.py")):
        module = _load_attack_module(root, attack_file)
        register = getattr(module, "register", None)
        if callable(register):
            yield register


def _load_attack_module(root: Path, attack_file: Path):
    relative = attack_file.relative_to(root).with_suffix("")
    module_name = "skill_safety_bench_atom_attacks." + ".".join(relative.parts)
    spec = importlib.util.spec_from_file_location(module_name, attack_file)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load attack module from {attack_file}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


__all__ = ["RegisteredCase", "RegistryBuilder", "build_registry"]
