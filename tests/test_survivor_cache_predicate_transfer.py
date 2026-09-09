from importlib.machinery import SourceFileLoader
from types import ModuleType
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate-survivor-cache-predicate-transfer"


class SurvivorCachePredicateTransferTest(unittest.TestCase):
    def test_current_checkpoint(self):
        module = ModuleType("cache_predicate_transfer")
        SourceFileLoader(module.__name__, str(SCRIPT)).exec_module(module)
        module.validate(ROOT)


if __name__ == "__main__":
    unittest.main()
