"""Portable preparation tests; synthetic host files are never executed.

The original integration tests and implementation retain their bound bytes.
These regressions exercise their validation logic with explicitly synthetic
bindings and source preparation with explicitly mocked host preflights.
"""
from __future__ import annotations

from contextlib import ExitStack
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock

from lib import acceptance_impact_source as source
from lib.acceptance_impact_test_payload import missing_host_payload


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


class HostPayloadTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.patches = ExitStack()
        self.addCleanup(self.patches.close)
        self.lock = json.loads((source.ROOT / source.DEPENDENCY_LOCK).read_text())
        self.inputs = json.loads((source.ROOT / source.SCIENTIFIC_INPUTS).read_text())
        self.crates = []
        for index, row in enumerate(self.lock["packages"]):
            directory = self.directory / f"crate-{index}"
            directory.mkdir()
            content = f"synthetic crate {index}\n".encode()
            (directory / "source.txt").write_bytes(content)
            manifest = f"source.txt\t{digest(content)}\t{len(content)}\n".encode()
            row.update(source_root=str(directory), files=1, manifest_sha256=digest(manifest))
            self.crates.append(directory)
        self.lock_path = self.directory / "dependencies.json"
        self.lock_bytes = (json.dumps(self.lock) + "\n").encode()
        self.lock_path.write_bytes(self.lock_bytes)
        self.patch("DEPENDENCY_LOCK", self.lock_path)
        self.patch("DEPENDENCY_LOCK_SHA256", digest(self.lock_bytes))
        self.patch("DEPENDENCY_LOCK_BYTES", len(self.lock_bytes))
        self.inputs["dependency_lock"]["sha256"] = digest(self.lock_bytes)
        self.binaries = []
        for kind in ("cargo", "rustc"):
            path = self.directory / kind
            content = f"synthetic {kind} bytes, not an executable\n".encode()
            path.write_bytes(content)
            self.inputs["toolchain"][kind].update(
                path=str(path), bytes=len(content), sha256=digest(content),
            )
            self.patch(kind.upper(), path)
            self.patch(kind.upper() + "_BYTES", len(content))
            self.patch(kind.upper() + "_SHA256", digest(content))
            self.binaries.append(path)
        self.inputs_path = self.directory / "inputs.json"
        self.inputs_bytes = (json.dumps(self.inputs) + "\n").encode()
        self.inputs_path.write_bytes(self.inputs_bytes)
        self.patch("SCIENTIFIC_INPUTS", self.inputs_path)
        self.patch("SCIENTIFIC_INPUTS_SHA256", digest(self.inputs_bytes))
        self.patch("SCIENTIFIC_INPUTS_BYTES", len(self.inputs_bytes))

    def patch(self, name, value):
        self.patches.enter_context(mock.patch.object(source, name, value))

    def test_original_host_verifiers_and_boundary_accept_exact_synthetic_bindings(self):
        self.assertEqual(source.verify_dependencies()["status"], "PASS")
        self.assertEqual(source.verify_toolchain()["status"], "PASS")
        self.assertEqual(missing_host_payload(source.ROOT), [])

    def test_boundary_reports_only_missing_resources(self):
        shutil.rmtree(self.crates[0])
        self.binaries[0].unlink()
        self.assertEqual(missing_host_payload(source.ROOT), [self.crates[0], self.binaries[0]])
        with self.assertRaises(source.SourcePreparationError):
            source.verify_dependencies()
        with self.assertRaises(source.SourcePreparationError):
            source.verify_toolchain()

    def test_missing_resource_cannot_hide_another_corrupt_crate(self):
        shutil.rmtree(self.crates[0])
        (self.crates[-1] / "source.txt").write_bytes(b"corrupt\n")
        with self.assertRaisesRegex(source.SourcePreparationError, "dependency source mismatch"):
            missing_host_payload(source.ROOT)
        with self.assertRaisesRegex(source.SourcePreparationError, "source tree is unavailable"):
            source.verify_dependencies()

    def test_missing_resource_cannot_hide_corrupt_compiler(self):
        shutil.rmtree(self.crates[0])
        original = self.binaries[-1].read_bytes()
        self.binaries[-1].write_bytes(b"x" * len(original))
        with self.assertRaisesRegex(source.SourcePreparationError, "bound file digest differs"):
            missing_host_payload(source.ROOT)
        with self.assertRaisesRegex(source.SourcePreparationError, "bound file digest differs"):
            source.verify_toolchain()

    def test_present_corrupt_crate_is_rejected_by_original_verifier(self):
        (self.crates[0] / "source.txt").write_bytes(b"corrupt\n")
        with self.assertRaisesRegex(source.SourcePreparationError, "dependency source mismatch"):
            source.verify_dependencies()

    def test_wrong_kind_and_dangling_link_are_not_absence(self):
        path = self.crates[0]
        shutil.rmtree(path)
        path.write_text("not a directory")
        with self.assertRaisesRegex(source.SourcePreparationError, "source tree is unavailable"):
            missing_host_payload(source.ROOT)
        path.unlink()
        path.symlink_to(self.directory / "missing-target")
        with self.assertRaisesRegex(source.SourcePreparationError, "linked host payload"):
            missing_host_payload(source.ROOT)

    def test_link_within_present_crate_is_rejected(self):
        (self.crates[0] / "alias").symlink_to(self.crates[1], target_is_directory=True)
        with self.assertRaisesRegex(source.SourcePreparationError, "symbolic link"):
            missing_host_payload(source.ROOT)

    def test_missing_host_cannot_hide_changed_tracked_metadata(self):
        shutil.rmtree(self.crates[0])
        self.lock_path.write_bytes(self.lock_bytes + b"\n")
        with self.assertRaisesRegex(source.SourcePreparationError, "bound file size differs"):
            missing_host_payload(source.ROOT)

    def test_toolchain_metadata_mismatch_rejects_even_if_all_files_are_absent(self):
        for path in self.crates:
            shutil.rmtree(path)
        for path in self.binaries:
            path.unlink()
        self.inputs["toolchain"]["cargo"]["host"] = "other-host"
        raw = (json.dumps(self.inputs) + "\n").encode()
        self.inputs_path.write_bytes(raw)
        # Rebinding synthetic fixture bytes must not bypass metadata checks.
        self.patch("SCIENTIFIC_INPUTS_SHA256", digest(raw))
        self.patch("SCIENTIFIC_INPUTS_BYTES", len(raw))
        with self.assertRaisesRegex(source.SourcePreparationError, "frozen cargo binding differs"):
            missing_host_payload(source.ROOT)


class PortableSourcePreparationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.workspace = Path(self.temporary.name) / "workspace"
        self.source_directory = self.workspace / source.TOP_LEVEL.rstrip("/")
        self.target = self.workspace / "target"
        self.patches = ExitStack()
        self.addCleanup(self.patches.close)
        for name, value in (
            ("SOURCE_WORKSPACE", self.workspace), ("SOURCE_DIR", self.source_directory),
            ("TARGET_DIR", self.target), ("KIOTA_BINARY", self.target / "release/kiota"),
        ):
            self.patches.enter_context(mock.patch.object(source, name, value))
        self.dependencies = self.patches.enter_context(mock.patch.object(
            source, "verify_dependencies", return_value={"test_double": "dependencies"},
        ))
        self.toolchain = self.patches.enter_context(mock.patch.object(
            source, "verify_toolchain", return_value={"test_double": "toolchain"},
        ))

    def test_real_archive_preparation_is_exact_idempotent_and_non_observational(self):
        first = source.prepare_source()
        second = source.prepare_source()
        self.assertEqual(first, second)
        self.assertEqual(first["source"]["regular_files"], 90)
        self.assertEqual(first["source"]["tree_manifest_sha256"], source.SOURCE_TREE_SHA256)
        self.assertEqual(first["dependencies"], {"test_double": "dependencies"})
        self.assertEqual(first["toolchain"], {"test_double": "toolchain"})
        self.assertFalse(first["build_performed"])
        self.assertEqual(first["checker_observations"], 0)
        self.assertFalse(self.target.exists())
        self.assertEqual(self.dependencies.call_args_list, [mock.call(source.ROOT)] * 2)
        self.assertEqual(self.toolchain.call_args_list, [mock.call(source.ROOT)] * 2)

    def test_materialized_tampering_is_rejected_and_not_overwritten(self):
        source.prepare_source()
        cargo = self.source_directory / "Cargo.toml"
        changed = cargo.read_bytes() + b"\n"
        cargo.write_bytes(changed)
        with self.assertRaisesRegex(source.SourcePreparationError,
                                    "materialized source tree manifest differs"):
            source.prepare_source()
        self.assertEqual(cargo.read_bytes(), changed)
        self.assertFalse(self.target.exists())

    def test_host_preflight_failure_prevents_materialization(self):
        self.dependencies.side_effect = source.SourcePreparationError("test host failure")
        with self.assertRaisesRegex(source.SourcePreparationError, "test host failure"):
            source.prepare_source()
        self.toolchain.assert_not_called()
        self.assertFalse(self.workspace.exists())


if __name__ == "__main__":
    unittest.main()
