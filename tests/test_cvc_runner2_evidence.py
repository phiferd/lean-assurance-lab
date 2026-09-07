"""Pure adversarial checks for CVC-RUNNER-2 evidence accounting helpers."""
import json
from pathlib import Path
import tempfile
import unittest

from lib import cvc_runner2_evidence as evidence


class EvidenceHelperTests(unittest.TestCase):
    def write(self, directory, name, rows):
        path = Path(directory) / name
        path.write_text(''.join(json.dumps(row) + '\n' for row in rows))
        return path

    def test_legacy_pairs_and_charges(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write(directory, 'legacy.jsonl', [
                {'kind': 'RESERVED', 'reserved_launches': 2, 'reserved_seconds': 10},
                {'kind': 'TERMINAL', 'charged_seconds': 1.25},
            ])
            self.assertEqual(evidence._legacy(path), (2, 1.25))

    def test_legacy_rejects_reset_and_cap_tampering(self):
        with tempfile.TemporaryDirectory() as directory:
            for rows in [
                [{'kind': 'TERMINAL', 'charged_seconds': 0}],
                [{'kind': 'RESERVED', 'reserved_launches': 1, 'reserved_seconds': 5}],
                [{'kind': 'RESERVED', 'reserved_launches': 2, 'reserved_seconds': 5}],
                [{'kind': 'RESERVED', 'reserved_launches': 1, 'reserved_seconds': 5},
                 {'kind': 'TERMINAL', 'charged_seconds': 6}],
            ]:
                path = self.write(directory, 'legacy.jsonl', rows)
                with self.subTest(rows=rows), self.assertRaises(ValueError):
                    evidence._legacy(path)

    def test_session_caps_and_numbering(self):
        work = {'sessions': [{'number': 1, 'started_at': '2026-09-06T00:00:00+00:00',
                              'ended_at': '2026-09-06T01:30:00+00:00'}]}
        self.assertEqual(evidence._sessions(work), 5400)
        work['sessions'][0]['ended_at'] = '2026-09-06T01:30:01+00:00'
        with self.assertRaises(ValueError): evidence._sessions(work)
        work['sessions'][0]['ended_at'] = '2026-09-06T01:00:00+00:00'
        work['sessions'][0]['number'] = 2
        with self.assertRaises(ValueError): evidence._sessions(work)

    def test_command_accepts_declared_receipt_forms(self):
        self.assertEqual(evidence._command({'argv': ['scripts/run-unit-tests', '--require-full-payload']}),
                         'scripts/run-unit-tests --require-full-payload')
        self.assertEqual(evidence._command({'command': 'scripts/run-unit-tests'}), 'scripts/run-unit-tests')

    def test_current_binding_detects_tampering(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'bound'; path.write_text('original')
            row = {'path': 'bound', 'sha256': evidence.sha(path)}
            evidence._binding(Path(directory), row, current=True)
            path.write_text('changed')
            with self.assertRaises(ValueError): evidence._binding(Path(directory), row, current=True)


if __name__ == '__main__':
    unittest.main()
