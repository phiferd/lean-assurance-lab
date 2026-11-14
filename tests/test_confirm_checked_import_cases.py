import importlib.util
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "results/research/confirm-checked-import-cases-1"
sys.path.insert(0, str(HERE))


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


freeze = load("freeze_manifest")
runner = load("run_confirmation")
common = load("confirmation_common")


class ConfirmCheckedImportCasesTests(unittest.TestCase):
    def test_manifest_has_fixed_qualified_matrix(self):
        manifest = freeze.build_manifest()
        self.assertEqual(manifest["cells_per_phase"], 20)
        self.assertEqual(manifest["total_required_cells"], 40)
        self.assertEqual(len(manifest["cases"]), 20)
        self.assertEqual(len({cell["id"] for cell in manifest["cases"]}), 20)
        self.assertEqual(sum(cell["expected"] == "ACCEPT" for cell in manifest["cases"]), 10)
        self.assertEqual(sum(cell["expected"] == "REJECT" for cell in manifest["cases"]), 10)
        self.assertIn("pi/A-negative/lean", {cell["id"] for cell in manifest["cases"]})
        self.assertIn("generic rejection is unresolved", manifest["classification"]["pi_a_guard"])

    def test_runner_uses_exact_image_and_isolation_for_every_cell(self):
        cells = freeze.build_manifest()["cases"]
        names = set()
        for phase in ("initial", "replay"):
            for cell in cells:
                name, argv = runner.cell_argv(phase, cell)
                self.assertNotIn(name, names)
                names.add(name)
                self.assertIn(common.IMAGE, argv)
                self.assertIn("--network", argv)
                self.assertIn("none", argv)
                self.assertIn("--read-only", argv)
                self.assertIn("--rm", argv)
                self.assertIn("1001:1001", argv)
                self.assertTrue(any(arg.endswith(",readonly") for arg in argv if arg.startswith("type=bind")))
        self.assertEqual(len(names), 40)

    def test_family_qualified_names_prevent_b_collision(self):
        cells = freeze.build_manifest()["cases"]
        b_controls = [cell["id"] for cell in cells if cell["source_case_id"] == "B-control"]
        self.assertEqual(sorted(b_controls), [
            "expression/B-control/lean", "expression/B-control/nanoda",
            "pi/B-control/lean", "pi/B-control/nanoda",
        ])


if __name__ == "__main__":
    unittest.main()
