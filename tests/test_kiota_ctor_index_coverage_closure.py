import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts/validate-kiota-ctor-index-coverage-closure"


class KiotaCtorIndexCoverageClosureTest(unittest.TestCase):
    def run_validator(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(VALIDATOR), "--root", str(root)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )

    def copy_fixture(self, destination: Path) -> None:
        paths = [
            "config/research-queue.json",
            "docs/research/KIOTA_CTOR_INDEX_TEST_PLAN.md",
            "corpus/generated/nanoda-gen-a59d7fa2cfb3-valid-ctor-index.ndjson",
            "corpus/generated/nanoda-gen-a59d7fa2cfb3-valid-control.ndjson",
            "results/research/semantic-import-contract-1/kiota-source.tar.gz",
            "results/research/semantic-import-contract-1/source-lock.json",
        ]
        for relative in paths:
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, target)
        shutil.copytree(
            ROOT / "results/research/kiota-ctor-index-coverage-1",
            destination / "results/research/kiota-ctor-index-coverage-1",
        )

    def test_live_closure_passes(self) -> None:
        completed = self.run_validator(ROOT)
        self.assertEqual(completed.returncode, 0, completed.stdout)
        self.assertEqual(completed.stdout.strip(), "PASS")

    def test_changed_coverage_decision_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.copy_fixture(root)
            path = root / "results/research/kiota-ctor-index-coverage-1/coverage-map.json"
            value = json.loads(path.read_text())
            value["decision"] = "EQUIVALENT_COVERAGE_NO_VALUE"
            path.write_text(json.dumps(value, indent=2) + "\n")
            completed = self.run_validator(root)
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("coverage decision changed", completed.stdout)


if __name__ == "__main__":
    unittest.main()
