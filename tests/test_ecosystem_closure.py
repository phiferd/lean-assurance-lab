import copy
import hashlib
import importlib.machinery
import importlib.util
import unittest
from unittest.mock import patch
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader(
    "ecosystem_closure", str(ROOT / "scripts" / "build-ecosystem-closure")
)
spec = importlib.util.spec_from_loader(loader.name, loader)
closure = importlib.util.module_from_spec(spec)
loader.exec_module(closure)


class EcosystemClosureTests(unittest.TestCase):
    def observation(self):
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        rows = {}
        for name, data in {
            "binary": b"fixture binary", "artifact": b"fixture artifact",
            "stdout": b"", "stderr": b"",
        }.items():
            path = root / name
            path.write_bytes(data)
            rows[name] = {"path": name, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
        return temporary, {"checker": "kiota", "exit_code": 0, "outcome": "ACCEPT", **rows}

    def test_corrupted_raw_binding_is_refused(self):
        temporary, row = self.observation()
        with temporary, patch.object(closure, "ROOT", Path(temporary.name)):
            row["stdout"]["sha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "evidence changed"):
                closure.validate_observation(row)

    def test_forged_outcome_is_refused_from_bound_raw_evidence(self):
        temporary, row = self.observation()
        with temporary, patch.object(closure, "ROOT", Path(temporary.name)):
            row["outcome"] = "REJECT"
            with self.assertRaisesRegex(ValueError, "outcome does not match"):
                closure.validate_observation(row)

    def test_budget_and_fixed_selection_are_enforced(self):
        actual_read = closure.read

        def changed_budget(path):
            value = actual_read(path)
            if path == closure.BASE + "/triage/results.json":
                value = copy.deepcopy(value)
                value["cases"][0]["budget"]["seconds"] = 121
            return value

        original_verify = closure.verify

        def verify_without_external_binary(row):
            if row["path"].startswith("external/"):
                return
            original_verify(row)

        with patch.object(closure, "read", side_effect=changed_budget), patch.object(closure, "verify", side_effect=verify_without_external_binary):
            with self.assertRaisesRegex(ValueError, "triage bounds failed"):
                closure.build()

        def changed_selection(path):
            value = actual_read(path)
            if path == closure.BASE + "/triage/results.json":
                value = copy.deepcopy(value)
                value["cases"].reverse()
            return value

        with patch.object(closure, "read", side_effect=changed_selection), patch.object(closure, "verify", side_effect=verify_without_external_binary):
            with self.assertRaisesRegex(ValueError, "triage selection changed"):
                closure.build()


if __name__ == "__main__":
    unittest.main()
