"""Availability boundary for the frozen acceptance-impact host integration tests.

Missing host-local Cargo sources or compiler binaries may be reported explicitly
by the test driver. Present but corrupt inputs always fail, even when another
input is absent. This helper never supplies a replacement PASS receipt and never
changes the frozen source-preparation implementation.
"""
from __future__ import annotations

from pathlib import Path

from lib import acceptance_impact_source as source


def _absent(path: Path) -> bool:
    # A dangling link is corrupt payload, not missing payload. Likewise, errors
    # other than ENOENT (including a non-directory parent) must not become skips.
    try:
        path.lstat()
    except FileNotFoundError:
        return True
    source._require(not path.is_symlink(), f"linked host payload: {path}")
    return False


def missing_host_payload(root: Path) -> list[Path]:
    """Validate tracked bindings and every present host input; list absent ones."""
    root = Path(root).resolve()
    source.inspect_source_archive(root)
    dependency_path = root / source.DEPENDENCY_LOCK
    source._bound_file(dependency_path, source.DEPENDENCY_LOCK_SHA256,
                       source.DEPENDENCY_LOCK_BYTES)
    inputs_path = root / source.SCIENTIFIC_INPUTS
    source._bound_file(inputs_path, source.SCIENTIFIC_INPUTS_SHA256,
                       source.SCIENTIFIC_INPUTS_BYTES)
    lock = source._load_json(dependency_path)
    inputs = source._load_json(inputs_path)
    source._require(lock.get("schema_version") == 1, "dependency lock schema differs")
    source._require(lock.get("cargo_lock") == {
        "sha256": "5ec82186988acc6147319f5d09e80dbec526cd43d25f3dd1ac9a0a9dc00b743b",
        "bytes": 4845, "version": 4,
    }, "Cargo.lock binding differs")
    source._require(inputs.get("source_revision") == source.SOURCE_REVISION,
                    "prior scientific-input source revision differs")
    source._require(inputs.get("source_archive", {}).get("sha256") == source.ARCHIVE_SHA256,
                    "prior scientific-input archive differs")
    source._require(inputs.get("dependency_lock", {}).get("sha256") == source.DEPENDENCY_LOCK_SHA256,
                    "prior scientific-input dependency lock differs")
    cargo_home = inputs.get("environment", {}).get("CARGO_HOME")
    source._require(isinstance(cargo_home, str) and Path(cargo_home).is_absolute(),
                    "frozen Cargo home differs")
    packages = lock.get("packages")
    source._require(isinstance(packages, list) and len(packages) == 21,
                    "dependency package set differs")
    missing: list[Path] = []
    identities: set[tuple[str, str]] = set()
    for package in packages:
        name, version = package.get("name"), package.get("version")
        source._require(isinstance(name, str) and isinstance(version, str),
                        "dependency identity is malformed")
        source._require((name, version) not in identities,
                        f"duplicate dependency identity: {name}")
        identities.add((name, version))
        path = Path(package.get("source_root", ""))
        source._require(path.is_absolute(), f"dependency source root is not absolute: {name}")
        if _absent(path):
            missing.append(path)
            continue
        source._require(path.is_dir(), f"source tree is unavailable: {path}")
        source._require(not any(node.is_symlink() for node in path.rglob("*")),
                        f"source tree contains a symbolic link: {path}")
        count, digest = source._tree_manifest(path)
        source._require(count == package.get("files") and digest == package.get("manifest_sha256"),
                        f"dependency source mismatch: {name}")
    for kind, path, digest, size, version in (
        ("cargo", source.CARGO, source.CARGO_SHA256, source.CARGO_BYTES, source.CARGO_VERSION),
        ("rustc", source.RUSTC, source.RUSTC_SHA256, source.RUSTC_BYTES, source.RUSTC_VERSION),
    ):
        row = inputs.get("toolchain", {}).get(kind, {})
        source._require(all(row.get(key) == value for key, value in {
            "path": str(path), "sha256": digest, "bytes": size,
            "version": version, "host": source.RUST_HOST,
        }.items()), f"frozen {kind} binding differs")
        if _absent(path):
            missing.append(path)
        else:
            source._bound_file(path, digest, size)
    return missing
