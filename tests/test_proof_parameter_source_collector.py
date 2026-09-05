import importlib.machinery
import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader(
    "proof_sources", str(ROOT / "scripts/collect-proof-parameter-sources")
)
spec = importlib.util.spec_from_loader(loader.name, loader)
module = importlib.util.module_from_spec(spec)
loader.exec_module(module)


class ProofParameterSourceCollectorTests(unittest.TestCase):
    def test_scope_is_two_pinned_get_requests(self):
        self.assertEqual(len(module.SOURCES), 2)
        for _, endpoint, _ in module.SOURCES:
            self.assertTrue(endpoint.startswith("repos/"))
            self.assertIn("?ref=", endpoint)


if __name__ == "__main__":
    unittest.main()
