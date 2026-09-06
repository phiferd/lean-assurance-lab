"""Characterize the stopped controller's module/namespace ordering boundary."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lib import cvc_prep as prep
SCRIPT = ROOT / 'results/research/conditional-validation-contracts/cvc-prep-1/validate-evidence.py'
spec = importlib.util.spec_from_file_location('cvc_prep_closure', SCRIPT)
closure = importlib.util.module_from_spec(spec)
spec.loader.exec_module(closure)


class ClosureBoundaryTests(unittest.TestCase):
    def fixture(self, root):
        build = root / 'build'
        for rel in ['Pkg/Thing/A.olean', 'Pkg/Thing.olean']:
            p = build / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(rel)
        return build, prep.inventory(root, build)

    def test_characterized_path_vs_string_order_boundary(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build, outputs = self.fixture(root)
            state = {1: {'terminal': {'status': 'COMPLETE', 'outputs': outputs}}}
            self.assertNotEqual(outputs, sorted(outputs, key=lambda r: r['path']))
            with self.assertRaisesRegex(ValueError, 'unrecorded or missing'):
                prep.verify_prior_outputs(root, state, build)
            self.assertEqual(closure.verify_output_set(root, build, outputs), outputs)

    def test_closure_still_rejects_changed_and_additional_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build, outputs = self.fixture(root)
            extra = build / 'extra.ir'
            extra.write_text('additional')
            with self.assertRaises(ValueError):
                closure.verify_output_set(root, build, outputs)
            extra.unlink()
            (build / 'Pkg/Thing.olean').write_text('changed')
            with self.assertRaises(ValueError):
                closure.verify_output_set(root, build, outputs)

    def test_duplicate_receipts_are_not_collapsed_into_success(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build, outputs = self.fixture(root)
            with self.assertRaisesRegex(ValueError, 'duplicate'):
                closure.verify_output_set(root, build, outputs + [outputs[0]])


if __name__ == '__main__':
    unittest.main()
