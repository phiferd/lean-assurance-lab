from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

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

    def test_binds_source_lock_byte_count(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "src" / "main.rs"
            source.parent.mkdir()
            source.write_text("fn main() {}\n", encoding="utf-8")
            row = {"source_path": "src/main.rs", "binding": {
                "path": "src/main.rs", "sha256": audit.sha(source), "bytes": source.stat().st_size}}
            self.assertEqual(audit.source_file(root, row), source)

    def test_allows_existing_error_directory_for_new_ledger(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            existing = root / audit.OUT
            existing.mkdir(parents=True)
            self.assertEqual(audit.prepare_output(root), existing / "audit.json")


if __name__ == "__main__":
    unittest.main()
