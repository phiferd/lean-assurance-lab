from __future__ import annotations

import unittest

from lib.child_panic_confirmation import SUCCESS, classify


def receipt(code):
    return {"exit_code": code, "memory_monitor_error": None, "memory_monitor_samples": 1,
            "maximum_observed_rss_bytes": 1, "memory_exceeded": False,
            "timed_out": False, "cleanup_complete": True}


class ChildPanicConfirmationTests(unittest.TestCase):
    def test_accept(self):
        self.assertEqual(classify("control-baseline", receipt(0), SUCCESS, b""), "ACCEPT")

    def test_direct_refusal(self):
        stderr = b"thread 'main' panicked\nassertion failed: self.def_eq(u, v)\n"
        self.assertEqual(classify("candidate-baseline", receipt(101), b"", stderr),
                         "DIRECT_ASSERTION_REFUSAL")

    def test_worker_join_refusal(self):
        stderr = (b"thread 'thread_0' panicked\nassertion failed: self.def_eq(u, v)\n"
                  b"A thread in `check_all_declars` panicked while being joined\n")
        self.assertEqual(classify("candidate-mutant", receipt(101), b"", stderr),
                         "WORKER_PANIC_JOIN_REFUSAL")


if __name__ == "__main__":
    unittest.main()
