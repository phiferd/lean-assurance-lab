#!/usr/bin/env python3
"""Build and bind the exact selected Nanoda revision under supervision."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from lib.resource_envelope_supervisor import run_direct

RUN = Path(__file__).resolve().parent
SOURCE_REPO = ROOT / "external" / "comparator-screen-nanoda"
COMMIT = "0da9f98feadd3a0a2ef4b3dbcf52a298a6fef929"
ARCHIVE = RUN / "nanoda-source.tar"
BINARY = RUN / "nanoda.bin"
CONFIG = RUN / "config.json"
CARGO = Path("/opt/homebrew/bin/cargo")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def supervision_fault(receipt: dict[str, object]) -> bool:
    return bool(
        receipt["accounting_error"] or receipt["monitor_errors"]
        or receipt["pipe_errors"] or receipt["cleanup_errors"]
        or receipt["trace_gap_fault"] or not receipt["reap_complete"]
        or not receipt["cleanup_complete"]
    )


def main() -> None:
    result_path = RUN / "nanoda-build.json"
    if any(path.exists() for path in (BINARY, result_path)):
        raise RuntimeError("refusing to overwrite retained Nanoda build artifacts")
    subprocess.run(
        ["git", "-C", str(SOURCE_REPO), "cat-file", "-e", COMMIT + "^{commit}"],
        check=True,
    )
    if not ARCHIVE.exists():
        subprocess.run(
            ["git", "-C", str(SOURCE_REPO), "archive", "--format=tar",
             "--output", str(ARCHIVE), COMMIT],
            check=True,
        )
    attempt = RUN / "attempts" / "nanoda-build-r2"
    attempt.mkdir(parents=True, exist_ok=False)
    build_root = Path(tempfile.mkdtemp(prefix="lal-nanoda-capture-", dir="/private/tmp"))
    try:
        with tarfile.open(ARCHIVE, "r") as archive:
            archive.extractall(build_root)
        env = dict(os.environ)
        env["CARGO_TARGET_DIR"] = str(build_root / "target")
        supervised = run_direct(
            argv=[str(CARGO), "build", "--release", "--locked"],
            cwd=build_root, env=env, stdin_bytes=None,
            timeout_seconds=600, memory_ceiling_bytes=4 * 1024**3,
            sample_interval_seconds=1, max_trace_gap_seconds=10,
            cleanup_seconds=10, output_cap_bytes=20 * 1024**2,
        )
        (attempt / "stdout.log").write_bytes(supervised.stdout)
        (attempt / "stderr.log").write_bytes(supervised.stderr)
        save(attempt / "receipt.json", supervised.receipt)
        if supervision_fault(supervised.receipt):
            raise RuntimeError("Nanoda build supervision fault")
        if supervised.receipt["exit_code"] != 0:
            raise RuntimeError("Nanoda build failed")
        built = build_root / "target" / "release" / "nanoda_bin"
        if not built.is_file():
            raise RuntimeError("Nanoda build did not produce nanoda_bin")
        shutil.copyfile(built, BINARY)
        BINARY.chmod(0o755)
    finally:
        shutil.rmtree(build_root, ignore_errors=True)
    cargo_version = subprocess.run(
        [str(CARGO), "--version"], check=True, text=True,
        stdout=subprocess.PIPE,
    ).stdout.strip()
    rustc_version = subprocess.run(
        ["rustc", "--version"], check=True, text=True,
        stdout=subprocess.PIPE,
    ).stdout.strip()
    record = {
        "schema_version": 1,
        "repository": "https://github.com/ammkrn/nanoda_lib.git",
        "commit": COMMIT,
        "source_archive": {"path": str(ARCHIVE.relative_to(ROOT)),
                           "sha256": sha(ARCHIVE), "bytes": ARCHIVE.stat().st_size},
        "cargo_lock_sha256": hashlib.sha256(subprocess.run(
            ["git", "-C", str(SOURCE_REPO), "show", f"{COMMIT}:Cargo.lock"],
            check=True, stdout=subprocess.PIPE,
        ).stdout).hexdigest(),
        "binary": {"path": str(BINARY.relative_to(ROOT)),
                   "sha256": sha(BINARY), "bytes": BINARY.stat().st_size},
        "config": {"path": str(CONFIG.relative_to(ROOT)),
                   "sha256": sha(CONFIG), "bytes": CONFIG.stat().st_size},
        "toolchain": {"cargo": cargo_version, "rustc": rustc_version},
        "build_attempt": str(attempt.relative_to(ROOT)),
        "repair": "Retained build r1 stopped before Cargo because the host Python tarfile API lacks the newer filter argument. Revision r2 extracts the trusted exact git archive with the host-compatible API.",
        "temporary_tree_removed": not build_root.exists(),
    }
    save(result_path, record)
    print(json.dumps(record, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
