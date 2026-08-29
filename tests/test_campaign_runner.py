import importlib.machinery
import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run-campaign"
loader = importlib.machinery.SourceFileLoader("campaign_runner", str(SCRIPT))
spec = importlib.util.spec_from_loader(loader.name, loader)
module = importlib.util.module_from_spec(spec)
loader.exec_module(module)


MANIFEST = {
    "source_sha256": "a" * 64,
    "mutation_model_sha256": "b" * 64,
    "coverage_manifest_sha256": "c" * 64,
    "mutants": [{"id": "mutant-a", "identity": "one"}, {"id": "mutant-b", "identity": "two"}],
}


class CampaignRunnerTests(unittest.TestCase):
    def test_binding_ignores_mutable_execution_evidence(self):
        with_evidence = dict(MANIFEST)
        with_evidence["execution"] = {"status": "COMPLETE"}
        self.assertEqual(module.batch_binding("batch", MANIFEST), module.batch_binding("batch", with_evidence))

    def test_reconcile_interruption_keeps_completed_phases(self):
        campaign = module.make_campaign("campaign", "batch", module.batch_binding("batch", MANIFEST))
        campaign["phases"]["build_validation"]["status"] = "COMPLETE"
        campaign["phases"]["execution"]["status"] = "RUNNING"
        module.reconcile_interruption(campaign)
        self.assertEqual(campaign["phases"]["build_validation"]["status"], "COMPLETE")
        self.assertEqual(campaign["phases"]["execution"]["status"], "INTERRUPTED")
        self.assertIn("interrupted_at", campaign["phases"]["execution"])

    def test_phase_commands_are_bounded_to_existing_mechanical_steps(self):
        self.assertEqual(module.command_for("build_validation", "batch")[-1], "--resume")
        self.assertEqual(module.command_for("execution", "batch")[-1], "--resume")
        self.assertTrue(module.command_for("assurance", "batch")[0].endswith("current-assurance-snapshot"))

    def test_reconciliation_adopts_completed_batch_work(self):
        campaign = module.make_campaign("campaign", "batch", module.batch_binding("batch", MANIFEST))
        completed = dict(MANIFEST)
        completed["build_validation"] = {"status": "COMPLETE", "results": [{}, {}]}
        completed["execution"] = {"status": "COMPLETE", "results": [{}, {}]}
        module.reconcile_completed_phases(campaign, completed)
        self.assertEqual(campaign["phases"]["build_validation"]["status"], "COMPLETE")
        self.assertEqual(campaign["phases"]["execution"]["status"], "COMPLETE")


if __name__ == "__main__":
    unittest.main()
