#!/usr/bin/env python3
"""Generate the immutable E1 source, runner, fixture, and launch manifest."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SOURCE_REPO = Path("/workspace/shared/lean4-pr15373-source")
HEAD_TREE = Path("/workspace/shared/lean4-pr15373-head")
PARENT_TREE = Path("/workspace/shared/lean4-pr15373-parent")
HEAD_REV = "015d54649bcaaa0861f355b59761ce308e629fbb"
PARENT_REV = "2c2bdd9630a7a6c51d7620d5efefcdba104f38f3"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def output(
    argv: list[str], cwd: Path | None = None, env: dict[str, str] | None = None
) -> str:
    return subprocess.check_output(argv, cwd=cwd, env=env, text=True).strip()


def identity(revision: str) -> dict[str, str]:
    commit = output(["git", "rev-parse", f"{revision}^{{commit}}"], SOURCE_REPO)
    tree = output(["git", "rev-parse", f"{revision}^{{tree}}"], SOURCE_REPO)
    listing = output(["git", "ls-tree", "-r", "--full-tree", revision], SOURCE_REPO)
    return {
        "commit": commit,
        "tree": tree,
        "recursive_tree_listing_sha256": hashlib.sha256((listing + "\n").encode()).hexdigest(),
    }


def resolved_ldd(binary: Path) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for line in output(["ldd", str(binary)]).splitlines():
        match = re.search(r"=>\s+(/\S+)\s+\(", line)
        if match is None:
            match = re.match(r"\s*(/\S+)\s+\(", line)
        if match is None:
            continue
        path = Path(match.group(1)).resolve()
        records.append({"path": str(path), "sha256": sha256(path)})
    return sorted(records, key=lambda item: item["path"])


def runner(label: str, tree: Path, revision: str) -> dict[str, object]:
    lean = tree / "build/release/stage1/bin/lean"
    shared = tree / "build/release/stage1/lib/lean/libleanshared.so"
    if not lean.is_file() or not shared.is_file():
        raise SystemExit(f"missing completed {label} runner")
    if output(["git", "rev-parse", "HEAD"], tree) != revision:
        raise SystemExit(f"{label} worktree revision changed")
    if output(["git", "status", "--porcelain"], tree):
        raise SystemExit(f"{label} source worktree is dirty")
    env = dict(os.environ)
    env["LD_LIBRARY_PATH"] = os.pathsep.join(
        ["/workspace/shared/lean-deps/lib", str(lean.parents[1] / "lib")]
    )
    return {
        "label": label,
        "source_revision": revision,
        "source_tree": output(["git", "rev-parse", "HEAD^{tree}"], tree),
        "lean_binary": {"path": str(lean), "sha256": sha256(lean)},
        "lean_version": output([str(lean), "--version"], env=env),
        "libleanshared": {"path": str(shared), "sha256": sha256(shared)},
        "dynamic_dependencies": resolved_ldd(lean),
    }


def relative_hashes(paths: list[Path]) -> dict[str, str]:
    return {str(path.relative_to(ROOT)): sha256(path) for path in sorted(paths)}


def receipt_hashes(names: list[str]) -> dict[str, str]:
    return {
        name: sha256(HERE / "attempts" / name / "receipt.json")
        for name in names
    }


def main() -> None:
    fixture = HERE / "fixture"
    prepared = HERE / "prepared"
    fixture_sources = list(fixture.glob("*.lean"))
    generated = list(prepared.glob("*/*.olean"))
    if len(generated) != 4:
        raise SystemExit("expected exactly four separately compiled fixture oleans")

    source_manifest = {
        "schema_version": 1,
        "repository": "https://github.com/leanprover/lean4",
        "head": identity(HEAD_REV),
        "parent": identity(PARENT_REV),
        "retained_exact_source": relative_hashes(list((HERE / "source").glob("*"))),
        "build_method": {
            "configure": "cmake --preset release -DUSE_GMP=OFF",
            "build": "make -j4 -C build/release",
            "cmake_version": output(["/workspace/shared/lean-build-tools/bin/cmake", "--version"]).splitlines()[0],
            "ninja_version": output(["/workspace/shared/lean-build-tools/bin/ninja", "--version"]),
            "gcc_version": output(["gcc", "--version"]).splitlines()[0],
            "libuv_revision": output(["git", "rev-parse", "HEAD"], Path("/workspace/shared/libuv-v1.51.0")),
            "libuv_shared_sha256": sha256(Path("/workspace/shared/lean-deps/lib/libuv.so.1.0.0")),
            "environment": {
                "CMAKE_PREFIX_PATH": "/workspace/shared/lean-deps",
                "PKG_CONFIG_PATH": "/workspace/shared/lean-deps/lib/pkgconfig",
                "USE_GMP": "OFF",
            },
            "identity_repair": {
                "reason": "Lean's bundled CMake helper reads the common-repository HEAD for a detached Git worktree, so the first completed binaries self-reported ref: refs/heads/master. The generated stage1 githash.h in each isolated build was replaced with that worktree's already-frozen 40-byte commit and the lean and leanshared targets were rebuilt identically.",
                "head_githash": HEAD_REV,
                "parent_githash": PARENT_REV,
                "targets": ["lean", "leanshared"],
            },
        },
        "successful_preparation_receipts": receipt_hashes([
            "head-build-3",
            "parent-build-1",
            "head-identity-repair-2",
            "parent-identity-repair-2",
            "head-identity-2",
            "parent-identity-2",
            "head-support-build-1",
            "parent-support-build-1",
            "head-harness-build-1",
            "parent-harness-build-1",
        ]),
        "retained_failed_preparation_attempts": [
            "head-build-1",
            "head-build-2",
            "head-identity-1",
            "parent-identity-1",
            "head-identity-repair-1",
            "parent-identity-repair-1"
        ],
    }
    (HERE / "source-manifest.json").write_text(
        json.dumps(source_manifest, indent=2, sort_keys=True) + "\n"
    )

    launch = {
        "schema_version": 1,
        "evidence_class": "E1",
        "experiment_id": "CONFIRM-LEAN-ETA-ADMISSION-1",
        "source_manifest_sha256": sha256(HERE / "source-manifest.json"),
        "expected_sha256": sha256(HERE / "expected.json"),
        "fixture_sources": relative_hashes(fixture_sources),
        "generated_oleans": relative_hashes(generated),
        "cell_runner_sha256": sha256(HERE / "run-cell.py"),
        "runners": {
            "head": runner("head", HEAD_TREE, HEAD_REV),
            "parent": runner("parent", PARENT_TREE, PARENT_REV),
        },
        "matrix": [
            {"id": "head-alias", "runner": "head", "cell": "alias-cell.lean"},
            {"id": "head-explicit", "runner": "head", "cell": "explicit-cell.lean"},
            {"id": "parent-alias", "runner": "parent", "cell": "alias-cell.lean"},
            {"id": "parent-explicit", "runner": "parent", "cell": "explicit-cell.lean"},
        ],
        "cell_supervision": {
            "timeout_seconds": 600,
            "memory_ceiling_bytes": 4294967296,
            "sample_interval_seconds": 1,
            "max_trace_gap_seconds": 5,
            "cleanup_seconds": 10,
            "output_cap_bytes": 20971520,
        },
        "launch_invariants": [
            "fresh process per cell",
            "trust level zero via -t 0",
            "compile source independently under each runner",
            "no generated olean crosses runner directories",
            "explicit doCheck true",
            "semantic Kernel.Exception only may count as REJECT",
            "accepted declaration stored type and value equal submitted expressions",
        ],
    }
    (HERE / "launch-manifest.json").write_text(
        json.dumps(launch, indent=2, sort_keys=True) + "\n"
    )


if __name__ == "__main__":
    main()
