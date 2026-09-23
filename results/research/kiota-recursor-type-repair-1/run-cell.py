#!/usr/bin/env python3
"""Run one exact, committed Kiota recursor-repair build or test cell.

Every launch revalidates the committed control plane, the complete patched
source inventory, the offline Cargo dependency tree, and the fixed command.
Attempt counts are observations only: a failed cell may be repaired and retried
without a cap, but each process receives a new durable attempt directory.
"""
from __future__ import annotations

import fcntl
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tarfile
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from lib.cvc_process import atomic
from lib.metamorphic_pilot_runner import run_supervised


BASE = ROOT / "results/research/kiota-recursor-type-repair-1"
ITEM = "KIOTA-RECURSOR-TYPE-REPAIR-1"
REVISION = "9fa2c297dd700fe8fd1712a86bdbb258e1c01c42"

FOCUSED_TESTS = (
    "recursor_type_reconstruction_control_accepts",
    "recursor_type_reconstruction_candidate_rejects_exactly",
    "recursor_type_reconstruction_rejection_is_atomic",
    "recursor_type_reconstruction_ordinary_indexed_accepts",
    "recursor_type_reconstruction_two_nested_specializations_accept",
    "recursor_type_reconstruction_deep_parametric_nested_accepts",
    "recursor_type_reconstruction_mutual_nested_accepts",
)

CELL_SPECS: dict[str, dict[str, Any]] = {
    "001-build": {
        "kind": "build",
        "argv": ("test", "--offline", "--locked", "--no-run"),
        "outcome": "BUILD_PASS",
        "tests": (),
    },
    "002-focused": {
        "kind": "test",
        "argv": ("test", "--offline", "--locked", "--test", "exports",
                 "recursor_type_reconstruction", "--", "--nocapture"),
        "outcome": "FOCUSED_PASS",
        "tests": FOCUSED_TESTS,
    },
    "003-candidate": {
        "kind": "test",
        "argv": ("test", "--offline", "--locked", "--test", "exports",
                 FOCUSED_TESTS[1], "--", "--exact", "--nocapture"),
        "outcome": "EXPECTED_REJECT_CONFIRMED",
        "tests": (FOCUSED_TESTS[1],),
    },
    "004-control": {
        "kind": "test",
        "argv": ("test", "--offline", "--locked", "--test", "exports",
                 FOCUSED_TESTS[0], "--", "--exact", "--nocapture"),
        "outcome": "EXPECTED_ACCEPT_CONFIRMED",
        "tests": (FOCUSED_TESTS[0],),
    },
    "005-ordinary": {
        "kind": "test",
        "argv": ("test", "--offline", "--locked", "--test", "exports",
                 FOCUSED_TESTS[3], "--", "--exact", "--nocapture"),
        "outcome": "EXPECTED_ACCEPT_CONFIRMED",
        "tests": (FOCUSED_TESTS[3],),
    },
    "006-nested-two": {
        "kind": "test",
        "argv": ("test", "--offline", "--locked", "--test", "exports",
                 FOCUSED_TESTS[4], "--", "--exact", "--nocapture"),
        "outcome": "EXPECTED_ACCEPT_CONFIRMED",
        "tests": (FOCUSED_TESTS[4],),
    },
    "007-nested-deep": {
        "kind": "test",
        "argv": ("test", "--offline", "--locked", "--test", "exports",
                 FOCUSED_TESTS[5], "--", "--exact", "--nocapture"),
        "outcome": "EXPECTED_ACCEPT_CONFIRMED",
        "tests": (FOCUSED_TESTS[5],),
    },
    "008-nested-mutual": {
        "kind": "test",
        "argv": ("test", "--offline", "--locked", "--test", "exports",
                 FOCUSED_TESTS[6], "--", "--exact", "--nocapture"),
        "outcome": "EXPECTED_ACCEPT_CONFIRMED",
        "tests": (FOCUSED_TESTS[6],),
    },
    "009-full": {
        "kind": "test",
        "argv": ("test", "--offline", "--locked", "--", "--nocapture"),
        "outcome": "FULL_SUITE_PASS",
        "tests": (),
    },
}
CELL_ORDER = tuple(CELL_SPECS)

MANDATORY_BINDING_ROLES = frozenset({
    "supervisor",
    "supervisor_tests",
    "process_supervisor",
    "atomic_helper",
    "protocol",
    "patch_package",
    "patch",
    "patch_review",
    "dependency_lock",
    "runner_review",
    "fixture_manifest",
    "regression_contract",
    "source_archive",
    "python",
    "cargo",
    "rustc",
    "cargo_manifest",
    "cargo_lock",
})

