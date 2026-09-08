"""Planning assurance checks use file copies only; no fixture/checker process."""
import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from lib.research_queue_v2 import validate_queue
from lib.survivor_proposal import BASE, ROOT, SELECTED, HISTORICAL_CLASSIFICATION_INPUTS, binding, validate


class SurvivorProposalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.seed_temp = tempfile.TemporaryDirectory()
        cls.seed = Path(cls.seed_temp.name)
        cls.manifest = json.loads((ROOT / BASE / "evidence-manifest.json").read_text())
        paths = {r["path"] for r in cls.manifest["inputs"]}
        paths.update(str(p.relative_to(ROOT)) for p in (ROOT / BASE).glob("*.json"))
        work = json.loads((ROOT / BASE / "work-record.json").read_text())
        paths.update(r["snapshot"] for r in work["entry_bindings"])
        paths.add("results/assurance/current.json")
        paths.add("config/research-queue.json")
        paths.update(HISTORICAL_CLASSIFICATION_INPUTS)
        paths.add("config/authorized-runs/triage.json")
        review = json.loads((ROOT / BASE / "source-review.json").read_text())
        observations = json.loads((ROOT / review["prior_observations"]["path"]).read_text())
        paths.update(row[observer]["artifact"]["path"] for row in observations
                     for observer in ("baseline", "mutant"))
        for name in paths:
            dest = cls.seed / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, dest)

    @classmethod
    def tearDownClass(cls):
        cls.seed_temp.cleanup()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        shutil.copytree(self.seed, self.root, dirs_exist_ok=True)

    def tearDown(self):
        self.temp.cleanup()

    def read(self, name):
        return json.loads((self.root / BASE / (name + ".json")).read_text())

    def write(self, name, value):
        (self.root / BASE / (name + ".json")).write_text(json.dumps(value))

    def test_portable_proposal_needs_no_ignored_binary_or_execution(self):
        self.assertFalse((self.root / "external").exists())
        result = validate(self.root)
        self.assertEqual(result["selected_mutant"], SELECTED)
        self.assertIs(result["execution_authorized"], False)
        self.assertEqual(result["checker_launches"], 0)

    def test_missing_unknown_or_malformed_fields_are_refused(self):
        original = self.read("execution-proposal")
        for changed in ({k: v for k, v in original.items() if k != "limits"},
                        {**original, "command": ["run-science"]},
                        {**original, "limits": []}):
            with self.subTest(changed=changed.get("limits")):
                self.write("execution-proposal", changed)
                with self.assertRaises(ValueError):
                    validate(self.root)

    def test_widened_limits_or_scientific_materialization_are_refused(self):
        original = self.read("execution-proposal")
        for field in original["limits"]:
            changed = copy.deepcopy(original)
            changed["limits"][field] += 1
            self.write("execution-proposal", changed)
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "limits"):
                validate(self.root)
        changed = copy.deepcopy(original)
        changed["scientific_variant_scope"]["fixed_mutant_source_materializations"] = 2
        self.write("execution-proposal", changed)
        with self.assertRaisesRegex(ValueError, "one future"):
            validate(self.root)

    def test_authorization_or_alias_binary_cannot_be_inferred(self):
        original = self.read("execution-proposal")
        for field, value in (("execution_authorized", True), ("launch_ready", True),
                             ("selected_binary", {"mutant_id": "nanoda-gen-21ef4d1d32a1"})):
            changed = copy.deepcopy(original)
            changed[field] = value
            self.write("execution-proposal", changed)
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "nonexecutable"):
                validate(self.root)

    def test_alias_observation_cannot_become_selected_result(self):
        review = self.read("source-review")
        review["selected_on_reused_pair"] = "ACCEPT"
        self.write("source-review", review)
        with self.assertRaisesRegex(ValueError, "alias outcome attribution"):
            validate(self.root)

    def test_candidate_cannot_precede_controls_or_add_observer(self):
        proposal = self.read("execution-proposal")
        proposal["matrix"][0], proposal["matrix"][2] = proposal["matrix"][2], proposal["matrix"][0]
        self.write("execution-proposal", proposal)
        with self.assertRaisesRegex(ValueError, "controls-first"):
            validate(self.root)

    def test_prelaunch_gate_cannot_disappear_or_claim_approval(self):
        original = self.read("execution-proposal")
        for gates in (original["prelaunch_gates"][:-1],
                      [{**g, "approved": True} for g in original["prelaunch_gates"]]):
            changed = copy.deepcopy(original)
            changed["prelaunch_gates"] = gates
            self.write("execution-proposal", changed)
            with self.assertRaisesRegex(ValueError, "seven prelaunch"):
                validate(self.root)

    def test_inventory_cannot_hide_alternative_or_change_old_schedule(self):
        original = self.read("inventory")
        changed = copy.deepcopy(original)
        changed["entries"].pop()
        self.write("inventory", changed)
        with self.assertRaisesRegex(ValueError, "seven distinct"):
            validate(self.root)
        changed = copy.deepcopy(original)
        changed["entries"][1]["covering_tests_executed"] = 1
        self.write("inventory", changed)
        with self.assertRaisesRegex(ValueError, "projection"):
            validate(self.root)

    def test_exact_source_or_reused_export_input_drift_is_refused(self):
        for name in (BASE + "/evidence/pinned-nanoda/src/tc.rs",
                     "corpus/generated/nanoda-gen-21ef4d1d32a1-let-value-type-mismatch.ndjson"):
            path = self.root / name
            old = path.read_bytes()
            path.write_bytes(old + b"\n")
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, "input drift"):
                validate(self.root)
            path.write_bytes(old)

    def test_extra_unbound_rust_source_is_refused(self):
        (self.root / BASE / "evidence/pinned-nanoda/src/unreviewed.rs").write_text("// unrelated\n")
        with self.assertRaisesRegex(ValueError, "source inventory"):
            validate(self.root)

    def test_planning_cannot_promote_classification(self):
        path = self.root / "results/assurance/current.json"
        value = json.loads(path.read_text())
        value["mutation_testing"]["pending_survivor_triage"]["count"] = 6
        path.write_text(json.dumps(value))
        with self.assertRaisesRegex(ValueError, "canonical mutation classification"):
            validate(self.root)

    def test_authorized_future_state_does_not_reinterpret_historical_proposal(self):
        path = self.root / "results/assurance/current.json"
        value = json.loads(path.read_text())
        value["mutation_testing"]["pending_survivor_triage"]["count"] = 6
        path.write_text(json.dumps(value))
        for name in HISTORICAL_CLASSIFICATION_INPUTS:
            (self.root / name).write_text("a later separately authorized classification record\n")
        queue_path = self.root / "config/research-queue.json"
        queue = json.loads(queue_path.read_text())
        queue["frontier_id"] = "F-FUTURE-AUTHORIZED-SUCCESSOR"
        queue_path.write_text(json.dumps(queue))
        self.assertEqual(validate(self.root)["status"], "PASS")

    def test_result_cannot_claim_scientific_work_or_a_second_completed_item(self):
        original = self.read("result")
        variants = []
        changed = copy.deepcopy(original)
        changed["research_counts"]["checker_launches"] = 1
        variants.append(changed)
        changed = copy.deepcopy(original)
        changed["assurance_changes"]["classifications_changed"] = 1
        variants.append(changed)
        changed = copy.deepcopy(original)
        changed["completed_items"].append("SURVIVOR-LET-REUSE-1")
        variants.append(changed)
        changed = copy.deepcopy(original)
        changed["scientific_status"] = "WITNESS_FOUND"
        variants.append(changed)
        for changed in variants:
            self.write("result", changed)
            with self.subTest(result=changed), self.assertRaises(ValueError):
                validate(self.root)

    def test_required_historical_binding_cannot_be_omitted(self):
        evidence = self.read("evidence-manifest")
        evidence["inputs"] = [r for r in evidence["inputs"] if r["path"] != "config/authorized-runs/triage.json"]
        self.write("evidence-manifest", evidence)
        with self.assertRaisesRegex(ValueError, "required historical/tooling"):
            validate(self.root)

    def test_entry_transition_retains_valid_paused_queue_and_cvc5_bindings(self):
        entry = self.read("entry-decision")
        before = json.loads((self.root / entry["before_queue"]).read_text())
        refs = {before["plan"], *before["handoff"]["evidence_refs"]}
        for item in before["items"]:
            refs.update(item["evidence_refs"])
            if item["closure"]:
                refs.update(item["closure"]["evidence_refs"])
        # Real referenced bytes in a temporary repository view, plus archived
        # status. No current status/selection is substituted into old evidence.
        for name in refs:
            dest = self.root / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, dest)
        status = self.root / "docs/RESEARCH_STATUS.md"
        status.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(self.root / BASE / "entry-snapshot/docs/RESEARCH_STATUS.md", status)
        validate_queue(before, self.root)
        with self.assertRaisesRegex(ValueError, "queue is PAUSED"):
            validate_queue(before, self.root, require_ready=True)
        current = json.loads((ROOT / "config/research-queue.json").read_text())
        self.assertNotEqual(current, before)
        self.assertEqual(entry["retired_placeholder"], next(i for i in before["items"]
                         if i["id"] == "CVC-NEXT-AUTHORIZATION"))
        history = [r for r in self.manifest["inputs"]
                   if "/cvc-5-conditional/" in r["path"]]
        self.assertGreaterEqual(len(history), 3)
        for row in history:
            binding(ROOT, row)
            binding(self.root, row)


if __name__ == "__main__":
    unittest.main()
