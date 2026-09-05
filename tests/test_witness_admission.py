import copy
import importlib.machinery
import importlib.util
import unittest
from unittest.mock import patch
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader("witness_admission", str(ROOT / "scripts" / "build-witness-admission"))
spec = importlib.util.spec_from_loader(loader.name, loader)
admission = importlib.util.module_from_spec(spec)
loader.exec_module(admission)


class WitnessAdmissionTests(unittest.TestCase):
    def clone_safe_build(self):
        """Triage raw observations are tracked; payload binaries are optional in CI."""
        real_verify = admission.verify

        def verify_without_optional_payload(row):
            if row["path"].startswith("external/"):
                return
            real_verify(row)

        with patch.object(admission, "verify", side_effect=verify_without_optional_payload):
            return admission.build()

    def test_fixed_evidence_renders_two_successors_without_launching_processes(self):
        with patch("subprocess.run", side_effect=AssertionError("admission must not launch a process")):
            outputs = self.clone_safe_build()
        self.assertIn("corpus/augmented/manifest-v2.json", outputs)
        self.assertIn(admission.REGISTRY, outputs)
        self.assertEqual(outputs[admission.REGISTRY].count("\n"), admission.PREDECESSOR_REGISTRY_LINES + 2)
        manifest = admission.json.loads(outputs["corpus/augmented/manifest-v2.json"])
        self.assertEqual(manifest["schema_version"], 2)
        self.assertEqual(len(manifest["tests"]), 3)
        for mutant_id in admission.IDS:
            row = admission.json.loads(outputs[admission.REGISTRY].splitlines()[admission.PREDECESSOR_REGISTRY_LINES + admission.IDS.index(mutant_id)])
            self.assertEqual((row["id"], row["status"], row["classification"]), (mutant_id, "KILLED", "MEANINGFUL_SEMANTIC"))
            self.assertIn("updated_at", row)
            self.assertNotIn("recorded_at", row)
        metadata = admission.json.loads(outputs["results/witnesses/nanoda-gen-f19ffc8a2e9b-witness/metadata.json"])
        self.assertEqual(metadata["search_status"], "WITNESS_FOUND")
        self.assertEqual(metadata["semantic_status"], "UNRESOLVED")
        self.assertEqual(metadata["profile_status"], "CONFIRMED_OFFICIAL_PROFILE_OUTCOME")
        self.assertEqual(metadata["minimization_status"], "NOT_RUN")

    def test_forged_outcome_is_refused_from_raw_bytes(self):
        real_read = admission.read

        def forged(path):
            value = real_read(path)
            if path.endswith("nanoda-gen-f19ffc8a2e9b/result.json"):
                value = copy.deepcopy(value)
                value["observations"][1]["baseline"]["outcome"] = "ACCEPT"
            return value

        real_verify = admission.verify
        with patch.object(admission, "read", side_effect=forged), patch.object(admission, "verify", side_effect=lambda row: None if row["path"].startswith("external/") else real_verify(row)):
            with self.assertRaisesRegex(ValueError, "outcome does not match"):
                admission.build()

    def test_changed_registry_is_not_accepted_as_a_predecessor(self):
        registry = ROOT / admission.REGISTRY
        original = registry.read_text(encoding="utf-8")
        real_read_text = Path.read_text
        with patch.object(Path, "read_text", autospec=True, side_effect=lambda path, *args, **kwargs: "{}\n" + original if path == registry else real_read_text(path, *args, **kwargs)):
            with self.assertRaisesRegex(ValueError, "registry is not"):
                self.clone_safe_build()


if __name__ == "__main__":
    unittest.main()