ALLOWED_ENVIRONMENT = frozenset({
    "PATH", "CARGO_HOME", "CARGO_NET_OFFLINE", "CARGO_TARGET_DIR", "RUSTC",
    "RUST_BACKTRACE", "LANG", "LC_ALL", "TMPDIR",
})
REQUIRED_ENVIRONMENT = frozenset({
    "PATH", "CARGO_HOME", "CARGO_NET_OFFLINE", "CARGO_TARGET_DIR", "RUSTC",
    "RUST_BACKTRACE", "LANG",
})

TEST_LINE = re.compile(r"(?m)^test ([^ ]+) \.\.\. ok$")
SUMMARY_LINE = re.compile(
    r"(?m)^test result: (ok|FAILED)\. ([0-9]+) passed; ([0-9]+) failed; "
    r"([0-9]+) ignored; ([0-9]+) measured; ([0-9]+) filtered out;"
)


class RunnerError(ValueError):
    """A fail-closed control-plane or result-classification error."""


def require(test: bool, message: str) -> None:
    if not test:
        raise RunnerError(message)


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha256(path: Path) -> str:
    return digest(path.read_bytes())


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def safe_relative(value: Any, label: str) -> str:
    require(isinstance(value, str) and value != "", f"invalid {label} path")
    path = PurePosixPath(value)
    require(not path.is_absolute() and ".." not in path.parts and "." not in path.parts,
            f"unsafe {label} path: {value}")
    return path.as_posix()


def exact_file(path: Path, row: dict[str, Any], label: str) -> None:
    require(path.is_file(), f"missing {label}: {path}")
    require(not path.is_symlink(), f"symlink is not an exact {label}: {path}")
    require(type(row.get("bytes")) is int and row["bytes"] >= 0,
            f"invalid {label} byte count")
    require(isinstance(row.get("sha256"), str) and len(row["sha256"]) == 64,
            f"invalid {label} hash")
    require(path.stat().st_size == row["bytes"] and sha256(path) == row["sha256"],
            f"stale {label}: {path}")


def committed_bytes(path: Path) -> bytes:
    relative = path.relative_to(ROOT).as_posix()
    try:
        return subprocess.check_output(
            ["git", "show", "HEAD:" + relative], cwd=ROOT, stderr=subprocess.PIPE
        )
    except subprocess.CalledProcessError as error:
        raise RunnerError(f"cannot read committed binding {relative}") from error


def binding_map(manifest: dict[str, Any]) -> dict[str, tuple[dict[str, Any], Path]]:
    rows = manifest.get("bindings")
    require(isinstance(rows, list), "manifest bindings must be a list")
    result: dict[str, tuple[dict[str, Any], Path]] = {}
    for row in rows:
        require(isinstance(row, dict), "invalid binding row")
        role = row.get("role")
        require(isinstance(role, str) and role not in result, "duplicate or missing binding role")
        value = row.get("path")
        require(isinstance(value, str), f"missing path for binding {role}")
        path = Path(value)
        path = path if path.is_absolute() else ROOT / safe_relative(value, role)
        exact_file(path, row, f"{role} binding")
        if not Path(value).is_absolute():
            require(committed_bytes(path) == path.read_bytes(),
                    f"relative binding is not committed exactly: {value}")
        result[role] = (row, path)
    missing = MANDATORY_BINDING_ROLES - set(result)
    require(not missing, "missing mandatory binding roles: " + ", ".join(sorted(missing)))
    return result


def tree_manifest(path: Path) -> tuple[int, str]:
    require(path.is_dir() and not path.is_symlink(), f"invalid dependency directory: {path}")
    files = sorted(candidate for candidate in path.rglob("*") if candidate.is_file())
    require(not any(candidate.is_symlink() for candidate in files),
            f"dependency tree contains a symlink: {path}")
    rows = "".join(
        f"{candidate.relative_to(path).as_posix()}\t{sha256(candidate)}\t{candidate.stat().st_size}\n"
        for candidate in files
    ).encode()
    return len(files), digest(rows)


def verify_dependencies(lock_path: Path, source: Path) -> dict[str, Any]:
    lock = json.loads(lock_path.read_text())
    require(lock.get("schema_version") == 1 and lock.get("item_id") == ITEM,
            "wrong dependency-lock identity")
    cargo_lock = lock.get("cargo_lock")
    require(isinstance(cargo_lock, dict), "dependency lock lacks Cargo.lock binding")
    exact_file(source / "Cargo.lock", cargo_lock, "source Cargo.lock")
    packages = lock.get("packages")
    require(isinstance(packages, list) and packages, "dependency lock has no packages")
    seen: set[tuple[str, str]] = set()
    for package in packages:
        key = (package.get("name"), package.get("version"))
        require(all(isinstance(value, str) and value for value in key) and key not in seen,
                "duplicate or invalid dependency identity")
        seen.add(key)
        count, manifest_hash = tree_manifest(Path(package["source_root"]))
        require(count == package.get("files") and manifest_hash == package.get("manifest_sha256"),
                "dependency source mismatch: " + package["name"])
    return lock


