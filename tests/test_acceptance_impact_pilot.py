from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from lib import acceptance_impact_pilot as pilot


def safe_receipt(code: int = 0) -> dict:
    return {
        "exit_code": code,
        "memory_monitor_error": None,
        "memory_monitor_samples": 2,
        "maximum_observed_rss_bytes": 4096,
        "memory_exceeded": False,
        "timed_out": False,
        "cleanup_complete": True,
    }


class AcceptanceImpactPilotTests(unittest.TestCase):
    def test_frozen_cell_order_and_gate_are_exact(self) -> None:
        self.assertEqual(len(pilot.EXPECTED_CELLS), 4)
        self.assertEqual(len({row["cell_id"] for row in pilot.EXPECTED_CELLS}), 4)
        self.assertEqual([row["ordinal"] for row in pilot.EXPECTED_CELLS], [1, 2, 3, 4])
        self.assertEqual(set(pilot.EXPECTED_GATE),
                         {row["cell_id"] for row in pilot.EXPECTED_CELLS})

    def test_classifier_accepts_only_exact_success_and_intended_rejection(self) -> None:
        receipt = safe_receipt()
        self.assertEqual(pilot.classify("kiota-9fa2c297", receipt, b"", b"")[0], "ACCEPT")
        self.assertEqual(
            pilot.classify("official-lean-4.33.0", receipt,
                           b"Accepted 7 declarations.\n", b"")[0], "ACCEPT")
        rejected = safe_receipt(1)
        self.assertEqual(
            pilot.classify("official-lean-4.33.0", rejected, b"",
                           b"uncaught exception: Invalid recursor LALNest.rec_1\n")[0],
            "INTENDED_RECURSOR_REJECT",
        )
        self.assertEqual(pilot.classify("kiota-9fa2c297", receipt, b"noise", b"")[0],
                         "INFRASTRUCTURE_AUDIT_FAILURE")

    def test_every_safety_defect_is_infrastructure_failure(self) -> None:
        for key, value in (
            ("memory_monitor_error", "lost"), ("memory_monitor_samples", 0),
            ("maximum_observed_rss_bytes", 0), ("memory_exceeded", True),
            ("timed_out", True), ("cleanup_complete", False),
        ):
            receipt = safe_receipt()
            receipt[key] = value
            self.assertEqual(
                pilot.classify("kiota-9fa2c297", receipt, b"", b"")[0],
                "INFRASTRUCTURE_AUDIT_FAILURE",
                key,
            )

    def test_build_environment_contains_only_frozen_keys(self) -> None:
        manifest = {
            "environment": {"PATH": "/bin", "LANG": "C"},
            "required_absent_environment": ["RUSTFLAGS"],
        }
        self.assertEqual(pilot._build_environment(manifest), manifest["environment"])
        manifest["environment"]["RUSTFLAGS"] = "-Ctarget-cpu=native"
        with self.assertRaisesRegex(pilot.PilotError, "required-absent"):
            pilot._build_environment(manifest)

    def test_validate_only_never_invokes_supervisor(self) -> None:
        with mock.patch.object(pilot, "run_supervised",
                               side_effect=AssertionError("must not launch")):
            result = pilot.validate_preparation(require_commit=False)
        self.assertEqual(result["pair_audit"], "PASS")
        self.assertEqual(result["source_environment"], "PASS")

    def test_raw_receipt_replay_rejects_tampering(self) -> None:
        with tempfile.TemporaryDirectory(dir=pilot.ROOT) as raw:
            directory = Path(raw)
            stdout = directory / "cell.stdout"
            stderr = directory / "cell.stderr"
            stdout.write_bytes(b"ok")
            stderr.write_bytes(b"")
            receipt = safe_receipt()
            receipt.update({
                "raw_stdout_path": stdout.relative_to(pilot.ROOT).as_posix(),
                "raw_stderr_path": stderr.relative_to(pilot.ROOT).as_posix(),
                "stdout_bytes": 2, "stderr_bytes": 0,
                "stdout_sha256": pilot.sha256(stdout), "stderr_sha256": pilot.sha256(stderr),
            })
            self.assertEqual(pilot._verify_raw(receipt), (b"ok", b""))
            stdout.write_bytes(b"changed")
            with self.assertRaisesRegex(pilot.PilotError, "raw stdout"):
                pilot._verify_raw(receipt)

    def test_launch_lock_is_exclusive(self) -> None:
        lock = pilot.ROOT / pilot.BASE / ".stage-1-launch.lock"
        try:
            with pilot._launch_lock(pilot.ROOT):
                with self.assertRaisesRegex(pilot.PilotError, "owns the lock"):
                    with pilot._launch_lock(pilot.ROOT):
                        pass
        finally:
            lock.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
