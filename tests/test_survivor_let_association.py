import copy
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lib import survivor_let_association as association


class SurvivorLetAssociationTests(unittest.TestCase):
    def test_render_appends_one_classification_and_no_corpus_output(self):
        outputs = association.render(ROOT)
        self.assertEqual(outputs[association.REGISTRY].count("\n"), 607)
        self.assertEqual(
            set(outputs),
            {
                association.ASSOCIATION,
                association.CONFIRMATION,
                association.TRANSITION,
                association.RESULT,
                association.REPORT,
                association.EVIDENCE_MANIFEST,
                association.REGISTRY,
            },
        )
        self.assertFalse(any(path.startswith("corpus/") for path in outputs))
        row = json.loads(outputs[association.REGISTRY].splitlines()[-1])
        self.assertEqual(
            (row["id"], row["status"], row["classification"]),
            (association.MUTANT, "KILLED", "MEANINGFUL_SEMANTIC"),
        )
        rendered = json.loads(outputs[association.ASSOCIATION])
        self.assertTrue(rendered["no_duplicate_corpus_artifact"])
        self.assertFalse(rendered["declaration_validation"]["normative_source_change"])

    def test_historical_transition_executes_unchanged_admission_producer(self):
        result = association.validate_historical_admission(ROOT)
        self.assertEqual(result["status"], "PASS")
        self.assertTrue(result["old_admission_outputs_verified"])

    def test_input_drift_is_refused_but_future_successor_state_is_allowed(self):
        frozen = copy.deepcopy(association.FROZEN)
        try:
            association.FROZEN[association.PAIR["candidate"]] = (601, "0" * 64)
            with self.assertRaisesRegex(ValueError, "frozen association input changed"):
                association.render(ROOT)
        finally:
            association.FROZEN.clear()
            association.FROZEN.update(frozen)

        registry = ROOT / association.REGISTRY
        original = registry.read_text(encoding="utf-8")
        extra = original + "{}\n"
        read_text = Path.read_text
        with patch.object(
            Path,
            "read_text",
            autospec=True,
            side_effect=lambda path, *args, **kwargs: (
                extra if path == registry else read_text(path, *args, **kwargs)
            ),
        ):
            association.check(ROOT)

        inventory = ROOT / association.INVENTORY
        read_bytes = Path.read_bytes
        with patch.object(
            Path,
            "read_bytes",
            autospec=True,
            side_effect=lambda path, *args, **kwargs: (
                b"future inventory\n"
                if path == inventory
                else read_bytes(path, *args, **kwargs)
            ),
        ):
            association.check(ROOT)

        with patch.object(
            Path,
            "read_text",
            autospec=True,
            side_effect=lambda path, *args, **kwargs: (
                "{}\n" + original if path == registry else read_text(path, *args, **kwargs)
            ),
        ):
            with self.assertRaisesRegex(ValueError, "historical registry predecessor"):
                association.check(ROOT)


if __name__ == "__main__":
    unittest.main()