def archive_files(archive: Path, top_level: str) -> dict[str, bytes]:
    require(top_level.endswith("/") and top_level.count("/") == 1,
            "invalid source archive top-level prefix")
    files: dict[str, bytes] = {}
    with tarfile.open(archive, "r:gz") as bundle:
        for member in bundle.getmembers():
            require(member.isdir() or member.isfile(),
                    f"source archive contains a non-file entry: {member.name}")
            if member.isdir():
                continue
            require(member.name.startswith(top_level),
                    f"source archive member outside top-level prefix: {member.name}")
            relative = safe_relative(member.name[len(top_level):], "archive member")
            require(relative not in files, f"duplicate archive member: {relative}")
            stream = bundle.extractfile(member)
            require(stream is not None, f"cannot read archive member: {relative}")
            files[relative] = stream.read()
    require(files, "source archive has no files")
    return files


def verify_frozen_fixtures(bindings: dict[str, tuple[dict[str, Any], Path]],
                           source: Path, package: dict[str, Any]) -> None:
    manifest = json.loads(bindings["fixture_manifest"][1].read_text())
    require(manifest.get("target_revision") == REVISION, "wrong fixture manifest revision")
    rows = manifest.get("accepted_fixture_bindings")
    require(isinstance(rows, list) and len(rows) == 4, "wrong accepted-fixture matrix")
    for row in rows:
        target = source / "tests/fixtures" / Path(row["path"]).name
        exact_file(target, row, "frozen accepted fixture")

    contract = json.loads(bindings["regression_contract"][1].read_text())
    require(contract.get("item_id") == "RECURSOR-TYPE-TRUST-BOUNDARY-1" and
            contract.get("status") == "FROZEN_REPAIR_READINESS",
            "wrong frozen regression-contract identity")
    preserved = contract.get("preserved_pair")
    required = contract.get("required_regression")
    require(isinstance(preserved, dict) and isinstance(required, dict) and
            required.get("candidate_expected") == "REJECT" and
            required.get("control_expected") == "ACCEPT" and
            required.get("candidate_identity") == "PRESERVED_EXACTLY" and
            required.get("control_identity") == "PRESERVED_EXACTLY",
            "wrong frozen candidate/control contract")
    additions = {
        row.get("source_path"): row for row in package["changed_files"]
        if row.get("kind") == "ADDED"
    }
    for role, target_name in (
        ("candidate", "recursor-type-reconstruction.reject.ndjson"),
        ("control", "recursor-type-reconstruction.accept.ndjson"),
    ):
        frozen = preserved.get(role)
        require(isinstance(frozen, dict), f"regression contract lacks {role}")
        added = additions.get(frozen.get("path"))
        require(isinstance(added, dict) and Path(added["path"]).name == target_name and
                added.get("source_bytes") == frozen.get("bytes") and
                added.get("source_sha256") == frozen.get("sha256"),
                f"patch package does not preserve the exact {role}")


def verify_source(package_path: Path, archive_binding: tuple[dict[str, Any], Path],
                  source: Path, protocol: dict[str, Any]) -> dict[str, Any]:
    package = json.loads(package_path.read_text())
    require(package.get("schema_version") == 1 and package.get("item_id") == ITEM,
            "wrong patch-package identity")
    require(package.get("source_revision") == REVISION, "wrong patch-package revision")
    source_archive = package.get("source_archive")
    require(isinstance(source_archive, dict), "patch package lacks source archive")
    archive_row, archive_path = archive_binding
    require(source_archive.get("path") == display_path(archive_path),
            "patch package/archive binding path disagreement")
    require(source_archive.get("bytes") == archive_row.get("bytes") and
            source_archive.get("sha256") == archive_row.get("sha256"),
            "patch package/archive binding digest disagreement")
    top_level = source_archive.get("top_level")
    require(top_level == f"kiota-{REVISION}/", "wrong source archive top level")
    archived = archive_files(archive_path, top_level)

    changes = package.get("changed_files")
    require(isinstance(changes, list) and changes, "patch package has no changed-file ledger")
    allowed = set(protocol.get("intended_patch_paths", [])) | set(protocol.get("intended_test_paths", []))
    rows: dict[str, dict[str, Any]] = {}
    for row in changes:
        require(isinstance(row, dict), "invalid changed-file row")
        relative = safe_relative(row.get("path"), "changed file")
        require(relative not in rows and relative in allowed,
                f"duplicate or unauthorized changed file: {relative}")
        kind = row.get("kind")
        require(kind in ("MODIFIED", "ADDED"), f"invalid change kind: {relative}")
        if kind == "MODIFIED":
            require(relative in archived, f"modified path absent from archive: {relative}")
            require(row.get("base_bytes") == len(archived[relative]) and
                    row.get("base_sha256") == digest(archived[relative]),
                    f"wrong pristine binding: {relative}")
        else:
            require(relative not in archived and row.get("base_bytes") == 0 and
                    row.get("base_sha256") is None,
                    f"wrong added-file base binding: {relative}")
            source_path = ROOT / safe_relative(row.get("source_path"), "added-file source")
            source_row = {
                "bytes": row.get("source_bytes"),
                "sha256": row.get("source_sha256"),
            }
            exact_file(source_path, source_row, "added-file source")
            require(row.get("patched_bytes") == row.get("source_bytes") and
                    row.get("patched_sha256") == row.get("source_sha256"),
                    f"added file is not an exact source copy: {relative}")
        rows[relative] = row

    expected_inventory = set(archived) | {
        relative for relative, row in rows.items() if row["kind"] == "ADDED"
    }
    require(source.is_dir() and not source.is_symlink(), "invalid patched source directory")
    all_nodes = list(source.rglob("*"))
    require(not any(node.is_symlink() for node in all_nodes), "patched source contains a symlink")
    actual_inventory = {
        candidate.relative_to(source).as_posix() for candidate in all_nodes if candidate.is_file()
    }
    require(actual_inventory == expected_inventory, "patched source file inventory mismatch")

    observed_changes: set[str] = set()
    for relative in sorted(expected_inventory):
        current = (source / relative).read_bytes()
        row = rows.get(relative)
        if row is None:
            require(current == archived[relative], "unlisted source modification: " + relative)
            continue
        require(len(current) == row.get("patched_bytes") and
                digest(current) == row.get("patched_sha256"),
                "patched source mismatch: " + relative)
        if row["kind"] == "MODIFIED":
            require(current != archived[relative], "listed modification has unchanged bytes: " + relative)
        observed_changes.add(relative)
    require(observed_changes == set(rows), "changed-file ledger is incomplete")
    require(package.get("changed_paths") in (None, list(rows)),
            "changed_paths disagrees with changed-file ledger order")
    return package


