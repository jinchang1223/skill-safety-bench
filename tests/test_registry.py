from __future__ import annotations

import unittest

from case_library import build_registry
from catalog import load_case_specs


class RegistryCoverageTest(unittest.TestCase):
    def test_every_case_spec_has_an_attack_implementation(self) -> None:
        self.assertEqual(set(load_case_specs()), set(build_registry()))

    def test_every_case_spec_exposes_valid_surface_metadata(self) -> None:
        for spec in load_case_specs().values():
            self.assertTrue(spec.coordination_scopes)
            if spec.surface_mode == "composite":
                self.assertIsNone(spec.resolve_surface(None))
                with self.assertRaises(ValueError):
                    spec.resolve_surface("skill_doc_surface")
                continue

            self.assertEqual(spec.resolve_surface(None), spec.default_surface)
            self.assertEqual(spec.resolve_surface(spec.default_surface), spec.default_surface)

    def test_every_case_declares_attack_methods(self) -> None:
        for spec in load_case_specs().values():
            self.assertTrue(spec.attack_methods, f"case '{spec.id}' must declare attack_methods")


if __name__ == "__main__":
    unittest.main()
