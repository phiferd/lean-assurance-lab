from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from lib import acceptance_impact_source as source


class AcceptanceImpactSourceTests(unittest.TestCase):
    def test_archive_dependencies_and_toolchain_match_frozen_inputs(self) -> None:
        archive = source.inspect_source_archive()
        self.assertEqual(archive["status"], "PASS")
        self.assertEqual(archive["regular_files"], 90)
        self.assertEqual(archive["tree_manifest_sha256"], source.SOURCE_TREE_SHA256)

        dependencies = source.verify_dependencies()
        self.assertEqual(dependencies["status"], "PASS")
        self.assertEqual(len(dependencies["packages"]), 21)

        toolchain = source.verify_toolchain()
        self.assertEqual(toolchain["cargo"]["sha256"], source.CARGO_SHA256)
        self.assertEqual(toolchain["rustc"]["sha256"], source.RUSTC_SHA256)

    def test_prepare_is_exact_idempotent_and_non_observational(self) -> None:
        external = source.ROOT / "external"
        with tempfile.TemporaryDirectory(prefix="acceptance-impact-source-test-", dir=external) as raw:
            workspace = Path(raw) / "workspace"
            source_dir = workspace / source.TOP_LEVEL.rstrip("/")
            target_dir = workspace / "target"
            binary = target_dir / "release/kiota"
            with (mock.patch.object(source, "SOURCE_WORKSPACE", workspace),
                  mock.patch.object(source, "SOURCE_DIR", source_dir),
                  mock.patch.object(source, "TARGET_DIR", target_dir),
                  mock.patch.object(source, "KIOTA_BINARY", binary)):
                first = source.prepare_source()
                second = source.prepare_source()
                self.assertEqual(first, second)
                self.assertEqual(first["status"], "PASS")
                self.assertFalse(first["build_performed"])
                self.assertEqual(first["checker_observations"], 0)
                self.assertFalse(target_dir.exists())
                self.assertEqual(source.verify_source_tree(source_dir)["regular_files"], 90)

    def test_materialized_source_tampering_is_rejected(self) -> None:
        external = source.ROOT / "external"
        with tempfile.TemporaryDirectory(prefix="acceptance-impact-source-tamper-", dir=external) as raw:
            workspace = Path(raw) / "workspace"
            source_dir = workspace / source.TOP_LEVEL.rstrip("/")
            target_dir = workspace / "target"
            binary = target_dir / "release/kiota"
            with (mock.patch.object(source, "SOURCE_WORKSPACE", workspace),
                  mock.patch.object(source, "SOURCE_DIR", source_dir),
                  mock.patch.object(source, "TARGET_DIR", target_dir),
                  mock.patch.object(source, "KIOTA_BINARY", binary)):
                source.prepare_source()
                cargo = source_dir / "Cargo.toml"
                cargo.write_bytes(cargo.read_bytes() + b"\n")
                with self.assertRaisesRegex(source.SourcePreparationError,
                                            "materialized source tree manifest differs"):
                    source.verify_source_tree(source_dir)


if __name__ == "__main__":
    unittest.main()
