"""Disjoint launch-gate regressions; never render selected inputs or run a checker."""

import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from lib import resource_envelope_launch as launch
from lib import resource_envelope_control as control
from lib.resource_envelope_control import GateError, binding
from lib.resource_envelope_supervisor import SupervisedResult
from lib.resource_envelope_producer import canonical_json


def save(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")


class ResourceEnvelopeLaunchTests(unittest.TestCase):
    def test_observer_input_mutation_preserves_raw_and_custody_fault(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            source = base / "synthetic.ndjson"
            source.write_bytes(b"synthetic input\n")
            attempt = base / "attempt"
            attempt.mkdir()
            execution = {"invocations": {"official": [str(base / "checker"),
                                                    "{export_path}"]},
                         "environment": {},
                         "limits": {"checker": {"timeout_seconds": 2,
                                                "memory_ceiling_bytes": 4096},
                                    "sample_interval_seconds": 0.01,
                                    "max_trace_gap_seconds": 1.0,
                                    "cleanup_seconds": 2.0,
                                    "ps_timeout_seconds": 0.5,
                                    "output_cap_bytes": 1000}}
            with patch.object(control, "ROOT", base), \
                 patch.multiple(launch, ROOT=base, BASE=base, OFFICIAL_BINARY="checker"):
                frozen = binding(source)
                def mutate(**_kwargs):
                    source.write_bytes(b"changed input\n")
                    return SupervisedResult(receipt={"stdin_bytes": None},
                                            stdout=b"raw observer output", stderr=b"")
                with patch.object(launch, "run_direct", side_effect=mutate):
                    with self.assertRaisesRegex(GateError, "input custody differs"):
                        launch._profile_run(attempt=attempt, label="synthetic", profile="official",
                                            export_path=source, expected=b"ignored",
                                            expected_binding=frozen, execution=execution,
                                            baseline=False)
                self.assertEqual((attempt / "processes/synthetic.stdout").read_bytes(),
                                 b"raw observer output")
                fault = json.loads((attempt / "processes/synthetic.custody-failure.json").read_text())
                self.assertEqual(fault["status"], "INPUT_CUSTODY_REPAIR_PAUSE")
                self.assertEqual(fault["expected_input"], frozen)
                self.assertIsNotNone(fault["process"])
                source.write_bytes(b"synthetic input\n")
                nano_attempt = base / "nano-attempt"
                nano_attempt.mkdir()
                execution["invocations"]["nanoda"] = [str(base / "nano"),
                                                       str(base / "nanoda-single-check.json")]
                with patch.object(launch, "NANODA_BINARY", "nano"), \
                     patch.object(launch, "run_direct",
                                  return_value=SupervisedResult(
                                      receipt={"stdin_bytes": len(source.read_bytes()),
                                               "stdin_sha256": "wrong"},
                                      stdout=b"nano raw", stderr=b"")):
                    with self.assertRaisesRegex(GateError, "Nanoda stdin"):
                        launch._profile_run(attempt=nano_attempt, label="synthetic-nano",
                                            profile="nanoda", export_path=source,
                                            expected=b"ignored", expected_binding=binding(source),
                                            execution=execution, baseline=False)
                self.assertEqual((nano_attempt / "processes/synthetic-nano.stdout").read_bytes(),
                                 b"nano raw")
                failed_attempt = base / "spawn-attempt"
                failed_attempt.mkdir()
                with patch.object(launch, "run_direct", side_effect=OSError("synthetic spawn")):
                    with self.assertRaisesRegex(GateError, "observer launch failed"):
                        launch._profile_run(attempt=failed_attempt, label="synthetic-spawn",
                                            profile="official", export_path=source,
                                            expected=b"ignored", expected_binding=binding(source),
                                            execution=execution, baseline=False)
                failed = json.loads((failed_attempt / "processes/synthetic-spawn.launch-failure.json").read_text())
                self.assertEqual(failed["status"], "OBSERVER_LAUNCH_REPAIR_PAUSE")
                self.assertEqual(failed["input"], binding(source))

    def test_smoke_gate_rejects_stale_review_and_changed_profile(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            science, execution_path = base / "science.json", base / "execution.json"
            contract, inp = base / "smoke-fixture-contract.json", base / "synthetic.ndjson"
            manifest, review = base / "smoke.json", base / "review.json"
            preflight = base / "independent-preflight-review.json"
            for path in (science, execution_path, preflight):
                save(path, {})
            inp.write_bytes(b'{"synthetic":true}\n')
            fixture = {"input": binding(inp), "expected_outputs":
                       {"official": "fixture-official\n", "nanoda": "fixture-nanoda\n"}}
            save(contract, fixture)
            checker_limits = {"timeout_seconds": 2, "memory_ceiling_bytes": 4096}
            execution = {"limits": {"checker": checker_limits},
                         "invocations": {"official": ["/synthetic/official", "{export_path}"],
                                         "nanoda": ["/synthetic/nanoda"]}}
            profile_rows = [
                {"id": name, "expected_stdout": fixture["expected_outputs"][name],
                 "expected_stderr": "", "limits": checker_limits,
                 "invocation": execution["invocations"][name]}
                for name in ("official", "nanoda")]
            row = {"status": "FROZEN_BEFORE_SMOKE_LAUNCH",
                   "scientific_manifest": binding(science),
                   "execution_manifest": binding(execution_path),
                   "fixture_contract": binding(contract), "input": binding(inp),
                   "preflight_review": binding(preflight), "profiles": profile_rows}
            with patch.object(control, "ROOT", base), \
                 patch.multiple(launch, ROOT=base, BASE=base, SCIENCE=science,
                                EXECUTION=execution_path, SMOKE_MANIFEST=manifest,
                                SMOKE_LAUNCH_REVIEW=review), \
                 patch.object(launch, "require_construction_gate", return_value=({}, execution)), \
                 patch.object(control, "_committed"), \
                 patch.object(launch, "_committed"):
                fixture["input"] = binding(inp)
                save(contract, fixture)
                row.update(scientific_manifest=binding(science),
                           execution_manifest=binding(execution_path),
                           fixture_contract=binding(contract),
                           preflight_review=binding(preflight), input=binding(inp))
                save(manifest, row)
                save(review, {"verdict": "PASS_FOR_SMOKE_LAUNCH",
                              "smoke_manifest_sha256": "stale",
                              "execution_manifest_sha256": binding(execution_path)["sha256"]})
                with self.assertRaisesRegex(GateError, "smoke launch review"):
                    launch.require_smoke_gate()
                saved_review = json.loads(review.read_text())
                saved_review["smoke_manifest_sha256"] = binding(manifest)["sha256"]
                save(review, saved_review)
                self.assertEqual(launch.require_smoke_gate()[0], row)
                row["profiles"][0]["expected_stdout"] = "unreviewed-output\n"
                save(manifest, row)
                with self.assertRaisesRegex(GateError, "profile contract"):
                    launch.require_smoke_gate()

    def test_corpus_lock_detects_file_mutation(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            corpus = base / "corpus"
            corpus.mkdir()
            indexed = corpus / "index.json"
            indexed.write_bytes(b'{"synthetic":1}\n')
            construction = base / "construction-run-0001" / "construction-result.json"
            review = base / "independent-corpus-review.json"
            science, execution = base / "science.json", base / "execution.json"
            for path in (construction, science, execution):
                save(path, {})
            save(review, {"verdict": "PASS_FOR_CORPUS_SEALING",
                          "corpus_index_sha256": binding(indexed)["sha256"],
                          "construction_result_sha256": binding(construction)["sha256"]})
            audit = {"status": "PASS", "count": 12}
            with patch.object(control, "ROOT", base), \
                 patch.multiple(launch, ROOT=base, BASE=base, CORPUS=corpus,
                                CORPUS_LOCK=base / "corpus-lock.json",
                                CORPUS_REVIEW=review, SCIENCE=science, EXECUTION=execution), \
                 patch.object(launch, "require_construction_gate"), \
                 patch.object(launch, "audit_corpus", return_value=audit), \
                 patch.object(control, "_committed"), \
                 patch.object(launch, "_committed"):
                launch.seal_corpus()
                launch.require_corpus_lock()
                indexed.write_bytes(b'{"synthetic":2}\n')
                with self.assertRaisesRegex(GateError, "bound file changed"):
                    launch.require_corpus_lock()

    def test_scientific_gate_replays_committed_smoke_raw(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            fixture = base / "synthetic-fixture.ndjson"
            fixture.write_bytes(b"synthetic fixture\n")
            manifest = base / "smoke-manifest.json"
            science, execution, lock = (base / name for name in
                                        ("science.json", "execution.json", "corpus-lock.json"))
            result_path, attempt_path = base / "smoke-result.json", base / "smoke-attempt.json"
            result_review, prelaunch = base / "smoke-review.json", base / "prelaunch.json"
            for path in (science, execution, lock):
                save(path, {})
            limits = {"checker": {"timeout_seconds": 2,
                                  "memory_ceiling_bytes": 4096},
                      "sample_interval_seconds": 0.01,
                      "max_trace_gap_seconds": 1.0, "cleanup_seconds": 2.0,
                      "ps_timeout_seconds": 0.5, "output_cap_bytes": 1000}
            execution_data = {"invocations": {
                "official": [str(base / "official"), "{export_path}"],
                "nanoda": [str(base / "nanoda"), str(base / "nanoda-single-check.json")]},
                "limits": limits}
            with patch.object(control, "ROOT", base), \
                 patch.multiple(launch, ROOT=base, BASE=base, SCIENCE=science,
                                EXECUTION=execution, CORPUS_LOCK=lock,
                                SMOKE_MANIFEST=manifest, SMOKE_RESULT=result_path,
                                SMOKE_RESULT_REVIEW=result_review,
                                PRELAUNCH_REVIEW=prelaunch), \
                 patch.object(control, "_committed"), \
                 patch.object(launch, "_committed"), \
                 patch.object(launch, "require_construction_gate",
                              return_value=({}, execution_data)), \
                 patch.object(launch, "require_corpus_lock", return_value={}), \
                 patch.object(launch, "require_smoke_gate") as smoke_gate, \
                 patch.object(launch, "classify", return_value={"status": "ACCEPTED"}):
                input_ref = binding(fixture)
                smoke_gate.return_value = ({"input": input_ref}, execution_data)
                profiles = []
                for profile in ("official", "nanoda"):
                    directory = base / profile
                    directory.mkdir()
                    stdout = directory / "stdout.raw"
                    stderr = directory / "stderr.raw"
                    receipt = directory / "receipt.json"
                    stdout.write_bytes(b"synthetic accepted\n")
                    stderr.write_bytes(b"")
                    save(receipt, {"raw_stdout_path": stdout.relative_to(base).as_posix(),
                                   "raw_stderr_path": stderr.relative_to(base).as_posix(),
                                   "argv": [arg.replace("{export_path}", str(fixture))
                                            for arg in execution_data["invocations"][profile]],
                                   "cwd": str(base),
                                   "limits": {**limits["checker"],
                                              **{name: limits[name] for name in (
                                                  "sample_interval_seconds", "max_trace_gap_seconds",
                                                  "cleanup_seconds", "ps_timeout_seconds",
                                                  "output_cap_bytes")}},
                                   "started_monotonic_ns": 100,
                                   "stdin_bytes": input_ref["bytes"] if profile == "nanoda" else None,
                                   "stdin_sha256": input_ref["sha256"] if profile == "nanoda" else None})
                    profiles.append({"profile": profile, "input": input_ref,
                                     "disposition": {"status": "ACCEPTED"},
                                     "started_monotonic_ns": 100,
                                     "process": {"stdout": binding(stdout),
                                                 "stderr": binding(stderr),
                                                 "receipt": binding(receipt)}})
                attempt = {"status": "SMOKE_EXACT_ACCEPTANCE_BOTH_PROFILES",
                           "smoke_manifest": binding(manifest) if manifest.exists() else None,
                           "profiles": profiles}
                save(manifest, {})
                attempt["smoke_manifest"] = binding(manifest)
                save(attempt_path, attempt)
                save(result_path, {"attempt_result": binding(attempt_path), **attempt})
                save(result_review, {"verdict": "PASS_EXACT_SMOKE_RESULTS",
                                     "smoke_result_sha256": binding(result_path)["sha256"]})
                save(prelaunch, {"verdict": "PASS_FOR_SCIENTIFIC_LAUNCH",
                                 "scientific_manifest_sha256": binding(science)["sha256"],
                                 "execution_manifest_sha256": binding(execution)["sha256"],
                                 "corpus_lock_sha256": binding(lock)["sha256"],
                                 "smoke_result_sha256": binding(result_path)["sha256"]})
                launch.require_scientific_launch_gate()
                (base / "official/stdout.raw").write_bytes(b"changed\n")
                with self.assertRaisesRegex(GateError, "bound file changed"):
                    launch.require_scientific_launch_gate()

    def test_scientific_gate_blocks_all_observer_launches(self):
        with patch.object(launch, "require_scientific_launch_gate",
                          side_effect=GateError("missing independent review")), \
             patch.object(launch, "run_direct") as observer:
            with self.assertRaisesRegex(GateError, "missing independent review"):
                launch.run_science()
            observer.assert_not_called()

    def test_scientific_limit_pauses_before_skipping_or_later_launch(self):
        # Synthetic dispositions only: no selected term bytes and no process launch.
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            (base / "baseline-empty.ndjson").write_bytes(b"synthetic empty\n")
            seen = []

            def ref(path):
                return {"path": Path(path).relative_to(base).as_posix(),
                        "bytes": 1, "sha256": "synthetic"}

            def observed(*, label, profile, export_path, **_kwargs):
                seen.append(label)
                status = ("OBSERVED_TIME_LIMIT" if label == "official-rep1-pi-016"
                          else "ACCEPTED")
                return {"profile": profile, "input": ref(export_path),
                        "process": {"synthetic": True},
                        "disposition": {"status": status, "reason": "synthetic"}}

            execution = {"empty_export": {"sha256": "synthetic", "bytes": 1}}
            locked = {"files": [ref(base / "corpus" / "exports" / f"rep1-{family}-{size:03d}.ndjson")
                                for family in ("pi", "let") for size in (16, 32, 64, 128, 256, 512)]}
            with patch.multiple(launch, ROOT=base, BASE=base, CORPUS=base / "corpus",
                                SCIENCE=base / "science.json",
                                EXECUTION=base / "execution.json",
                                CORPUS_LOCK=base / "corpus-lock.json",
                                SMOKE_RESULT=base / "smoke-result.json",
                                PRELAUNCH_REVIEW=base / "prelaunch.json"), \
                 patch.object(launch, "require_scientific_launch_gate",
                              return_value=(locked, execution)), \
                 patch.object(launch, "_profile_run", side_effect=observed), \
                 patch.object(launch, "binding", side_effect=ref), \
                 patch.object(launch, "run_direct") as process:
                result = launch.run_science()
            self.assertEqual(result["status"], "AWAITING_INDEPENDENT_LIMIT_DIAGNOSIS")
            self.assertEqual(result["trigger_cell_id"], "official-rep1-pi-016")
            self.assertEqual(result["next_slot_index"], 4)
            self.assertEqual(len(result["events"]), 4)
            self.assertEqual(seen, ["official-before-01", "official-before-02",
                                    "official-before-03", "official-rep1-pi-016"])
            self.assertFalse((base / "science-run-0001/science-result.json").exists())
            self.assertTrue((base / "science-run-0001/science-pause.json").is_file())
            process.assert_not_called()
            prior = base / "science-run-0001/science-pause.json"
            with patch.multiple(launch, ROOT=base, BASE=base, CORPUS=base / "corpus",
                                SCIENCE=base / "science.json",
                                EXECUTION=base / "execution.json",
                                CORPUS_LOCK=base / "corpus-lock.json",
                                SMOKE_RESULT=base / "smoke-result.json",
                                PRELAUNCH_REVIEW=base / "prelaunch.json"), \
                 patch.object(launch, "require_scientific_launch_gate",
                              return_value=(locked, execution)), \
                 patch.object(launch, "_resume_state",
                              return_value=(result["events"],
                                            {"official/pi": "official-rep1-pi-016"},
                                            [{"synthetic_review": True}])), \
                 patch.object(launch, "_profile_run", side_effect=observed), \
                 patch.object(launch, "binding", side_effect=ref), \
                 patch.object(launch, "_verify_prefix_events"), \
                 patch.object(launch, "run_direct") as resumed_process:
                complete = launch.run_science(resume_pause=prior)
                with self.assertRaisesRegex(GateError, "completed scientific matrix"):
                    launch.run_science(resume_pause=prior)
                resumed_process.assert_not_called()
            self.assertEqual(complete["status"], "COMPLETE_FIXED_MATRIX")
            self.assertEqual((len(complete["baselines"]), len(complete["cells"])), (12, 24))
            self.assertEqual(len([row for row in complete["cells"]
                                  if row["status"] == "NOT_RUN_AFTER_LIMIT"]), 5)
            self.assertEqual(seen.count("official-rep1-pi-016"), 1)
            self.assertEqual(len(seen), 31)

    def test_baseline_and_science_control_faults_stop_immediately(self):
        for fault_id, expected_launches in (("official-before-01", 1),
                                            ("official-rep1-pi-016", 4)):
            with self.subTest(fault=fault_id), tempfile.TemporaryDirectory() as folder:
                base = Path(folder)
                (base / "baseline-empty.ndjson").write_bytes(b"synthetic empty\n")
                seen = []

                def ref(path):
                    return {"path": Path(path).relative_to(base).as_posix(),
                            "bytes": 1, "sha256": "synthetic"}

                def observed(*, attempt, label, profile, export_path, **_kwargs):
                    seen.append(label)
                    raw = attempt / "processes" / f"{label}.stdout"
                    raw.parent.mkdir(parents=True, exist_ok=True)
                    raw.write_bytes(b"preserved synthetic raw\n")
                    return {"profile": profile, "input": ref(export_path),
                            "process": {"stdout": ref(raw)},
                            "disposition": {"status": ("REPAIR_PAUSE" if label == fault_id
                                                       else "ACCEPTED"),
                                            "reason": "synthetic control fault"}}

                locked = {"files": [ref(base / "corpus/exports/rep1-pi-016.ndjson")]}
                execution = {"empty_export": {"sha256": "synthetic", "bytes": 1}}
                with patch.multiple(launch, ROOT=base, BASE=base,
                                    CORPUS=base / "corpus", SCIENCE=base / "science.json",
                                    EXECUTION=base / "execution.json",
                                    CORPUS_LOCK=base / "corpus-lock.json",
                                    SMOKE_RESULT=base / "smoke.json"), \
                     patch.object(launch, "require_scientific_launch_gate",
                                  return_value=(locked, execution)), \
                     patch.object(launch, "_profile_run", side_effect=observed), \
                     patch.object(launch, "binding", side_effect=ref), \
                     patch.object(launch, "run_direct") as process:
                    with self.assertRaisesRegex(GateError, "requires repair"):
                        launch.run_science()
                self.assertEqual(len(seen), expected_launches)
                self.assertFalse(any(name.startswith("nanoda") for name in seen))
                attempt = base / "science-run-0001"
                self.assertEqual(len((attempt / "ledger.ndjson").read_bytes().splitlines()),
                                 expected_launches)
                self.assertEqual(json.loads((attempt / "science-failure.json").read_text())["status"],
                                 "SCIENCE_REPAIR_PAUSE")
                self.assertTrue((attempt / "processes" / f"{fault_id}.stdout").is_file())
                process.assert_not_called()

    def test_resume_requires_exact_independent_limit_review(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            attempt = base / "science-run-0001"
            attempt.mkdir()
            science, execution, lock = (base / name for name in
                                        ("science.json", "execution.json", "corpus-lock.json"))
            for path in (science, execution, lock):
                save(path, {})
            baseline = base / "baseline-empty.ndjson"
            baseline.write_bytes(b"synthetic empty\n")
            export = base / "corpus/exports/rep1-pi-016.ndjson"
            export.parent.mkdir(parents=True)
            export.write_bytes(b"synthetic graph\n")
            pause_path = attempt / "science-pause.json"
            review_path = attempt / "independent-limit-review.json"
            ledger = attempt / "ledger.ndjson"
            with patch.object(control, "ROOT", base), \
                 patch.multiple(launch, ROOT=base, BASE=base, CORPUS=base / "corpus",
                                SCIENCE=science,
                                EXECUTION=execution, CORPUS_LOCK=lock), \
                 patch.object(control, "_committed"), \
                 patch.object(launch, "_committed"), \
                 patch.object(launch, "classify",
                              side_effect=lambda receipt, *_args, **_kwargs:
                              {"status": receipt["test_status"], "reason": "synthetic"}):
                schedule = launch._schedule()
                limits = {"checker": {"timeout_seconds": 2,
                                      "memory_ceiling_bytes": 4096},
                          "sample_interval_seconds": 0.01,
                          "max_trace_gap_seconds": 1.0,
                          "cleanup_seconds": 2.0,
                          "ps_timeout_seconds": 0.5,
                          "output_cap_bytes": 1000}
                runtime = {"empty_export": {"bytes": binding(baseline)["bytes"],
                                             "sha256": binding(baseline)["sha256"]},
                           "invocations": {"official": [str(base / "official"), "{export_path}"],
                                           "nanoda": [str(base / "nanoda")]},
                           "limits": limits}
                corpus_lock = {"files": [binding(export)]}
                events = []
                for number, slot in enumerate(schedule[:4]):
                    inp = baseline if slot["kind"] == "baseline" else export
                    stdout = attempt / f"{number}.stdout"
                    stderr = attempt / f"{number}.stderr"
                    receipt = attempt / f"{number}.receipt.json"
                    stdout.write_bytes(b"synthetic raw")
                    stderr.write_bytes(b"")
                    status = "ACCEPTED" if slot["kind"] == "baseline" else "OBSERVED_TIME_LIMIT"
                    save(receipt, {"argv": [str(base / "official"), str(inp)],
                                   "cwd": str(base),
                                   "limits": {**limits["checker"],
                                              **{name: limits[name] for name in
                                                 ("sample_interval_seconds", "max_trace_gap_seconds",
                                                  "cleanup_seconds", "ps_timeout_seconds",
                                                  "output_cap_bytes")}},
                                   "stdin_bytes": None, "stdin_sha256": None,
                                   "raw_stdout_path": stdout.relative_to(base).as_posix(),
                                   "raw_stderr_path": stderr.relative_to(base).as_posix(),
                                   "started_monotonic_ns": 100 + 10 * number,
                                   "drained_monotonic_ns": 105 + 10 * number,
                                   "test_status": status})
                    process = {"stdout": binding(stdout), "stderr": binding(stderr),
                               "receipt": binding(receipt)}
                    row = {"status": status, "profile": "official", "input": binding(inp),
                           "process": process, "started_monotonic_ns": 100 + 10 * number,
                           "disposition": {"status": status, "reason": "synthetic"}}
                    if slot["kind"] == "baseline":
                        row.update(baseline_id=slot["id"], phase="before")
                    else:
                        row.update(cell_id=slot["id"], family="pi", size=16)
                    events.append({"slot": slot, "row": row})
                ledger.write_bytes(b"".join(canonical_json(row) for row in events))
                pause = {"status": "AWAITING_INDEPENDENT_LIMIT_DIAGNOSIS",
                         "scientific_manifest": binding(science),
                         "execution_manifest": binding(execution),
                         "corpus_lock": binding(lock), "events": events,
                         "segment_start_index": 0, "next_slot_index": 4,
                         "trigger_cell_id": schedule[3]["id"],
                         "ledger": binding(ledger), "approved_triggers": {}, "history": []}
                save(pause_path, pause)
                review = {"verdict": "PASS_FOR_SEQUENCE_STOP",
                          "science_pause_sha256": "wrong",
                          "trigger_cell_id": schedule[3]["id"],
                          "trigger_receipt_sha256": events[-1]["row"]["process"]["receipt"]["sha256"],
                          "ledger_sha256": binding(ledger)["sha256"]}
                save(review_path, review)
                with self.assertRaisesRegex(GateError, "limit diagnosis"):
                    launch._resume_state(pause_path, schedule, corpus_lock, runtime)
                review["science_pause_sha256"] = binding(pause_path)["sha256"]
                save(review_path, review)
                resumed, triggers, history = launch._resume_state(
                    pause_path, schedule, corpus_lock, runtime)
                self.assertEqual(len(resumed), 4)
                self.assertEqual(triggers, {"official/pi": schedule[3]["id"]})
                self.assertEqual(len(history), 2)
                next_export = base / "corpus/exports/rep1-pi-032.ndjson"
                next_export.write_bytes(b"synthetic next graph\n")
                next_lock = {"files": [binding(export), binding(next_export)]}
                forged_skip = {"slot": schedule[4], "row": {
                    "cell_id": schedule[4]["id"], "profile": "official",
                    "family": "pi", "size": 32, "status": "NOT_RUN_AFTER_LIMIT",
                    "trigger_cell_id": "forged-trigger", "input": binding(next_export)}}
                with self.assertRaisesRegex(GateError, "malformed skipped cell"):
                    launch._verify_prefix_events(
                        [*events, forged_skip], schedule, next_lock, runtime,
                        {"official/pi": schedule[3]["id"]}, "later-candidate")
                first_raw = attempt / "0.stdout"
                first_raw.write_bytes(b"changed earlier accepted raw")
                with self.assertRaisesRegex(GateError, "bound file changed"):
                    launch._resume_state(pause_path, schedule, corpus_lock, runtime)
                first_raw.write_bytes(b"synthetic raw")
                events[0]["row"].pop("process")
                ledger.write_bytes(b"".join(canonical_json(row) for row in events))
                pause["events"] = events
                pause["ledger"] = binding(ledger)
                save(pause_path, pause)
                review["science_pause_sha256"] = binding(pause_path)["sha256"]
                review["ledger_sha256"] = binding(ledger)["sha256"]
                save(review_path, review)
                with self.assertRaisesRegex(GateError, "executed slot schema differs"):
                    launch._resume_state(pause_path, schedule, corpus_lock, runtime)

    def test_two_reviewed_limits_keep_smaller_accepted_sizes(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            first_dir, second_dir = base / "science-run-0001", base / "science-run-0002"
            first_dir.mkdir()
            second_dir.mkdir()
            science, execution, lock_path = (base / name for name in
                                             ("science.json", "execution.json", "corpus-lock.json"))
            for path in (science, execution, lock_path):
                save(path, {})
            baseline = base / "baseline-empty.ndjson"
            baseline.write_bytes(b"synthetic empty\n")
            sizes = (16, 32, 64, 128, 256, 512)
            exports = {}
            for family, choices in (("pi", sizes), ("let", (16,))):
                for size in choices:
                    path = base / f"corpus/exports/rep1-{family}-{size:03d}.ndjson"
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(f"synthetic {family} {size}\n".encode())
                    exports[(family, size)] = path
            limits = {"checker": {"timeout_seconds": 2, "memory_ceiling_bytes": 4096},
                      "sample_interval_seconds": 0.01, "max_trace_gap_seconds": 1.0,
                      "cleanup_seconds": 2.0, "ps_timeout_seconds": 0.5,
                      "output_cap_bytes": 1000}
            with patch.object(control, "ROOT", base), \
                 patch.multiple(launch, ROOT=base, BASE=base, CORPUS=base / "corpus",
                                SCIENCE=science, EXECUTION=execution,
                                CORPUS_LOCK=lock_path), \
                 patch.object(control, "_committed"), \
                 patch.object(launch, "_committed"), \
                 patch.object(launch, "classify",
                              side_effect=lambda receipt, *_args, **_kwargs:
                              {"status": receipt["test_status"], "reason": "synthetic"}):
                schedule = launch._schedule()
                runtime = {"empty_export": {"bytes": binding(baseline)["bytes"],
                                             "sha256": binding(baseline)["sha256"]},
                           "invocations": {"official": [str(base / "official"), "{export_path}"],
                                           "nanoda": [str(base / "nanoda")]},
                           "limits": limits}
                corpus_lock = {"files": [binding(path) for path in exports.values()]}
                events = []
                for index, slot in enumerate(schedule[:10]):
                    if slot["kind"] == "baseline":
                        inp, status = baseline, "ACCEPTED"
                    else:
                        inp = exports[(slot["family"], slot["size"])]
                        status = ("OBSERVED_TIME_LIMIT" if index in (6, 9)
                                  else "NOT_RUN_AFTER_LIMIT" if index in (7, 8)
                                  else "ACCEPTED")
                    if status == "NOT_RUN_AFTER_LIMIT":
                        row = {"cell_id": slot["id"], "profile": "official",
                               "family": "pi", "size": slot["size"],
                               "status": status, "trigger_cell_id": schedule[6]["id"],
                               "input": binding(inp)}
                    else:
                        parent = first_dir if index <= 6 else second_dir
                        stdout = parent / f"{index}.stdout"
                        stderr = parent / f"{index}.stderr"
                        receipt_path = parent / f"{index}.receipt.json"
                        stdout.write_bytes(b"synthetic raw")
                        stderr.write_bytes(b"")
                        save(receipt_path, {
                            "argv": [str(base / "official"), str(inp)], "cwd": str(base),
                            "limits": {**limits["checker"], **{name: limits[name] for name in (
                                "sample_interval_seconds", "max_trace_gap_seconds",
                                "cleanup_seconds", "ps_timeout_seconds", "output_cap_bytes")}},
                            "stdin_bytes": None, "stdin_sha256": None,
                            "raw_stdout_path": stdout.relative_to(base).as_posix(),
                            "raw_stderr_path": stderr.relative_to(base).as_posix(),
                            "started_monotonic_ns": 100 + 10 * index,
                            "drained_monotonic_ns": 105 + 10 * index,
                            "test_status": status})
                        row = {"status": status, "profile": "official", "input": binding(inp),
                               "process": {"receipt": binding(receipt_path),
                                           "stdout": binding(stdout), "stderr": binding(stderr)},
                               "disposition": {"status": status, "reason": "synthetic"},
                               "started_monotonic_ns": 100 + 10 * index}
                        if slot["kind"] == "baseline":
                            row.update(baseline_id=slot["id"], phase="before")
                        else:
                            row.update(cell_id=slot["id"], family=slot["family"],
                                       size=slot["size"])
                    events.append({"slot": slot, "row": row})

                def write_pause(directory, prefix, start, approved, history):
                    ledger = directory / "ledger.ndjson"
                    ledger.write_bytes(b"".join(canonical_json(row) for row in prefix[start:]))
                    pause = directory / "science-pause.json"
                    last = prefix[-1]
                    save(pause, {"status": "AWAITING_INDEPENDENT_LIMIT_DIAGNOSIS",
                                 "scientific_manifest": binding(science),
                                 "execution_manifest": binding(execution),
                                 "corpus_lock": binding(lock_path),
                                 "events": prefix, "segment_start_index": start,
                                 "next_slot_index": len(prefix),
                                 "trigger_cell_id": last["slot"]["id"],
                                 "ledger": binding(ledger),
                                 "approved_triggers": approved, "history": history})
                    review = directory / "independent-limit-review.json"
                    save(review, {"verdict": "PASS_FOR_SEQUENCE_STOP",
                                  "science_pause_sha256": binding(pause)["sha256"],
                                  "trigger_cell_id": last["slot"]["id"],
                                  "trigger_receipt_sha256": last["row"]["process"]["receipt"]["sha256"],
                                  "ledger_sha256": binding(ledger)["sha256"]})
                    return pause, review

                first_pause, first_review = write_pause(first_dir, events[:7], 0, {}, [])
                history = [binding(first_pause), binding(first_review)]
                second_pause, _ = write_pause(second_dir, events, 7,
                                              {"official/pi": schedule[6]["id"]}, history)
                _, triggers, replayed_history = launch._resume_state(
                    second_pause, schedule, corpus_lock, runtime)
                self.assertEqual(triggers, {"official/pi": schedule[6]["id"],
                                            "official/let": schedule[9]["id"]})
                self.assertEqual(len(replayed_history), 4)
                duplicated = copy.deepcopy(events)
                duplicated[1]["row"]["process"] = duplicated[0]["row"]["process"]
                duplicated[1]["row"]["started_monotonic_ns"] = 100
                with self.assertRaisesRegex(GateError, "reused a process receipt"):
                    launch._verify_prefix_events(
                        duplicated, schedule, corpus_lock, runtime,
                        {"official/pi": schedule[6]["id"]}, schedule[9]["id"])
                out_of_order = copy.deepcopy(events)
                second_receipt_path = first_dir / "1.receipt.json"
                second_receipt = json.loads(second_receipt_path.read_text())
                second_receipt["started_monotonic_ns"] = 99
                second_receipt["drained_monotonic_ns"] = 104
                save(second_receipt_path, second_receipt)
                out_of_order[1]["row"]["process"]["receipt"] = binding(second_receipt_path)
                out_of_order[1]["row"]["started_monotonic_ns"] = 99
                with self.assertRaisesRegex(GateError, "timestamps contradict"):
                    launch._verify_prefix_events(
                        out_of_order, schedule, corpus_lock, runtime,
                        {"official/pi": schedule[6]["id"]}, schedule[9]["id"])


if __name__ == "__main__":
    unittest.main()
