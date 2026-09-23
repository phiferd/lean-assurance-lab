"""Clean-checkout regressions for exact, source-only historical test inputs."""
from __future__ import annotations

import hashlib
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock

from lib import acceptance_impact_source as source
from lib import kiota_recursor_type_design as design
from lib import kiota_source_payload as payload
from lib import recursor_type_trust_boundary as boundary


class KiotaSourcePayloadTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        for relative in (source.SOURCE_LOCK, source.ARCHIVE, payload.WRAPPER_CUSTODY):
            destination = self.root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source.ROOT / relative, destination)

    def test_clean_checkout_restores_all_bound_external_sources_without_host_payload(self):
        self.assertFalse((self.root / "external").exists())
        forbidden = AssertionError("source bootstrap must not inspect hosts or launch processes")
        with mock.patch.object(source, "verify_dependencies", side_effect=forbidden), \
                mock.patch.object(source, "verify_toolchain", side_effect=forbidden), \
                mock.patch("subprocess.Popen", side_effect=forbidden):
            receipt = payload.prepare_test_source(self.root)
        self.assertEqual(receipt["status"], "PASS")
        self.assertEqual(receipt["source"]["regular_files"], 90)
        self.assertFalse(receipt["build_performed"])
        self.assertEqual(receipt["checker_observations"], 0)
        self.assertFalse((self.root / source.TARGET_DIR).exists())
        bindings = [*design.SOURCE_BINDINGS.values(), *design.FIXTURE_BINDINGS.values(),
                    *boundary.SOURCE_BINDINGS.values(), boundary.TEST_SEAM]
        for relative, size, digest, *_ in bindings:
            if relative.startswith("external/"):
                with self.subTest(path=relative):
                    data = (self.root / relative).read_bytes()
                    self.assertEqual(len(data), size)
                    self.assertEqual(hashlib.sha256(data).hexdigest(), digest)

    def test_existing_exact_payload_is_idempotent(self):
        first = payload.prepare_test_source(self.root)
        tracked = self.root / source.SOURCE_DIR / "src/parser.rs"
        before = tracked.stat().st_mtime_ns
        self.assertEqual(payload.prepare_test_source(self.root), first)
        self.assertEqual(tracked.stat().st_mtime_ns, before)

    def test_changed_tree_fails_without_overwriting(self):
        payload.prepare_test_source(self.root)
        target = self.root / source.SOURCE_DIR / "src/parser.rs"
        target.write_bytes(b"changed source")
        with self.assertRaisesRegex(source.SourcePreparationError, "tree manifest differs"):
            payload.prepare_test_source(self.root)
        self.assertEqual(target.read_bytes(), b"changed source")

    def test_changed_wrapper_fails_without_overwriting(self):
        payload.prepare_test_source(self.root)
        target = self.root / payload.WRAPPER_TARGET
        target.write_bytes(b"changed wrapper")
        with self.assertRaisesRegex(source.SourcePreparationError, "bound file size differs"):
            payload.prepare_test_source(self.root)
        self.assertEqual(target.read_bytes(), b"changed wrapper")

    def test_changed_archive_and_custody_are_rejected(self):
        for relative in (source.ARCHIVE, payload.WRAPPER_CUSTODY):
            with self.subTest(path=relative):
                target = self.root / relative
                original = target.read_bytes()
                target.write_bytes(b"x" * len(original))
                with self.assertRaisesRegex(source.SourcePreparationError, "bound file digest differs"):
                    payload.prepare_test_source(self.root)
                self.assertFalse((self.root / "external").exists())
                target.write_bytes(original)

    def test_linked_ancestor_is_rejected_before_writing(self):
        outside = self.root / "outside"
        outside.mkdir()
        (self.root / "external").symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(source.SourcePreparationError, "linked source payload path"):
            payload.prepare_test_source(self.root)
        self.assertEqual(list(outside.iterdir()), [])

    def test_linked_tree_and_wrapper_are_rejected(self):
        payload.prepare_test_source(self.root)
        tree = self.root / source.SOURCE_DIR
        original = tree / "src/parser.rs"
        renamed = original.with_name("parser.saved")
        original.rename(renamed)
        original.symlink_to(renamed.name)
        with self.assertRaisesRegex(source.SourcePreparationError, "tree contains a link"):
            payload.prepare_test_source(self.root)
        original.unlink()
        renamed.rename(original)
        wrapper = self.root / payload.WRAPPER_TARGET
        wrapper.unlink()
        wrapper.symlink_to(self.root / payload.WRAPPER_CUSTODY)
        with self.assertRaisesRegex(source.SourcePreparationError, "linked source payload path"):
            payload.prepare_test_source(self.root)

    def test_incomplete_existing_workspace_is_not_replaced(self):
        workspace = self.root / source.SOURCE_WORKSPACE
        workspace.mkdir(parents=True)
        sentinel = workspace / "unfinished.txt"
        sentinel.write_text("preserve")
        with self.assertRaisesRegex(source.SourcePreparationError, "source tree is unavailable"):
            payload.prepare_test_source(self.root)
        self.assertEqual(sentinel.read_text(), "preserve")
        self.assertFalse((self.root / source.SOURCE_DIR).exists())


if __name__ == "__main__":
    unittest.main()
