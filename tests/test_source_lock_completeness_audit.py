from __future__ import annotations

import unittest

from lib import source_lock_completeness_audit as audit


class SourceLockAuditTests(unittest.TestCase):
    def test_resolves_relative_include(self):
        self.assertEqual(audit.resolved_path("src/main.rs", "../README.md"), "README.md")

    def test_detects_pinned_readme_directive(self):
        rows = audit.directives("src/main.rs", 'const X: &str = include_str!("../README.md");')
        self.assertEqual(rows, [{"source_path": "src/main.rs", "macro": "include_str",
                                 "literal": "../README.md", "resolved_path": "README.md"}])

    def test_refuses_source_root_escape(self):
        with self.assertRaises(ValueError):
            audit.resolved_path("src/main.rs", "../../secret")


if __name__ == "__main__":
    unittest.main()