def required_cargo_absences(source: Path, cargo_home: Path) -> set[str]:
    paths: set[str] = set()
    current = source
    while True:
        paths.add(str(current / ".cargo/config"))
        paths.add(str(current / ".cargo/config.toml"))
        if current.parent == current:
            break
        current = current.parent
    paths.add(str(cargo_home / "config"))
    paths.add(str(cargo_home / "config.toml"))
    return paths


def verify_expected_contract(cell: str, expected: Any) -> None:
    require(isinstance(expected, dict), "manifest lacks expected result contract")
    spec = CELL_SPECS[cell]
    require(expected.get("exit") == 0 and expected.get("outcome") == spec["outcome"],
            "wrong expected exit/outcome contract")
    if cell == "001-build":
        return
    if cell == "009-full":
        fields = ("unit_passed", "binary_passed", "integration_passed", "doctest_passed",
                  "total_passed", "failed", "ignored")
        require(all(type(expected.get(field)) is int and expected[field] >= 0 for field in fields),
                "invalid full-suite count contract")
        require(expected["total_passed"] == sum(expected[field] for field in
                ("unit_passed", "binary_passed", "integration_passed", "doctest_passed")),
                "full-suite total does not equal component counts")
        require(expected["failed"] == 0, "full suite must expect zero failures")
        return
    require(expected.get("named_tests") == list(spec["tests"]), "wrong named-test contract")
    for field in ("integration_passed", "failed", "ignored", "filtered_out"):
        require(type(expected.get(field)) is int and expected[field] >= 0,
                f"invalid focused count contract: {field}")
    require(expected["integration_passed"] == len(spec["tests"]) and expected["failed"] == 0,
            "focused pass/fail count differs from fixed cell")


