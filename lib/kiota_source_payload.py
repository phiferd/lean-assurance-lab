"""Restore source-only test inputs from exact committed custody copies.

The historical validators retain their original paths and hashes. This test
bootstrap supplies those bytes on a clean checkout without requiring the Rust
toolchain or Cargo registry used by the historical experiment.
"""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import tempfile
from typing import Any

from lib import acceptance_impact_source as source


WRAPPER_CUSTODY = Path(
    "results/research/conditional-validation-contracts/cvc-4-conditional/"
    "mapping/sources/official-main.lean"
)
WRAPPER_TARGET = Path("external/lean-kernel-arena/checkers/official-v4.33.0/Main.lean")
WRAPPER_BYTES = 968
WRAPPER_SHA256 = "f0c209172f79e2b0b6599f7acc989e15a158f4118a6ddab0a567773b75f333bb"


def _ordinary_path(root: Path, relative: Path) -> Path:
    """Reject linked ancestors as well as linked final files/directories."""
    path = root
    for part in relative.parts:
        path = path / part
        if path.is_symlink():
            raise source.SourcePreparationError(f"linked source payload path: {path}")
    return path


def _verify_tree(path: Path, root: Path) -> dict[str, Any]:
    # The frozen tree checker checks file links; reject directory links too.
    if path.is_dir() and any(entry.is_symlink() for entry in path.rglob("*")):
        raise source.SourcePreparationError(f"source payload tree contains a link: {path}")
    return source.verify_source_tree(path, root)


def prepare_test_source(root: Path = source.ROOT) -> dict[str, Any]:
    """Materialize absent source inputs, or verify them without overwriting.

    No dependency/toolchain inspection, build, checker, or network operation is
    performed. Existing incomplete or changed payloads fail closed. Fresh
    Kiota extraction is verified in an owned temporary directory before rename.
    """
    root = Path(root).resolve()
    archive = source.inspect_source_archive(root)
    workspace = _ordinary_path(root, source.SOURCE_WORKSPACE)
    tree = _ordinary_path(root, source.SOURCE_DIR)
    custody = _ordinary_path(root, WRAPPER_CUSTODY)
    source._bound_file(custody, WRAPPER_SHA256, WRAPPER_BYTES)
    wrapper = _ordinary_path(root, WRAPPER_TARGET)
    if wrapper.exists():
        source._bound_file(wrapper, WRAPPER_SHA256, WRAPPER_BYTES)

    if workspace.exists():
        if not workspace.is_dir():
            raise source.SourcePreparationError(f"source workspace is not a directory: {workspace}")
        tree_receipt = _verify_tree(tree, root)
    else:
        workspace.parent.mkdir(parents=True, exist_ok=True)
        temporary = Path(tempfile.mkdtemp(prefix=workspace.name + ".test-", dir=workspace.parent))
        try:
            source._extract_archive(root / source.ARCHIVE, temporary)
            _verify_tree(temporary / source.TOP_LEVEL.rstrip("/"), root)
            if workspace.exists() or workspace.is_symlink():
                raise source.SourcePreparationError(f"source workspace appeared during preparation: {workspace}")
            os.rename(temporary, workspace)
        finally:
            if temporary.exists():
                shutil.rmtree(temporary)
        tree_receipt = _verify_tree(tree, root)

    if not wrapper.exists():
        wrapper.parent.mkdir(parents=True, exist_ok=True)
        # Exclusive creation preserves any file that appeared since preflight.
        with wrapper.open("xb") as output:
            output.write(custody.read_bytes())
    source._bound_file(wrapper, WRAPPER_SHA256, WRAPPER_BYTES)
    return {
        "status": "PASS",
        "archive": archive,
        "source": tree_receipt,
        "official_wrapper": {
            "path": WRAPPER_TARGET.as_posix(),
            "custody_path": WRAPPER_CUSTODY.as_posix(),
            "bytes": WRAPPER_BYTES,
            "sha256": WRAPPER_SHA256,
        },
        "build_performed": False,
        "checker_observations": 0,
        "network_requests": 0,
    }
