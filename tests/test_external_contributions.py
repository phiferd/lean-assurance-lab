import copy
import importlib.machinery
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader(
    "external_contributions", str(ROOT / "scripts" / "build-external-contributions")
)
spec = importlib.util.spec_from_loader(loader.name, loader)
external_contributions = importlib.util.module_from_spec(spec)
loader.exec_module(external_contributions)


class ExternalContributionTests(unittest.TestCase):
    def test_actual_ledger_validates_and_view_is_current(self):
        ledger = external_contributions.load_and_validate()
        rendered = external_contributions.render(ledger)
        self.assertEqual(
            (ROOT / "docs" / "EXTERNAL_CONTRIBUTIONS.md").read_text(encoding="utf-8"),
            rendered,
        )
        self.assertEqual(len(ledger["contributions"]), 6)

    def test_current_index_includes_open_merged_and_local_draft_states(self):
        ledger = external_contributions.load_and_validate()
        states = {
            row["upstream"]["state"] if row["upstream"] else row["lifecycle"]
            for row in ledger["contributions"]
        }
        self.assertEqual(states, {"OPEN", "MERGED", "LOCAL_DRAFT"})
        cache = next(
            row
            for row in ledger["contributions"]
            if row["id"] == "NANODA-CACHE-REGRESSION-PR-DRAFT"
        )
        self.assertTrue(cache["next_step"]["requires_fresh_preflight"])
        self.assertTrue(cache["next_step"]["requires_human_authorization"])
        self.assertIsNone(cache["upstream"])

    def test_duplicate_external_reference_is_rejected(self):
        ledger = json.loads(external_contributions.LEDGER.read_text(encoding="utf-8"))
        duplicate = copy.deepcopy(ledger["contributions"][0])
        duplicate["id"] = "DUPLICATE-ENTRY"
        ledger["contributions"].append(duplicate)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ledger.json"
            path.write_text(json.dumps(ledger), encoding="utf-8")
            with mock.patch.object(external_contributions, "LEDGER", path):
                with self.assertRaisesRegex(ValueError, "duplicate external contribution"):
                    external_contributions.load_and_validate()

    def test_generator_is_explicitly_offline(self):
        ledger = external_contributions.load_and_validate()
        self.assertFalse(ledger["status_policy"]["network_refresh_is_automatic"])
        self.assertIn("performs no network requests", external_contributions.render(ledger))

    def test_all_convention_named_pull_request_drafts_are_indexed(self):
        ledger = external_contributions.load_and_validate()
        tracked = {
            row["submission_material"]
            for row in ledger["contributions"]
            if row["submission_material"]
        }
        drafts = {
            str(path.relative_to(ROOT))
            for path in (ROOT / "results" / "action-recommendations" / "drafts").glob("*-pr.md")
        }
        self.assertLessEqual(drafts, tracked)


if __name__ == "__main__":
    unittest.main()