def verify_manifest(cell: str) -> dict[str, Any]:
    require(cell in CELL_SPECS, "fixed cell ID required")
    manifest_path = BASE / "execution" / f"{cell}-manifest.json"
    raw = manifest_path.read_bytes()
    require(committed_bytes(manifest_path) == raw, "execution manifest must be committed exactly")
    manifest = json.loads(raw)
    require(manifest.get("schema_version") == 1 and manifest.get("item_id") == ITEM and
            manifest.get("cell_id") == cell and manifest.get("source_revision") == REVISION,
            "wrong execution-manifest identity")
    bindings = binding_map(manifest)

    require(bindings["supervisor"][1] == Path(__file__).resolve(), "wrong supervisor binding")
    require(bindings["supervisor_tests"][1] == BASE / "test-runner.py",
            "wrong supervisor-test binding")
    require(bindings["process_supervisor"][1] == ROOT / "lib/metamorphic_pilot_runner.py",
            "wrong process-supervisor binding")
    require(bindings["atomic_helper"][1] == ROOT / "lib/cvc_process.py",
            "wrong atomic-helper binding")
    require(bindings["protocol"][1] == BASE / "protocol.json", "wrong protocol binding")
    require(bindings["patch_package"][1] == BASE / "patch-package.json",
            "wrong patch-package binding")
    require(bindings["dependency_lock"][1] == BASE / "dependency-lock.json",
            "wrong dependency-lock binding")
    require(bindings["patch_review"][1] == BASE / "patch-review.json",
            "wrong patch-review binding")
    require(bindings["runner_review"][1] == BASE / "runner-review.json",
            "wrong runner-review binding")
    require(bindings["fixture_manifest"][1] ==
            ROOT / "results/research/kiota-recursor-type-design-1/acceptance-fixtures.json",
            "wrong fixture-manifest binding")
    require(bindings["regression_contract"][1] ==
            ROOT / "results/research/recursor-type-trust-boundary-1/regression-contract.json",
            "wrong regression-contract binding")

    protocol = json.loads(bindings["protocol"][1].read_text())
    require(protocol.get("item_id") == ITEM and protocol.get("status") == "ACTIVE",
            "protocol is not active for this item")
    require(protocol.get("execution_policy") == {
        "attempt_caps": "NONE",
        "accounting": "OBSERVABILITY_ONLY",
        "engineering_failure": "REPAIR_AND_RETRY_WITHIN_ITEM",
        "process_safety": "NONTERMINAL",
    }, "protocol execution policy is not persistent repair-and-retry")

    source = Path(manifest.get("cwd", ""))
    workspace = Path(protocol["workspace"]["path"])
    require(source == workspace / f"kiota-{REVISION}", "wrong exact source workspace")
    require(bindings["cargo_manifest"][1] == source / "Cargo.toml" and
            bindings["cargo_lock"][1] == source / "Cargo.lock",
            "Cargo input bindings are outside the exact source")

    package = verify_source(bindings["patch_package"][1], bindings["source_archive"],
                            source, protocol)
    patch = package.get("patch")
    require(isinstance(patch, dict), "patch package lacks patch binding")
    patch_row, patch_path = bindings["patch"]
    require(patch.get("path") == display_path(patch_path) and
            patch.get("bytes") == patch_row.get("bytes") and
            patch.get("sha256") == patch_row.get("sha256"),
            "patch-package patch binding disagreement")
    require(manifest.get("patch_package_sha256") == bindings["patch_package"][0]["sha256"],
            "manifest patch-package digest disagreement")

    dependency_lock = verify_dependencies(bindings["dependency_lock"][1], source)
    verify_frozen_fixtures(bindings, source, package)

    cargo = bindings["cargo"][1]
    rustc = bindings["rustc"][1]
    python = bindings["python"][1]
    runner_command = manifest.get("runner_command")
    require(runner_command == [str(python), display_path(Path(__file__).resolve()), cell],
            "wrong bound runner command")
    require(os.path.samefile(sys.executable, python), "runner invoked by an unbound Python")
    expected_argv = [str(cargo), *CELL_SPECS[cell]["argv"]]
    require(manifest.get("argv") == expected_argv, "cell command differs from fixed command")

    environment = manifest.get("environment")
    require(isinstance(environment, dict) and REQUIRED_ENVIRONMENT <= set(environment) <= ALLOWED_ENVIRONMENT,
            "invalid or expansive process environment")
    require(environment["CARGO_NET_OFFLINE"] == "true", "Cargo offline mode is not forced")
    require(environment["RUSTC"] == str(rustc), "RUSTC does not select the bound compiler")
    require(environment["PATH"] == f"{cargo.parent}:/usr/bin:/bin:/usr/sbin:/sbin",
            "PATH differs from the fixed offline tool path")
    cargo_home = Path(environment["CARGO_HOME"])
    registry_root = Path(dependency_lock["registry_root"])
    require(registry_root.parents[2] == cargo_home, "CARGO_HOME disagrees with dependency lock")
    target = Path(environment["CARGO_TARGET_DIR"])
    require(target == workspace / "target" and source not in target.parents,
            "Cargo target directory must be the fixed source-external workspace target")

    absent_paths = manifest.get("absent_paths")
    require(isinstance(absent_paths, list) and len(absent_paths) == len(set(absent_paths)),
            "invalid absent-path list")
    required_absent = required_cargo_absences(source, cargo_home)
    require(required_absent <= set(absent_paths), "manifest omits a Cargo config search path")
    for value in absent_paths:
        require(Path(value).is_absolute() and not Path(value).exists(),
                "unbound Cargo configuration exists: " + value)

    limits = protocol["process_safety"]
    if cell == "001-build":
        seconds, memory = limits["build_seconds"], limits["build_memory_bytes"]
    elif cell in ("002-focused", "009-full"):
        seconds, memory = limits["test_seconds_each"], limits["test_memory_bytes_each"]
    else:
        seconds = limits["fixture_cell_seconds_each"]
        memory = limits["fixture_cell_memory_bytes_each"]
    require(manifest.get("timeout_seconds") == seconds and manifest.get("memory_bytes") == memory,
            "cell process limits differ from the active protocol")
    verify_expected_contract(cell, manifest.get("expected"))

    manifest["_path"] = manifest_path
    manifest["_sha256"] = digest(raw)
    return manifest


