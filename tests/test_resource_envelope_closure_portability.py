"""Prospective replay of engineering closure fixtures beside frozen science."""

from pathlib import Path
import hashlib
import json
import shutil
import tempfile
import unittest

from lib.resource_envelope_closure_receipts import validate


ROOT = Path(__file__).resolve().parents[1]
REL = Path("results/research/resource-envelope-pilot-1/final-closure-2026-09-29-r2")


class ResourceEnvelopeClosurePortabilityTests(unittest.TestCase):
    def test_failed_closure_fixture_receipts_replay_from_foreign_checkout(self):
        self.assertEqual(validate(ROOT, REL)["cases"], 4)
        with tempfile.TemporaryDirectory() as directory:
            checkout = Path(directory) / "foreign-checkout"
            target = checkout / REL
            target.parent.mkdir(parents=True)
            shutil.copytree(ROOT / REL, target)
            self.assertEqual(len(validate(checkout, REL)["files"]), 12)

            raw = target / "supervisor-receipts/nonzero.stderr"
            raw.write_bytes(raw.read_bytes() + b"tamper")
            with self.assertRaisesRegex(ValueError, "closure raw stream differs"):
                validate(checkout, REL)

            receipt = target / "supervisor-receipts/nonzero.receipt.json"
            original_receipt = receipt.read_bytes()
            changed_raw = b"X" * len(b"refusal\n")
            raw.write_bytes(changed_raw)
            changed_receipt = json.loads(original_receipt)
            changed_receipt["stderr_sha256"] = hashlib.sha256(changed_raw).hexdigest()
            receipt.write_text(json.dumps(changed_receipt) + "\n")
            with self.assertRaisesRegex(ValueError, "closure raw stream differs"):
                validate(checkout, REL)

            raw.write_bytes(b"refusal\n")
            receipt.write_bytes(original_receipt)
            changed = receipt.read_text().replace('"exit_code": 7', '"exit_code": 0')
            receipt.write_text(changed)
            with self.assertRaisesRegex(ValueError, "closure supervisor disposition differs"):
                validate(checkout, REL)

            receipt.write_bytes(original_receipt)
            normal = target / "supervisor-receipts/normal.with.dots.receipt.json"
            original_normal = normal.read_bytes()
            changed_normal = json.loads(original_normal)
            changed_normal["exit_code"] = False
            normal.write_text(json.dumps(changed_normal) + "\n")
            with self.assertRaisesRegex(ValueError, "closure supervisor disposition differs"):
                validate(checkout, REL)


if __name__ == "__main__":
    unittest.main()
