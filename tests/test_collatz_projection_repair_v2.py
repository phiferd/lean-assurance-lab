import importlib.machinery
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "collatz-retrospective-projection-repair-v2"


def load_repair_module():
    loader = importlib.machinery.SourceFileLoader("collatz_projection_repair_v2_test", str(SCRIPT))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


REPAIR = load_repair_module()


class BoundedProjectionMutationTests(unittest.TestCase):
    def make_seed(self, directory: Path) -> Path:
        records = [
            {
                "inductive": {
                    "types": [
                        {"name": 10, "ctors": [100]},
                        {"name": 20, "ctors": [200]},
                        {"name": 30, "ctors": [300]},
                    ],
                    "ctors": [
                        {"induct": 10, "numFields": 2},
                        {"induct": 20, "numFields": 2},
                        {"induct": 30, "numFields": 1},
                    ],
                }
            },
            {"proj": {"typeName": 10, "idx": 0, "structure": 1}},
            {"proj": {"typeName": 20, "idx": 1, "structure": 2}},
        ]
        path = directory / "seed.ndjson"
        path.write_text("".join(json.dumps(row) + "\n" for row in records), encoding="utf-8")
        return path

    def test_lazy_order_matches_frozen_eager_generator(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "corpus") as temp_name:
            seed = self.make_seed(Path(temp_name))
            eager = REPAIR.FROZEN.projection_mutations([seed], 20260824)
            lazy = list(REPAIR.iter_bounded_projection_mutations([seed], 20260824, 64))

        self.assertEqual(lazy, eager)

    def test_lazy_limit_matches_prefix_of_frozen_generator(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "corpus") as temp_name:
            seed = self.make_seed(Path(temp_name))
            eager = REPAIR.FROZEN.projection_mutations([seed], 17)
            lazy = list(REPAIR.iter_bounded_projection_mutations([seed], 17, 2))

        self.assertEqual(lazy, eager[:2])


if __name__ == "__main__":
    unittest.main()
