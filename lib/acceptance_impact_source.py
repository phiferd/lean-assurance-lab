"""Exact, non-observational source preparation for ACCEPTANCE-IMPACT-PILOT-1.

This module only verifies and materializes the already archived Kiota source.
It never builds or launches Kiota (or any other scientific observer).
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import tarfile
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ITEM = "ACCEPTANCE-IMPACT-PILOT-1"
SOURCE_REVISION = "9fa2c297dd700fe8fd1712a86bdbb258e1c01c42"

SOURCE_LOCK = Path("results/research/kiota-ctor-index-test-1/source-lock.json")
DEPENDENCY_LOCK = Path("results/research/kiota-ctor-index-test-1/dependency-lock.json")
SCIENTIFIC_INPUTS = Path("results/research/kiota-ctor-index-test-1/scientific-inputs.json")
ARCHIVE = Path("results/research/kiota-ctor-index-test-1/kiota-source.tar.gz")

SOURCE_LOCK_SHA256 = "8ace8f6fda8bc607cd2370ba403245310c1cee79d0e726f08a145331a50b6e44"
SOURCE_LOCK_BYTES = 2358
DEPENDENCY_LOCK_SHA256 = "08f97b0825dba055f01ae2e172fbcb5424959523aa4bb70ad70fb4076bd777c7"
DEPENDENCY_LOCK_BYTES = 7287
SCIENTIFIC_INPUTS_SHA256 = "5863c3306cd670ea7417da78cad68ffa034831eec4e536cef51a57003590c003"
SCIENTIFIC_INPUTS_BYTES = 3177
ARCHIVE_SHA256 = "dacbc7bdb92471f2df8fbd4a31b6b6b07c1a0d3f435bfab9e9b093ddad06aaa8"
ARCHIVE_BYTES = 4587521
TOP_LEVEL = f"kiota-{SOURCE_REVISION}/"
SOURCE_REGULAR_FILES = 90
SOURCE_TREE_SHA256 = "e646d403e8f1a7f227e0009276dbcaf4ff07b92f63c46415c56ad828a6557437"

SOURCE_WORKSPACE = Path("external/acceptance-impact-pilot-1-kiota")
SOURCE_DIR = SOURCE_WORKSPACE / TOP_LEVEL.rstrip("/")
TARGET_DIR = SOURCE_WORKSPACE / "target"
KIOTA_BINARY = TARGET_DIR / "release/kiota"

CARGO = Path("/opt/homebrew/Cellar/rust/1.98.0/bin/cargo")
RUSTC = Path("/opt/homebrew/Cellar/rust/1.98.0/bin/rustc")
CARGO_SHA256 = "7dd84b082024c09872d9686922d1537b730a8a06bdd990dd75a6d5186c08dbcd"
CARGO_BYTES = 31148800
RUSTC_SHA256 = "1f9bb25ccda465e30e4eec0d7338725963297793f341de3394d870fbae0c6cc3"
RUSTC_BYTES = 341440
CARGO_VERSION = "cargo 1.98.0 (797e8a9bc 2026-08-05) (Homebrew)"
RUSTC_VERSION = "rustc 1.98.0 (88d9e12ae 2026-08-18) (Homebrew)"
RUST_HOST = "aarch64-apple-darwin"


class SourcePreparationError(ValueError):
    """A frozen source, dependency, or toolchain binding differs."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SourcePreparationError(message)


