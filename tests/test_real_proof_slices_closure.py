"""Negative controls for the final exact execution binding."""
import copy
import unittest
from unittest import mock

from lib import real_proof_slices_closure as closure


class ClosureBindingTests(unittest.TestCase):
    def test_changed_tooling_hash_fails_before_case_audit(self):
        actual=closure._hash
        target=closure.ROOT/"lib/real_proof_slices_audit.py"
        def changed(path):
            return "0"*64 if path==target else actual(path)
        with mock.patch.object(closure,"_hash",side_effect=changed):
            with self.assertRaisesRegex(closure.ClosureError,"bound tooling differs"):
                closure.validate()

    def test_changed_observer_argv_fails(self):
        actual=closure._read
        target=closure.BASE/"execution/attempt-0001/result.json"
        def changed(path):
            value=actual(path)
            if path==target:
                value=copy.deepcopy(value)
                value["cells"][0]["process_receipt"]["argv"][0]="/wrong/kernel"
            return value
        with mock.patch.object(closure,"_read",side_effect=changed),mock.patch.object(closure,"audit_case"):
            with self.assertRaisesRegex(closure.ClosureError,"observed command/cwd differs"):
                closure.validate()


if __name__=="__main__":
    unittest.main()
