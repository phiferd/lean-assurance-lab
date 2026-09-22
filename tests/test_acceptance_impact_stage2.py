from __future__ import annotations

from pathlib import Path
import unittest

from lib import acceptance_impact_stage2 as stage2


class AcceptanceImpactStage2Tests(unittest.TestCase):
    def test_matrix_is_exact_and_bounded(self) -> None:
        self.assertEqual([row["ordinal"] for row in stage2.EXPECTED_CELLS], [1, 2, 3, 4])
        self.assertEqual(len({row["artifact_id"] for row in stage2.EXPECTED_CELLS}), 2)
        self.assertEqual(set(stage2.EXPECTED_CONSEQUENTIAL),
                         {row["cell_id"] for row in stage2.EXPECTED_CELLS})

    def test_exact_matrix_is_consequential(self) -> None:
        rows = [{"cell": cell, "outcome": stage2.EXPECTED_CONSEQUENTIAL[cell["cell_id"]],
                 "receipt": {"raw_stderr_path": "unused"}}
                for cell in stage2.EXPECTED_CELLS]
        self.assertEqual(stage2._decision(rows, stage2.EXPECTED_CONSEQUENTIAL, stage2.ROOT),
                         "CONSEQUENTIAL_WITHIN_FIXED_USE")

    def test_nonexact_matrix_is_not_promoted_to_harmless(self) -> None:
        rows = [{"cell": cell, "outcome": "REJECT", "receipt": {"raw_stderr_path": "unused"}}
                for cell in stage2.EXPECTED_CELLS]
        self.assertEqual(stage2._decision(rows, stage2.EXPECTED_CONSEQUENTIAL, stage2.ROOT),
                         "CONSTRUCTION_OR_SEMANTIC_BOUNDARY")

    def test_completed_item_refuses_live_stage2_validation(self) -> None:
        with self.assertRaisesRegex(ValueError, "protocol is not ACTIVE"):
            stage2.validate_available(require_commit=False)

    def test_launch_lock_is_exclusive_and_removed(self) -> None:
        lock = stage2.ROOT / stage2.BASE / ".stage-2-launch.lock"
        with stage2._launch_lock(stage2.ROOT):
            self.assertTrue(lock.exists())
            with self.assertRaisesRegex(stage2.Stage2Error, "owns the lock"):
                with stage2._launch_lock(stage2.ROOT):
                    pass
        self.assertFalse(lock.exists())


if __name__ == "__main__":
    unittest.main()
