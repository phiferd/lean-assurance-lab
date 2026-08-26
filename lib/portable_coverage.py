"""Path-independent Rust coverage builds and canonical LLVM coverage parsing."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any, Iterable


VIRTUAL_CHECKER_ROOT = "/lean-assurance/nanoda"
VIRTUAL_CARGO_HOME = "/lean-assurance/cargo-home"
VIRTUAL_TARGET_ROOT = "/lean-assurance/cargo-target"
VIRTUAL_RUST_SYSROOT = "/lean-assurance/rust-sysroot"
PATH_REMAP_SCOPE = "all"


class PortableCoverageError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_digest(checker_root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted((checker_root / "src").rglob("*.rs")):
        digest.update(path.relative_to(checker_root).as_posix().encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def command_output(command: list[str]) -> str:
    return subprocess.run(
        command, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    ).stdout.strip()


def tool_identity() -> dict[str, str]:
    return {
        "cargo": command_output(["cargo", "--version"]),
        "rustc": command_output(["rustc", "--version", "--verbose"]),
        "host": command_output(["rustc", "--print", "host-tuple"]),
    }


def rustc_sysroot() -> Path:
    return Path(command_output(["rustc", "--print", "sysroot"])).resolve()


def cargo_home() -> Path:
    return Path(os.environ.get("CARGO_HOME", Path.home() / ".cargo")).resolve()


def remap_flags(checker_root: Path, target_dir: Path, instrument_coverage: bool) -> list[str]:
    mappings = [
        (target_dir.resolve(), VIRTUAL_TARGET_ROOT),
        (checker_root.resolve(), VIRTUAL_CHECKER_ROOT),
        (cargo_home(), VIRTUAL_CARGO_HOME),
        (rustc_sysroot(), VIRTUAL_RUST_SYSROOT),
    ]
    flags: list[str] = []
    if instrument_coverage:
        flags.extend(["-C", "instrument-coverage"])
    flags.extend(["-C", "codegen-units=1"])
    for source, destination in mappings:
        flags.extend(["--remap-path-prefix", f"{source}={destination}"])
    flags.extend(["--remap-path-scope", PATH_REMAP_SCOPE])
    return flags


def build_commands() -> list[list[str]]:
    commands = [["cargo", "build", "--locked", "--release"]]
    if command_output(["rustc", "--print", "host-tuple"]).endswith("-darwin"):
        commands.append(
            [
                "cargo",
                "rustc",
                "--locked",
                "--release",
                "--bin",
                "nanoda_bin",
                "--",
                "-C",
                "link-arg=-Wl,-no_uuid",
            ]
        )
    return commands


def build_environment(
    checker_root: Path, target_dir: Path, instrument_coverage: bool = True
) -> tuple[dict[str, str], list[str]]:
    flags = remap_flags(checker_root, target_dir, instrument_coverage)
    env = os.environ.copy()
    env.pop("RUSTFLAGS", None)
    env["CARGO_ENCODED_RUSTFLAGS"] = "\x1f".join(flags)
    env["CARGO_TARGET_DIR"] = str(target_dir.resolve())
    env["CARGO_INCREMENTAL"] = "0"
    env["CARGO_PROFILE_RELEASE_LTO"] = "false"
    env["SOURCE_DATE_EPOCH"] = "0"
    env["ZERO_AR_DATE"] = "1"
    return env, flags


def logical_remaps(instrument_coverage: bool = True) -> list[dict[str, str]]:
    mappings = [
        {"source": "cargo_target_dir", "destination": VIRTUAL_TARGET_ROOT},
        {"source": "checker_root", "destination": VIRTUAL_CHECKER_ROOT},
        {"source": "cargo_home", "destination": VIRTUAL_CARGO_HOME},
        {"source": "rustc_sysroot", "destination": VIRTUAL_RUST_SYSROOT},
    ]
    if instrument_coverage:
        mappings.insert(0, {"source": "rustc_flag", "destination": "-C instrument-coverage"})
    return mappings


def build_identity(checker_root: Path, instrument_coverage: bool = True) -> dict[str, Any]:
    cargo_lock = checker_root / "Cargo.lock"
    cargo_toml = checker_root / "Cargo.toml"
    return {
        "schema_version": 1,
        "commands": build_commands(),
        "environment": {
            "CARGO_INCREMENTAL": "0",
            "CARGO_PROFILE_RELEASE_LTO": "false",
            "SOURCE_DATE_EPOCH": "0",
            "ZERO_AR_DATE": "1",
            "rust_codegen_units": 1,
            "path_remaps": logical_remaps(instrument_coverage),
            "path_remap_scope": PATH_REMAP_SCOPE,
            "darwin_linker_no_uuid": tool_identity()["host"].endswith("-darwin"),
        },
        "source_sha256": source_digest(checker_root),
        "cargo_lock_sha256": sha256_file(cargo_lock),
        "cargo_toml_sha256": sha256_file(cargo_toml),
        "tools": tool_identity(),
    }


def build_checker(
    checker_root: Path,
    target_dir: Path,
    instrument_coverage: bool = True,
) -> tuple[Path, dict[str, Any], str]:
    env, _flags = build_environment(checker_root, target_dir, instrument_coverage)
    outputs = []
    for command in build_commands():
        proc = subprocess.run(
            command,
            cwd=checker_root,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        outputs.append(proc.stdout)
        if proc.returncode:
            raise PortableCoverageError(f"portable nanoda build failed:\n{proc.stdout[-4000:]}")
    binary = target_dir / "release" / "nanoda_bin"
    if not binary.is_file():
        raise PortableCoverageError(f"portable build emitted no binary: {binary}")
    identity = build_identity(checker_root, instrument_coverage)
    identity["binary"] = {
        "logical_path": "cargo-target/release/nanoda_bin",
        "sha256": sha256_file(binary),
        "bytes": binary.stat().st_size,
    }
    return binary, identity, "".join(outputs)


def expected_source_ids(checker_root: Path) -> list[str]:
    return sorted(path.relative_to(checker_root).as_posix() for path in (checker_root / "src").rglob("*.rs"))


def _coverage_files(export: dict[str, Any]) -> list[dict[str, Any]]:
    return [item for data in export.get("data", []) for item in data.get("files", [])]


def resolve_checker_source_root(files: list[dict[str, Any]], anchor: str = "src/tc.rs") -> str:
    suffix = f"/{anchor.lstrip('/')}"
    matches = {
        str(item.get("filename", "")).replace("\\", "/")[: -len(suffix)]
        for item in files
        if str(item.get("filename", "")).replace("\\", "/").endswith(suffix)
    }
    if len(matches) != 1:
        raise PortableCoverageError(
            f"expected one embedded checker root from anchor {anchor!r}, found {sorted(matches)}"
        )
    return next(iter(matches))


def canonical_coverage(
    export: dict[str, Any], source_ids: Iterable[str]
) -> tuple[str, list[str]]:
    files = _coverage_files(export)
    embedded_root = resolve_checker_source_root(files)
    expected = set(source_ids)
    by_filename: dict[str, list[dict[str, Any]]] = {}
    for item in files:
        filename = str(item.get("filename", "")).replace("\\", "/")
        by_filename.setdefault(filename, []).append(item)

    covered: set[str] = set()
    mapped_sources = 0
    for source_id in sorted(expected):
        filename = f"{embedded_root}/{source_id}"
        matches = by_filename.get(filename, [])
        if not matches:
            continue
        if len(matches) != 1:
            raise PortableCoverageError(
                f"expected one LLVM mapping for {source_id!r} at {filename!r}, found {len(matches)}"
            )
        mapped_sources += 1
        segments = matches[0].get("segments", [])
        if not segments:
            raise PortableCoverageError(f"LLVM mapping has no segments for {source_id}")
        for segment in segments:
            if len(segment) < 4:
                continue
            line, _column, count, has_count = segment[:4]
            if has_count and int(count) > 0:
                covered.add(f"{source_id}:{int(line)}")
    embedded_prefix = f"{embedded_root}/"
    unknown = sorted(
        filename[len(embedded_prefix) :]
        for filename in by_filename
        if filename.startswith(embedded_prefix)
        and filename[len(embedded_prefix) :] not in expected
    )
    if unknown:
        raise PortableCoverageError(f"LLVM mapping contains unknown checker sources: {unknown}")
    if mapped_sources == 0:
        raise PortableCoverageError("LLVM mapping contains no known checker sources")
    return embedded_root, sorted(covered)


def coverage_digest(locations: Iterable[str]) -> str:
    payload = json.dumps(sorted(set(locations)), separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def validate_sentinel(records: list[dict[str, Any]], test: str, location: str) -> None:
    matches = [row for row in records if row["test"] == test]
    if len(matches) != 1:
        raise PortableCoverageError(
            f"coverage sentinel test {test!r} must occur exactly once, found {len(matches)}"
        )
    if location not in matches[0]["covered"]:
        raise PortableCoverageError(
            f"coverage sentinel {test}:{location} was not covered"
        )
