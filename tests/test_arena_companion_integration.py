import importlib.machinery
import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader(
    "arena_companions", str(ROOT / "scripts/integrate-arena-companion-pairs")
)
spec = importlib.util.spec_from_loader(loader.name, loader)
module = importlib.util.module_from_spec(spec)
loader.exec_module(module)


class ArenaCompanionIntegrationTests(unittest.TestCase):
    def test_expected_outcomes_preserve_scientific_boundary(self):
        proof = module.PAIRS["proof-parameter-uniformity"]
        positivity = module.PAIRS["reducible-hidden-positivity"]
        self.assertEqual(proof["outcomes"], {"control": "accept", "candidate": "either"})
        self.assertEqual(positivity["outcomes"], {"control": "accept", "candidate": "reject"})

    def test_static_definitions_need_no_toolchain_or_checker(self):
        for pair in module.PAIRS.values():
            for role in ("control", "candidate"):
                text = module.yaml_text(pair["description"], "case.ndjson", pair["outcomes"][role])
                self.assertIn("file: tests/case.ndjson", text)
                self.assertNotIn("leanfile:", text)
                self.assertNotIn("run:", text)
                self.assertNotIn("checker", text.lower())


if __name__ == "__main__":
    unittest.main()
