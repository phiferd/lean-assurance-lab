import importlib.machinery
import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader(
    "arena_tutorial_source", str(ROOT / "scripts/collect-arena-tutorial-source")
)
spec = importlib.util.spec_from_loader(loader.name, loader)
module = importlib.util.module_from_spec(spec)
loader.exec_module(module)


class ArenaTutorialSourceCollectorTests(unittest.TestCase):
    def test_request_is_pinned_get_only_scope(self):
        self.assertEqual(
            module.ENDPOINT,
            "repos/leanprover/lean-kernel-arena/contents/tutorial/Tutorial.lean"
            "?ref=abc55357aee17c59dfdbf39c8a2e19739e23dd10",
        )


if __name__ == "__main__":
    unittest.main()