def _sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _load_json(path: Path) -> Any:
    def pairs(rows: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in rows:
            _require(key not in result, f"duplicate JSON key in {path}: {key}")
            result[key] = value
        return result

    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise SourcePreparationError(f"cannot read exact JSON input {path}: {error}") from error


def _bound_file(path: Path, expected_sha256: str, expected_bytes: int) -> dict[str, Any]:
    _require(path.is_file() and not path.is_symlink(), f"missing or linked bound file: {path}")
    size = path.stat().st_size
    digest = _sha256_file(path)
    _require(size == expected_bytes, f"bound file size differs: {path}")
    _require(digest == expected_sha256, f"bound file digest differs: {path}")
    return {"path": str(path), "sha256": digest, "bytes": size}


def _display(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def _resolve(root: Path, path: Path) -> Path:
    return path if path.is_absolute() else root / path


def _tree_manifest(path: Path) -> tuple[int, str]:
    _require(path.is_dir() and not path.is_symlink(), f"source tree is unavailable: {path}")
    files = sorted(candidate for candidate in path.rglob("*") if candidate.is_file())
    _require(not any(candidate.is_symlink() for candidate in files),
             f"source tree contains a symbolic link: {path}")
    rows = "".join(
        f"{candidate.relative_to(path).as_posix()}\t{_sha256_file(candidate)}\t{candidate.stat().st_size}\n"
        for candidate in files
    ).encode("utf-8")
    return len(files), _sha256_bytes(rows)


def _source_lock(root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    path = root / SOURCE_LOCK
    binding = _bound_file(path, SOURCE_LOCK_SHA256, SOURCE_LOCK_BYTES)
    lock = _load_json(path)
    archive = lock.get("archive", {})
    _require(lock.get("schema_version") == 1, "source lock schema differs")
    _require(lock.get("revision") == SOURCE_REVISION, "source revision differs")
    _require(archive.get("path") == ARCHIVE.as_posix(), "source archive path differs")
    _require(archive.get("sha256") == ARCHIVE_SHA256, "source archive digest lock differs")
    _require(archive.get("bytes") == ARCHIVE_BYTES, "source archive size lock differs")
    _require(archive.get("top_level") == TOP_LEVEL, "source archive prefix differs")
    _require(archive.get("regular_files") == SOURCE_REGULAR_FILES,
             "source archive file count differs")
    _require(archive.get("sorted_path_hash_size_manifest_sha256") == SOURCE_TREE_SHA256,
             "source archive tree lock differs")
    return lock, binding


def _validated_archive_members(bundle: tarfile.TarFile) -> list[tarfile.TarInfo]:
    members = bundle.getmembers()
    _require(len({member.name for member in members}) == len(members),
             "source archive contains duplicate member names")
    root_name = TOP_LEVEL.rstrip("/")
    regular = 0
    for member in members:
        pure = PurePosixPath(member.name)
        _require(not pure.is_absolute() and ".." not in pure.parts,
                 f"unsafe source archive path: {member.name}")
        _require(member.name == root_name or member.name.startswith(TOP_LEVEL),
                 f"source archive member escapes exact prefix: {member.name}")
        _require(member.isfile() or member.isdir(),
                 f"source archive contains a link or special member: {member.name}")
        if member.isfile():
            regular += 1
    _require(regular == SOURCE_REGULAR_FILES, "source archive regular-file count differs")
    return members


def inspect_source_archive(root: Path = ROOT) -> dict[str, Any]:
    """Verify the frozen archive without writing a materialized tree."""
    root = Path(root).resolve()
    lock, lock_binding = _source_lock(root)
    archive_path = root / ARCHIVE
    archive_binding = _bound_file(archive_path, ARCHIVE_SHA256, ARCHIVE_BYTES)
    rows: list[str] = []
    selected = {row["path"]: row for row in lock.get("selected_files", [])}
    selected_seen: set[str] = set()
    try:
        with tarfile.open(archive_path, "r:gz") as bundle:
            members = _validated_archive_members(bundle)
            for member in members:
                if not member.isfile():
                    continue
                stream = bundle.extractfile(member)
                _require(stream is not None, f"cannot read source archive member: {member.name}")
                raw = stream.read()
                relative = member.name[len(TOP_LEVEL):]
                digest = _sha256_bytes(raw)
                _require(len(raw) == member.size, f"source archive member size differs: {relative}")
                rows.append(f"{relative}\t{digest}\t{len(raw)}\n")
                if relative in selected:
                    expected = selected[relative]
                    _require(expected.get("sha256") == digest and expected.get("bytes") == len(raw),
                             f"selected source member differs: {relative}")
                    selected_seen.add(relative)
    except (OSError, tarfile.TarError) as error:
        raise SourcePreparationError(f"cannot inspect source archive: {error}") from error
    manifest = _sha256_bytes("".join(sorted(rows)).encode("utf-8"))
    _require(len(rows) == SOURCE_REGULAR_FILES and manifest == SOURCE_TREE_SHA256,
             "source archive tree manifest differs")
    _require(selected_seen == set(selected), "source archive lacks a selected locked file")
    return {
        "schema_version": 1,
        "item_id": ITEM,
        "status": "PASS",
        "source_revision": SOURCE_REVISION,
        "source_lock": {**lock_binding, "path": SOURCE_LOCK.as_posix()},
        "archive": {**archive_binding, "path": ARCHIVE.as_posix()},
        "top_level": TOP_LEVEL,
        "members": len(members),
        "regular_files": len(rows),
        "tree_manifest_sha256": manifest,
    }


def verify_source_tree(source_dir: Path, root: Path = ROOT) -> dict[str, Any]:
    """Prove that a materialized directory is byte-identical to the archive tree."""
    root = Path(root).resolve()
    source = _resolve(root, Path(source_dir)).resolve()
    inspect_source_archive(root)
    files, manifest = _tree_manifest(source)
    _require(files == SOURCE_REGULAR_FILES, "materialized source file count differs")
    _require(manifest == SOURCE_TREE_SHA256, "materialized source tree manifest differs")
    return {
        "schema_version": 1,
        "item_id": ITEM,
        "status": "PASS",
        "source_revision": SOURCE_REVISION,
        "source_directory": _display(source, root),
        "regular_files": files,
        "tree_manifest_sha256": manifest,
    }


def verify_dependencies(root: Path = ROOT) -> dict[str, Any]:
    """Verify every exact Cargo registry source tree retained by the prior lock."""
    root = Path(root).resolve()
    path = root / DEPENDENCY_LOCK
    binding = _bound_file(path, DEPENDENCY_LOCK_SHA256, DEPENDENCY_LOCK_BYTES)
    lock = _load_json(path)
    _require(lock.get("schema_version") == 1, "dependency lock schema differs")
    cargo_lock = lock.get("cargo_lock", {})
    _require(cargo_lock.get("sha256") ==
             "5ec82186988acc6147319f5d09e80dbec526cd43d25f3dd1ac9a0a9dc00b743b",
             "Cargo.lock digest differs in dependency lock")
    _require(cargo_lock.get("bytes") == 4845 and cargo_lock.get("version") == 4,
             "Cargo.lock size or version differs in dependency lock")
    packages = lock.get("packages")
    _require(isinstance(packages, list) and len(packages) == 21,
             "dependency package set differs")
    verified: list[dict[str, Any]] = []
    identities: set[tuple[str, str]] = set()
    for package in packages:
        name, version = package.get("name"), package.get("version")
        _require(isinstance(name, str) and isinstance(version, str),
                 "dependency identity is malformed")
        _require((name, version) not in identities, f"duplicate dependency identity: {name}")
        identities.add((name, version))
        source_root = Path(package.get("source_root", ""))
        _require(source_root.is_absolute(), f"dependency source root is not absolute: {name}")
        files, manifest = _tree_manifest(source_root)
        _require(files == package.get("files") and manifest == package.get("manifest_sha256"),
                 f"dependency source mismatch: {name}")
        verified.append({
            "name": name,
            "version": version,
            "files": files,
            "manifest_sha256": manifest,
        })
    return {
        "schema_version": 1,
        "item_id": ITEM,
        "status": "PASS",
        "dependency_lock": {**binding, "path": DEPENDENCY_LOCK.as_posix()},
        "cargo_lock_sha256": cargo_lock["sha256"],
        "packages": verified,
    }


def verify_toolchain(root: Path = ROOT) -> dict[str, Any]:
    """Verify the exact Rust binaries and frozen environment used previously."""
    root = Path(root).resolve()
    inputs_path = root / SCIENTIFIC_INPUTS
    inputs_binding = _bound_file(
        inputs_path, SCIENTIFIC_INPUTS_SHA256, SCIENTIFIC_INPUTS_BYTES
    )
    inputs = _load_json(inputs_path)
    _require(inputs.get("source_revision") == SOURCE_REVISION,
             "prior scientific-input source revision differs")
    _require(inputs.get("source_archive", {}).get("sha256") == ARCHIVE_SHA256,
             "prior scientific-input archive differs")
    _require(inputs.get("dependency_lock", {}).get("sha256") == DEPENDENCY_LOCK_SHA256,
             "prior scientific-input dependency lock differs")
    toolchain = inputs.get("toolchain", {})
    cargo = toolchain.get("cargo", {})
    rustc = toolchain.get("rustc", {})
    _require(cargo.get("path") == str(CARGO) and cargo.get("sha256") == CARGO_SHA256
             and cargo.get("bytes") == CARGO_BYTES and cargo.get("version") == CARGO_VERSION
             and cargo.get("host") == RUST_HOST, "frozen Cargo binding differs")
    _require(rustc.get("path") == str(RUSTC) and rustc.get("sha256") == RUSTC_SHA256
             and rustc.get("bytes") == RUSTC_BYTES and rustc.get("version") == RUSTC_VERSION
             and rustc.get("host") == RUST_HOST, "frozen rustc binding differs")
    cargo_binding = _bound_file(CARGO, CARGO_SHA256, CARGO_BYTES)
    rustc_binding = _bound_file(RUSTC, RUSTC_SHA256, RUSTC_BYTES)
    environment = inputs.get("environment", {})
    cargo_home = environment.get("CARGO_HOME")
    _require(isinstance(cargo_home, str) and Path(cargo_home).is_absolute(),
             "frozen Cargo home differs")
    return {
        "schema_version": 1,
        "item_id": ITEM,
        "status": "PASS",
        "scientific_inputs": {**inputs_binding, "path": SCIENTIFIC_INPUTS.as_posix()},
        "cargo": cargo_binding,
        "rustc": rustc_binding,
        "cargo_version": CARGO_VERSION,
        "rustc_version": RUSTC_VERSION,
        "host": RUST_HOST,
        "cargo_home": cargo_home,
    }


def _extract_archive(archive_path: Path, destination: Path) -> None:
    try:
        with tarfile.open(archive_path, "r:gz") as bundle:
            members = _validated_archive_members(bundle)
            for member in members:
                target = destination / member.name
                _require(target.resolve(strict=False).is_relative_to(destination.resolve()),
                         f"source archive extraction escapes destination: {member.name}")
                if member.isdir():
                    target.mkdir(parents=True, exist_ok=True)
                    os.chmod(target, member.mode & 0o777)
            for member in members:
                if not member.isfile():
                    continue
                target = destination / member.name
                target.parent.mkdir(parents=True, exist_ok=True)
                stream = bundle.extractfile(member)
                _require(stream is not None, f"cannot extract source archive member: {member.name}")
                with target.open("xb") as output:
                    shutil.copyfileobj(stream, output)
                os.chmod(target, member.mode & 0o777)
    except (OSError, tarfile.TarError) as error:
        raise SourcePreparationError(f"cannot materialize source archive: {error}") from error


def prepare_source(root: Path = ROOT) -> dict[str, Any]:
    """Materialize the exact source once, or verify the existing exact tree.

    The return value is intentionally the same for a fresh and an existing
    valid materialization. No build directory or observer process is created.
    """
    root = Path(root).resolve()
    archive = inspect_source_archive(root)
    dependencies = verify_dependencies(root)
    toolchain = verify_toolchain(root)
    workspace = _resolve(root, SOURCE_WORKSPACE)
    source = _resolve(root, SOURCE_DIR)
    target = _resolve(root, TARGET_DIR)
    if workspace.exists():
        _require(workspace.is_dir() and not workspace.is_symlink(),
                 "source workspace is not an ordinary directory")
        _require(source.is_dir(), "existing source workspace is incomplete")
    else:
        workspace.parent.mkdir(parents=True, exist_ok=True)
        temporary = workspace.with_name(workspace.name + ".materializing")
        _require(not temporary.exists(), "stale source materialization temporary exists")
        temporary.mkdir()
        _extract_archive(root / ARCHIVE, temporary)
        verify_source_tree(temporary / TOP_LEVEL.rstrip("/"), root)
        os.replace(temporary, workspace)
    source_receipt = verify_source_tree(source, root)
    return {
        "schema_version": 1,
        "item_id": ITEM,
        "status": "PASS",
        "source_revision": SOURCE_REVISION,
        "source_directory": _display(source, root),
        "target_directory": _display(target, root),
        "kiota_binary": _display(_resolve(root, KIOTA_BINARY), root),
        "archive": archive,
        "source": source_receipt,
        "dependencies": dependencies,
        "toolchain": toolchain,
        "build_performed": False,
        "checker_observations": 0,
    }


def inspect_environment(root: Path = ROOT) -> dict[str, Any]:
    """Inspect every frozen preparation input without materializing source."""
    root = Path(root).resolve()
    source = _resolve(root, SOURCE_DIR)
    result: dict[str, Any] = {
        "schema_version": 1,
        "item_id": ITEM,
        "status": "PASS",
        "source_revision": SOURCE_REVISION,
        "source_directory": _display(source, root),
        "target_directory": _display(_resolve(root, TARGET_DIR), root),
        "archive": inspect_source_archive(root),
        "dependencies": verify_dependencies(root),
        "toolchain": verify_toolchain(root),
        "source_materialized": source.is_dir(),
        "build_performed": False,
        "checker_observations": 0,
    }
    if source.is_dir():
        result["source"] = verify_source_tree(source, root)
    return result