def receipt_failure(receipt: dict[str, Any]) -> tuple[str, str] | None:
    if receipt.get("memory_monitor_error") is not None:
        return "INFRASTRUCTURE_AUDIT_FAILURE", "resident-memory monitor failed"
    if type(receipt.get("memory_monitor_samples")) is not int or receipt["memory_monitor_samples"] <= 0:
        return "INFRASTRUCTURE_AUDIT_FAILURE", "no process-group RSS sample was recorded"
    maximum = receipt.get("maximum_observed_rss_bytes")
    if type(maximum) is not int or maximum <= 0:
        return "INFRASTRUCTURE_AUDIT_FAILURE", "process-group RSS samples were not positive"
    if receipt.get("memory_exceeded") is True:
        return "PROCESS_SAFETY_FAILURE", "resident-memory ceiling was exceeded"
    if receipt.get("timed_out") is True:
        return "PROCESS_SAFETY_FAILURE", "process timeout was exceeded"
    if receipt.get("cleanup_complete") is not True:
        return "INFRASTRUCTURE_AUDIT_FAILURE", "complete process-group cleanup was not proven"
    if receipt.get("exit_code") != 0:
        return "ENGINEERING_FAILURE", f"Cargo exited {receipt.get('exit_code')!r}"
    return None


def parse_summaries(output: str) -> list[dict[str, int | str]]:
    return [
        {
            "status": match.group(1),
            "passed": int(match.group(2)),
            "failed": int(match.group(3)),
            "ignored": int(match.group(4)),
            "measured": int(match.group(5)),
            "filtered_out": int(match.group(6)),
        }
        for match in SUMMARY_LINE.finditer(output)
    ]


def classify(cell: str, manifest: dict[str, Any], receipt: dict[str, Any],
             stdout: bytes, stderr: bytes) -> tuple[bool, str, str]:
    if (receipt.get("argv") != manifest.get("argv") or
            receipt.get("cwd") != manifest.get("cwd") or
            receipt.get("memory_limit_bytes") != manifest.get("memory_bytes") or
            receipt.get("memory_enforcement") != "per-process-rss-process-group-monitor-v2"):
        return False, "INFRASTRUCTURE_AUDIT_FAILURE", "supervisor receipt differs from the bound request"
    failure = receipt_failure(receipt)
    if failure is not None:
        return False, *failure
    output = (stdout + b"\n" + stderr).decode(errors="replace")
    expected = manifest["expected"]
    if cell == "001-build":
        return True, expected["outcome"], "bound offline Cargo build completed"

    summaries = parse_summaries(output)
    if cell == "009-full":
        if len(summaries) != 4 or any(row["status"] != "ok" for row in summaries):
            return False, "INFRASTRUCTURE_AUDIT_FAILURE", "full-suite output has an unexpected harness layout"
        actual = {
            "unit_passed": summaries[0]["passed"],
            "binary_passed": summaries[1]["passed"],
            "integration_passed": summaries[2]["passed"],
            "doctest_passed": summaries[3]["passed"],
            "total_passed": sum(int(row["passed"]) for row in summaries),
            "failed": sum(int(row["failed"]) for row in summaries),
            "ignored": sum(int(row["ignored"]) for row in summaries),
        }
        wanted = {key: expected[key] for key in actual}
        if actual != wanted:
            return False, "INFRASTRUCTURE_AUDIT_FAILURE", "full-suite counts differ from the bound contract"
        return True, expected["outcome"], "all bound full-suite harness counts matched"

    names = TEST_LINE.findall(output)
    if len(summaries) != 1 or summaries[0]["status"] != "ok":
        return False, "INFRASTRUCTURE_AUDIT_FAILURE", "focused output lacks one successful harness summary"
    actual_summary = summaries[0]
    wanted_summary = {
        "passed": expected["integration_passed"],
        "failed": expected["failed"],
        "ignored": expected["ignored"],
        "filtered_out": expected["filtered_out"],
    }
    if any(actual_summary[key] != value for key, value in wanted_summary.items()):
        return False, "INFRASTRUCTURE_AUDIT_FAILURE", "focused harness counts differ from the bound contract"
    if len(names) != len(expected["named_tests"]) or set(names) != set(expected["named_tests"]):
        return False, "INFRASTRUCTURE_AUDIT_FAILURE", "focused named tests differ from the bound contract"
    return True, expected["outcome"], "bound named tests and harness counts matched"


