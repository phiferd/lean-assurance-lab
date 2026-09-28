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
        actual_hash=closure._hash
        target=closure.BASE/"execution/attempt-0001/result.json"
        controls=actual(closure.BASE/"execution-controls.json")
        portable={
            closure.Path(controls["runtime"]["python_path"]):controls["runtime"]["python_sha256"],
            closure.Path(controls["runtime"]["ps_path"]):controls["runtime"]["ps_sha256"],
        }
        for profile in controls["profiles"]:
            portable[closure.ROOT/profile["binary"]]=profile["sha256"]
            if "config_sha256" in profile:
                portable[closure.ROOT/profile["cwd"]/"config.json"]=profile["config_sha256"]
        def changed(path):
            value=actual(path)
            if path==target:
                value=copy.deepcopy(value)
                value["cells"][0]["process_receipt"]["argv"][0]="/wrong/kernel"
            return value
        def bound_hash(path):
            return portable[path] if path in portable else actual_hash(path)
        with mock.patch.object(closure,"_read",side_effect=changed),mock.patch.object(closure,"_hash",side_effect=bound_hash),mock.patch.object(closure,"audit_case"):
            with self.assertRaisesRegex(closure.ClosureError,"observed command/cwd differs"):
                closure.validate()


if __name__=="__main__":
    unittest.main()