def new_account() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "item_id": ITEM,
        "policy": {
            "attempt_caps": "NONE",
            "accounting": "OBSERVABILITY_ONLY",
            "engineering_failure": "REPAIR_AND_RETRY_WITHIN_ITEM",
        },
        "next_attempt": 1,
        "observations": {"processes": 0, "builds": 0, "tests": 0},
        "attempts": [],
        "pending": None,
        "safety_hold": None,
    }


def known_prelaunch_failure(reason: Any) -> bool:
    """Return true only for failures proven to precede child creation.

    ``run_supervised`` performs its /bin/ps backend preflight before creating
    pipes or invoking Popen. These exact diagnostics therefore prove that no
    Cargo process exists and need no cleanup hold.
    """
    if not isinstance(reason, str):
        return False
    return any(marker in reason for marker in (
        "memory monitor backend unavailable before launch:",
        "memory monitor backend returned no current-process-group sample",
        "RunnerError: /bin/ps is unavailable",
    ))


def result_receipt_cleanup(result: dict[str, Any]) -> bool:
    value = result.get("receipt")
    if not isinstance(value, str):
        return False
    path = Path(value)
    path = path if path.is_absolute() else ROOT / safe_relative(value, "attempt receipt")
    if not path.is_file():
        return False
    receipt = json.loads(path.read_text())
    return receipt.get("cleanup_complete") is True


def safety_hold_for(result: dict[str, Any]) -> dict[str, Any] | None:
    if result_receipt_cleanup(result) or known_prelaunch_failure(result.get("reason")):
        return None
    return {
        "attempt": result["attempt"],
        "cell_id": result["cell_id"],
        "reason": "PROCESS_ABSENCE_OR_CLEANUP_NOT_PROVEN",
        "result": result["result_path"],
    }


def reconcile_completed_pending(account: dict[str, Any], execution: Path) -> bool:
    """Recover an attempt whose durable result outlived accounting finalization."""
    pending = account.get("pending")
    if pending is None:
        return False
    attempts = account.get("attempts")
    require(isinstance(attempts, list), "accounting attempts must be a list")
    matches = [row for row in attempts if row.get("attempt") == pending]
    require(len(matches) == 1, "pending attempt is not uniquely accounted")
    row = matches[0]
    directory = execution / f"attempt-{pending:06d}-{row.get('cell_id')}"
    result_path = directory / "result.json"
    if not result_path.is_file():
        return False
    result = json.loads(result_path.read_text())
    require(result.get("schema_version") == 1 and result.get("item_id") == ITEM and
            result.get("attempt") == pending and result.get("cell_id") == row.get("cell_id") and
            result.get("manifest_sha256") == row.get("manifest_sha256") and
            result.get("status") in ("PASS", "FAIL"),
            "durable pending-attempt result does not match its reservation")
    relative_result = display_path(result_path)
    result["result_path"] = relative_result
    row["status"] = result["status"]
    row["outcome"] = result.get("outcome")
    row["result"] = relative_result
    account["pending"] = None
    account["safety_hold"] = safety_hold_for(result)
    atomic(execution / "accounting.json", account)
    return True


def validate_account(account: dict[str, Any], execution: Path) -> None:
    require(account.get("schema_version") == 1 and account.get("item_id") == ITEM,
            "wrong accounting identity")
    require(account.get("policy") == new_account()["policy"], "accounting policy changed")
    attempts = account.get("attempts")
    require(isinstance(attempts, list), "accounting attempts must be a list")
    require(account.get("next_attempt") == len(attempts) + 1, "non-contiguous attempt accounting")
    expected_dirs: set[str] = set()
    for number, row in enumerate(attempts, 1):
        require(row.get("attempt") == number and row.get("cell_id") in CELL_SPECS,
                "invalid attempt row")
        expected = f"attempt-{number:06d}-{row['cell_id']}"
        require(row.get("directory") == f"execution/{expected}", "wrong attempt directory binding")
        expected_dirs.add(expected)
        require((execution / expected).is_dir(), "accounted attempt directory is missing")
    actual_dirs = {path.name for path in execution.iterdir()
                   if path.is_dir() and path.name.startswith("attempt-")}
    require(actual_dirs == expected_dirs, "attempt-directory/accounting disagreement")
    observations = account.get("observations")
    require(observations == {
        "processes": len(attempts),
        "builds": sum(row["cell_id"] == "001-build" for row in attempts),
        "tests": sum(row["cell_id"] != "001-build" for row in attempts),
    }, "observational process counts disagree with attempts")
    pending = account.get("pending")
    if pending is not None:
        require(attempts and pending == attempts[-1]["attempt"] and
                attempts[-1].get("status") == "RESERVED",
                "invalid pending attempt")
    hold = account.get("safety_hold")
    if hold is not None:
        require(isinstance(hold, dict) and hold.get("reason") ==
                "PROCESS_ABSENCE_OR_CLEANUP_NOT_PROVEN",
                "invalid process-safety hold")
        matches = [row for row in attempts if row.get("attempt") == hold.get("attempt")]
        require(len(matches) == 1 and matches[0].get("cell_id") == hold.get("cell_id") and
                matches[0].get("status") == "FAIL" and matches[0].get("result") == hold.get("result"),
                "process-safety hold does not bind one failed attempt")


def load_account(execution: Path) -> dict[str, Any]:
    path = execution / "accounting.json"
    if path.exists():
        account = json.loads(path.read_text())
        account.setdefault("safety_hold", None)
        reconcile_completed_pending(account, execution)
    else:
        require(not any(candidate.is_dir() and candidate.name.startswith("attempt-")
                        for candidate in execution.iterdir()),
                "attempt directories exist without accounting")
        account = new_account()
    validate_account(account, execution)
    return account


def validate_sequence(account: dict[str, Any], cell: str) -> None:
    require(account.get("pending") is None,
            "a prior attempt lacks proven cleanup and reconciliation")
    require(account.get("safety_hold") is None,
            "a prior attempt has no proof of process absence or complete cleanup")
    successful = {row["cell_id"] for row in account["attempts"] if row.get("status") == "PASS"}
    predecessors = CELL_ORDER[:CELL_ORDER.index(cell)]
    missing = [candidate for candidate in predecessors if candidate not in successful]
    require(not missing, "earlier fixed cells have not passed: " + ", ".join(missing))


def reserve(account: dict[str, Any], cell: str, manifest: dict[str, Any],
            execution: Path) -> tuple[dict[str, Any], Path]:
    validate_sequence(account, cell)
    number = account["next_attempt"]
    name = f"attempt-{number:06d}-{cell}"
    directory = execution / name
    directory.mkdir(exist_ok=False)
    row = {
        "attempt": number,
        "cell_id": cell,
        "directory": f"execution/{name}",
        "manifest": display_path(manifest["_path"]),
        "manifest_sha256": manifest["_sha256"],
        "status": "RESERVED",
    }
    atomic(directory / "reservation.json", row)
    account["attempts"].append(row)
    account["next_attempt"] += 1
    account["observations"]["processes"] += 1
    account["observations"]["builds" if cell == "001-build" else "tests"] += 1
    account["pending"] = number
    atomic(execution / "accounting.json", account)
    return row, directory


def execute_cell(cell: str) -> dict[str, Any]:
    manifest = verify_manifest(cell)
    execution = BASE / "execution"
    execution.mkdir(exist_ok=True)
    account = load_account(execution)
    row, directory = reserve(account, cell, manifest, execution)
    raw_prefix = directory / "raw"
    receipt: dict[str, Any] | None = None
    try:
        receipt = run_supervised(
            argv=manifest["argv"],
            cwd=Path(manifest["cwd"]),
            stdin=None,
            env=manifest["environment"],
            timeout_seconds=manifest["timeout_seconds"],
            memory_bytes=manifest["memory_bytes"],
            raw_prefix=raw_prefix,
        )
        atomic(directory / "supervisor.json", receipt)
        stdout_path = Path(str(raw_prefix) + ".stdout")
        stderr_path = Path(str(raw_prefix) + ".stderr")
        require(stdout_path.is_file() and stderr_path.is_file(), "supervisor omitted raw output")
        passed, outcome, reason = classify(
            cell, manifest, receipt, stdout_path.read_bytes(), stderr_path.read_bytes()
        )
    except BaseException as error:
        passed = False
        outcome = "INFRASTRUCTURE_AUDIT_FAILURE"
        reason = f"{type(error).__name__}: {error}"
    result = {
        "schema_version": 1,
        "item_id": ITEM,
        "attempt": row["attempt"],
        "cell_id": cell,
        "manifest": row["manifest"],
        "manifest_sha256": row["manifest_sha256"],
        "status": "PASS" if passed else "FAIL",
        "outcome": outcome,
        "reason": reason,
        "receipt": display_path(directory / "supervisor.json") if receipt is not None else None,
        "raw_stdout": display_path(Path(str(raw_prefix) + ".stdout")),
        "raw_stderr": display_path(Path(str(raw_prefix) + ".stderr")),
    }
    result["result_path"] = display_path(directory / "result.json")
    atomic(directory / "result.json", result)
    row["status"] = result["status"]
    row["outcome"] = outcome
    row["result"] = result["result_path"]
    account["pending"] = None
    account["safety_hold"] = safety_hold_for(result)
    atomic(execution / "accounting.json", account)
    return result


def main(argv: list[str] | None = None) -> int:
    arguments = sys.argv[1:] if argv is None else argv
    require(len(arguments) == 1 and arguments[0] in CELL_SPECS, "fixed cell ID required")
    execution = BASE / "execution"
    execution.mkdir(exist_ok=True)
    with (execution / ".launch.lock").open("a") as owner_lock:
        fcntl.flock(owner_lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        result = execute_cell(arguments[0])
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
