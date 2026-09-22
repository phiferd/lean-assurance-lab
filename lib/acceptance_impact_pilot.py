"""Guarded build and Stage-1 execution for ACCEPTANCE-IMPACT-PILOT-1."""
from __future__ import annotations

from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any, Callable, Iterator

from lib.cvc_prep import committed
from lib.metamorphic_pilot_runner import run_supervised
from lib import acceptance_impact_pair as pair_audit
from lib import acceptance_impact_source as source


ROOT = Path(__file__).resolve().parents[1]
ITEM = "ACCEPTANCE-IMPACT-PILOT-1"
BASE = Path("results/research/acceptance-impact-pilot-1")
DESIGN = BASE / "stage-1-design.json"
PAIR_AUDIT = BASE / "pair-audit.json"
BUILD_MANIFEST = BASE / "build-manifest.json"
BUILD_DIR = BASE / "build-0001"
BUILD_RESULT = BUILD_DIR / "result.json"
EXECUTION_MANIFEST = BASE / "stage-1-execution-manifest.json"
RUN_DIR = BASE / "stage-1-run-0001"
RUN_RESULT = RUN_DIR / "result.json"
PROTOCOL = BASE / "protocol.json"
WORK = BASE / "work-record.json"
PLAN = Path("docs/research/ACCEPTANCE_IMPACT_PILOT_1_PLAN.md")
QUEUE = Path("config/research-queue.json")
STATUS = Path("docs/RESEARCH_STATUS.md")

MODULE = Path("lib/acceptance_impact_pilot.py")
SOURCE_MODULE = Path("lib/acceptance_impact_source.py")
PAIR_MODULE = Path("lib/acceptance_impact_pair.py")
SUPERVISOR = Path("lib/metamorphic_pilot_runner.py")
BUILD_SCRIPT = Path("scripts/build-acceptance-impact-target")
EXECUTE_SCRIPT = Path("scripts/execute-acceptance-impact-stage-1")
VALIDATE_SCRIPT = Path("scripts/validate-acceptance-impact-pilot-1")
SOURCE_SCRIPT = Path("scripts/prepare-acceptance-impact-source")
PAIR_SCRIPT = Path("scripts/build-acceptance-impact-pair-audit")
TEST = Path("tests/test_acceptance_impact_pilot.py")
SOURCE_TEST = Path("tests/test_acceptance_impact_source.py")
PAIR_TEST = Path("tests/test_acceptance_impact_pair.py")

PS = Path("/bin/ps")
PS_BYTES = 170816
PS_SHA256 = "57b93ca9ccbeb77e261f0792e9722eb44189dd81a81e26a90280a73a2f5a73bb"
OFFICIAL = Path("external/lean-kernel-arena/_build/checkers/official/src/.lake/build/bin/kernel")
OFFICIAL_BYTES = 100401632
OFFICIAL_SHA256 = "87efe83ae56410a4689b49ff5276dd9663fc85ae3641849d123b5fcef1692585"
OFFICIAL_DEFINITION = Path("external/lean-kernel-arena/checkers/official.yaml")
OFFICIAL_DEFINITION_BYTES = 214
OFFICIAL_DEFINITION_SHA256 = "4463cc2522d3a4f474515dc6781c193bc0e69e9b358a37ce11f0bb2eba9e556a"
OFFICIAL_TOOLCHAIN = Path("external/lean-kernel-arena/_build/checkers/official/src/lean-toolchain")
OFFICIAL_TOOLCHAIN_BYTES = 25
OFFICIAL_TOOLCHAIN_SHA256 = "302cd63c54178885b89e669f33b38f12f4dd7ae7e5cac537b3203e3768d8fb2b"

EXPECTED_CELLS = [
    {"ordinal": 1, "cell_id": "kiota-9fa2c297::control", "profile_id": "kiota-9fa2c297", "artifact_id": "control"},
    {"ordinal": 2, "cell_id": "kiota-9fa2c297::candidate", "profile_id": "kiota-9fa2c297", "artifact_id": "candidate"},
    {"ordinal": 3, "cell_id": "official-lean-4.33.0::control", "profile_id": "official-lean-4.33.0", "artifact_id": "control"},
    {"ordinal": 4, "cell_id": "official-lean-4.33.0::candidate", "profile_id": "official-lean-4.33.0", "artifact_id": "candidate"},
]
EXPECTED_GATE = {
    "kiota-9fa2c297::control": "ACCEPT",
    "kiota-9fa2c297::candidate": "ACCEPT",
    "official-lean-4.33.0::control": "ACCEPT",
    "official-lean-4.33.0::candidate": "INTENDED_RECURSOR_REJECT",
}


class PilotError(ValueError):
    pass


def _pairs(rows: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in rows:
        if key in result:
            raise PilotError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_pairs,
                          parse_constant=lambda value: (_ for _ in ()).throw(
                              PilotError(f"non-finite JSON value: {value}")))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise PilotError(f"cannot load JSON {path}: {error}") from error


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def binding(path: Path, root: Path = ROOT) -> dict[str, Any]:
    absolute = path if path.is_absolute() else root / path
    if not absolute.is_file() or absolute.is_symlink():
        raise PilotError(f"bound file is missing or linked: {path}")
    try:
        name = absolute.relative_to(root).as_posix()
    except ValueError:
        name = str(absolute)
    return {"path": name, "bytes": absolute.stat().st_size, "sha256": sha256(absolute)}


def verify_binding(row: Any, root: Path = ROOT) -> Path:
    if (not isinstance(row, dict) or set(row) != {"path", "bytes", "sha256"}
            or type(row["bytes"]) is not int or row["bytes"] < 0
            or not isinstance(row["sha256"], str)
            or re.fullmatch(r"[0-9a-f]{64}", row["sha256"]) is None):
        raise PilotError("invalid file binding")
    path = Path(row["path"])
    absolute = path if path.is_absolute() else root / path
    if (not absolute.is_file() or absolute.is_symlink()
            or absolute.stat().st_size != row["bytes"] or sha256(absolute) != row["sha256"]):
        raise PilotError(f"stale file binding: {row['path']}")
    return absolute


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    temporary = path.with_name(path.name + ".tmp")
    if temporary.exists() or temporary.is_symlink():
        raise PilotError(f"temporary output exists: {temporary}")
    with temporary.open("xb") as output:
        output.write(raw)
        output.flush()
        os.fsync(output.fileno())
    os.replace(temporary, path)


def _active(root: Path) -> None:
    protocol = load_json(root / PROTOCOL)
    queue = load_json(root / QUEUE)
    if protocol.get("item_id") != ITEM or protocol.get("status") != "ACTIVE":
        raise PilotError("pilot protocol is not ACTIVE")
    items = {row.get("id"): row for row in queue.get("items", []) if isinstance(row, dict)}
    if queue.get("selected_item") != ITEM or items.get(ITEM, {}).get("status") != "ACTIVE":
        raise PilotError("research queue does not select the ACTIVE pilot")


def _exact_binding(path: Path, size: int, digest: str, root: Path = ROOT) -> dict[str, Any]:
    row = binding(path, root)
    if row["bytes"] != size or row["sha256"] != digest:
        raise PilotError(f"exact external binding differs: {path}")
    return row


def _tooling(root: Path) -> list[dict[str, Any]]:
    return [binding(path, root) for path in (
        MODULE, SOURCE_MODULE, PAIR_MODULE, SUPERVISOR, BUILD_SCRIPT, EXECUTE_SCRIPT,
        VALIDATE_SCRIPT, SOURCE_SCRIPT, PAIR_SCRIPT, TEST, SOURCE_TEST, PAIR_TEST,
    )]


def _absent_cargo_config(root: Path) -> list[str]:
    source_dir = (root / source.SOURCE_DIR).resolve()
    cargo_home = Path("/Users/danphifer/.cargo")
    bases = [source_dir, *(source_dir.parents)]
    candidates: list[Path] = []
    for base in bases:
        candidates.extend((base / ".cargo/config", base / ".cargo/config.toml"))
        if base == Path("/"):
            break
    candidates.extend((cargo_home / "config", cargo_home / "config.toml"))
    unique = []
    for path in candidates:
        name = str(path)
        if name not in unique:
            unique.append(name)
    return unique


def make_build_manifest(root: Path = ROOT) -> dict[str, Any]:
    root = Path(root).resolve()
    _active(root)
    design = load_json(root / DESIGN)
    if design.get("cells") != EXPECTED_CELLS:
        raise PilotError("Stage-1 design cells differ")
    pair_audit.check(root)
    environment = dict(design["build_contract"]["environment"])
    environment["CARGO_TARGET_DIR"] = str((root / source.TARGET_DIR).resolve())
    absent = _absent_cargo_config(root)
    if any(Path(path).exists() for path in absent):
        raise PilotError("unbound Cargo configuration exists")
    return {
        "schema_version": 1,
        "item_id": ITEM,
        "kind": "PLAIN_RELEASE_BUILD",
        "source_revision": source.SOURCE_REVISION,
        "source_directory": source.SOURCE_DIR.as_posix(),
        "target_directory": source.TARGET_DIR.as_posix(),
        "output_binary": source.KIOTA_BINARY.as_posix(),
        "argv": design["build_contract"]["argv"],
        "environment": environment,
        "required_absent_environment": design["build_contract"]["required_absent_environment"],
        "required_absent_paths": absent,
        "timeout_seconds": 1200,
        "memory_bytes": 4294967296,
        "inputs": {
            "design": binding(DESIGN, root),
            "pair_audit": binding(PAIR_AUDIT, root),
            "source_lock": binding(source.SOURCE_LOCK, root),
            "archive": binding(source.ARCHIVE, root),
            "dependency_lock": binding(source.DEPENDENCY_LOCK, root),
            "cargo": _exact_binding(source.CARGO, source.CARGO_BYTES, source.CARGO_SHA256, root),
            "rustc": _exact_binding(source.RUSTC, source.RUSTC_BYTES, source.RUSTC_SHA256, root),
            "ps": _exact_binding(PS, PS_BYTES, PS_SHA256, root),
        },
        "tooling": _tooling(root),
        "source_edits": False,
        "scientific_checker_observations": 0,
    }


def freeze_build_manifest(root: Path = ROOT) -> dict[str, Any]:
    root = Path(root).resolve()
    path = root / BUILD_MANIFEST
    value = make_build_manifest(root)
    if path.exists():
        if path.read_bytes() != (json.dumps(value, indent=2, sort_keys=True) + "\n").encode():
            raise PilotError("existing build manifest differs")
    else:
        _write_json(path, value)
    return value


def validate_build_manifest(root: Path = ROOT, *, require_commit: bool = True) -> dict[str, Any]:
    root = Path(root).resolve()
    path = root / BUILD_MANIFEST
    actual = load_json(path)
    expected = make_build_manifest(root)
    if actual != expected:
        raise PilotError("build manifest is stale")
    if require_commit:
        committed(root, BUILD_MANIFEST.as_posix())
        for row in actual["tooling"]:
            if not Path(row["path"]).is_absolute():
                committed(root, row["path"])
        for name in (DESIGN, PAIR_AUDIT, PROTOCOL, WORK, PLAN, QUEUE, STATUS):
            committed(root, name.as_posix())
    return actual


def _safe_receipt(receipt: dict[str, Any], label: str) -> None:
    if receipt.get("memory_monitor_error"):
        raise PilotError(f"{label} memory monitor failed; repair before retry")
    if type(receipt.get("memory_monitor_samples")) is not int or receipt["memory_monitor_samples"] <= 0:
        raise PilotError(f"{label} lacks positive sampling; repair before retry")
    if type(receipt.get("maximum_observed_rss_bytes")) is not int or receipt["maximum_observed_rss_bytes"] <= 0:
        raise PilotError(f"{label} lacks positive RSS; repair before retry")
    if receipt.get("memory_exceeded") or receipt.get("timed_out"):
        raise PilotError(f"{label} hit a process safety control; diagnose before retry")
    if not receipt.get("cleanup_complete"):
        raise PilotError(f"{label} cleanup is incomplete; repair before retry")


def _verify_raw(receipt: dict[str, Any], root: Path = ROOT) -> tuple[bytes, bytes]:
    values = []
    for kind in ("stdout", "stderr"):
        path = root / receipt[f"raw_{kind}_path"]
        if (not path.is_file() or path.is_symlink() or path.stat().st_size != receipt[f"{kind}_bytes"]
                or sha256(path) != receipt[f"{kind}_sha256"]):
            raise PilotError(f"raw {kind} receipt differs")
        values.append(path.read_bytes())
    return values[0], values[1]


def _build_environment(manifest: dict[str, Any]) -> dict[str, str]:
    environment = {key: str(value) for key, value in manifest["environment"].items()}
    for key in manifest["required_absent_environment"]:
        if key in environment:
            raise PilotError(f"required-absent environment key is set: {key}")
    return environment


def build_target(root: Path = ROOT,
                 runner: Callable[..., dict[str, Any]] = run_supervised) -> dict[str, Any]:
    root = Path(root).resolve()
    manifest = validate_build_manifest(root, require_commit=True)
    prepared = source.prepare_source(root)
    if prepared.get("checker_observations") != 0:
        raise PilotError("source preparation launched an observer")
    if any(Path(path).exists() for path in manifest["required_absent_paths"]):
        raise PilotError("unbound Cargo configuration appeared")
    run_dir = root / BUILD_DIR
    if run_dir.exists() or (root / source.TARGET_DIR).exists():
        raise PilotError("refuse to overwrite a build attempt")
    run_dir.mkdir(parents=True)
    raw_prefix = run_dir / "raw/build"
    receipt = runner(
        argv=manifest["argv"], cwd=root / source.SOURCE_DIR, stdin=None,
        env=_build_environment(manifest), timeout_seconds=manifest["timeout_seconds"],
        memory_bytes=manifest["memory_bytes"], raw_prefix=raw_prefix,
    )
    stdout, stderr = _verify_raw(receipt, root)
    result: dict[str, Any] = {
        "schema_version": 1,
        "item_id": ITEM,
        "build_manifest": binding(BUILD_MANIFEST, root),
        "receipt": receipt,
        "stdout_empty": stdout == b"",
        "stderr_empty": stderr == b"",
        "status": "FAILED",
    }
    binary = root / source.KIOTA_BINARY
    if receipt.get("exit_code") == 0 and binary.is_file() and not binary.is_symlink():
        result["binary"] = binding(source.KIOTA_BINARY, root)
        result["source_after_build"] = source.verify_source_tree(source.SOURCE_DIR, root)
        result["status"] = "PASS"
    _write_json(root / BUILD_RESULT, result)
    _safe_receipt(receipt, "Kiota build")
    if result["status"] != "PASS":
        raise PilotError("Kiota build failed; preserve receipt and repair")
    return result


def validate_build_result(root: Path = ROOT, *, require_commit: bool = False) -> dict[str, Any]:
    root = Path(root).resolve()
    result = load_json(root / BUILD_RESULT)
    if result.get("item_id") != ITEM or result.get("status") != "PASS":
        raise PilotError("build result is not PASS")
    verify_binding(result["build_manifest"], root)
    verify_binding(result["binary"], root)
    receipt = result.get("receipt")
    if not isinstance(receipt, dict):
        raise PilotError("build result lacks receipt")
    _verify_raw(receipt, root)
    _safe_receipt(receipt, "Kiota build")
    source.verify_source_tree(source.SOURCE_DIR, root)
    if require_commit:
        for path in (BUILD_RESULT, Path(receipt["raw_stdout_path"]), Path(receipt["raw_stderr_path"])):
            committed(root, path.as_posix())
    return result


def make_execution_manifest(root: Path = ROOT) -> dict[str, Any]:
    root = Path(root).resolve()
    _active(root)
    build = validate_build_result(root, require_commit=True)
    pair_audit.check(root)
    official = _exact_binding(OFFICIAL, OFFICIAL_BYTES, OFFICIAL_SHA256, root)
    return {
        "schema_version": 1,
        "item_id": ITEM,
        "stage": "CURRENT_PREMISE_REPRODUCTION",
        "launch_owner": "root",
        "run_directory": RUN_DIR.as_posix(),
        "artifacts": {"control": dict(pair_audit.CONTROL), "candidate": dict(pair_audit.CANDIDATE)},
        "pair_audit": binding(PAIR_AUDIT, root),
        "build_result": binding(BUILD_RESULT, root),
        "profiles": {
            "kiota-9fa2c297": {
                "binary": build["binary"],
                "source_revision": source.SOURCE_REVISION,
                "success_contract": "exit 0; stdout empty; stderr empty",
            },
            "official-lean-4.33.0": {
                "binary": official,
                "definition": _exact_binding(OFFICIAL_DEFINITION, OFFICIAL_DEFINITION_BYTES,
                                               OFFICIAL_DEFINITION_SHA256, root),
                "toolchain": _exact_binding(OFFICIAL_TOOLCHAIN, OFFICIAL_TOOLCHAIN_BYTES,
                                              OFFICIAL_TOOLCHAIN_SHA256, root),
                "success_contract": "exit 0; stdout matches ^Accepted [0-9]+ declarations[.]\\n$; stderr empty",
            },
        },
        "cells": EXPECTED_CELLS,
        "expected_premise_gate": EXPECTED_GATE,
        "timeout_seconds_each": 120,
        "memory_bytes_each": 2147483648,
        "ps": _exact_binding(PS, PS_BYTES, PS_SHA256, root),
        "environment": {"LANG": "C", "PATH": "/usr/bin:/bin:/usr/sbin:/sbin", "RUST_BACKTRACE": "0"},
        "tooling": _tooling(root),
        "downstream_construction_before_pass": "FORBIDDEN",
    }


def freeze_execution_manifest(root: Path = ROOT) -> dict[str, Any]:
    root = Path(root).resolve()
    path = root / EXECUTION_MANIFEST
    value = make_execution_manifest(root)
    if path.exists():
        if load_json(path) != value:
            raise PilotError("existing execution manifest differs")
    else:
        _write_json(path, value)
    return value


def validate_execution_manifest(root: Path = ROOT, *, require_commit: bool = True) -> dict[str, Any]:
    root = Path(root).resolve()
    actual = load_json(root / EXECUTION_MANIFEST)
    expected = make_execution_manifest(root)
    if actual != expected:
        raise PilotError("Stage-1 execution manifest is stale")
    if require_commit:
        committed(root, EXECUTION_MANIFEST.as_posix())
        for row in actual["tooling"]:
            if not Path(row["path"]).is_absolute():
                committed(root, row["path"])
        for path in (PAIR_AUDIT, BUILD_RESULT, DESIGN, PROTOCOL, WORK, PLAN, QUEUE, STATUS):
            committed(root, path.as_posix())
    return actual


def classify(profile_id: str, receipt: dict[str, Any], stdout: bytes,
             stderr: bytes) -> tuple[str, str]:
    try:
        _safe_receipt(receipt, "checker cell")
    except PilotError as error:
        return "INFRASTRUCTURE_AUDIT_FAILURE", str(error)
    code = receipt.get("exit_code")
    if code is not None and code < 0:
        return "CRASH", f"terminated by signal {-code}"
    if profile_id == "kiota-9fa2c297":
        if code == 0 and stdout == b"" and stderr == b"":
            return "ACCEPT", "exit 0 with exact empty-output contract"
        if b"json parse" in stderr.lower():
            return "PARSER_IMPORT_REJECTION", "Kiota diagnostic identifies JSON import failure"
        if code == 1 and stderr.startswith(b"REJECT: "):
            return "REJECT", "Kiota structured semantic rejection"
        if code == 2 and stderr.startswith(b"DECLINE: "):
            return "DECLINE", "Kiota structured decline"
        if b"panic" in stderr.lower():
            return "CRASH", "Kiota panic diagnostic"
        return "INFRASTRUCTURE_AUDIT_FAILURE", "Kiota output/exit contract is unclassified"
    if profile_id == "official-lean-4.33.0":
        if (code == 0 and stderr == b""
                and re.fullmatch(rb"Accepted [0-9]+ declarations[.]\n", stdout)):
            return "ACCEPT", "exit 0 with exact official success contract"
        if (code == 1 and stdout == b""
                and stderr == b"uncaught exception: Invalid recursor LALNest.rec_1\n"):
            return "INTENDED_RECURSOR_REJECT", "exact intended-object recursor rejection"
        if any(marker in (stdout + stderr).lower() for marker in (b"json", b"parse", b"back-reference")):
            return "PARSER_IMPORT_REJECTION", "official diagnostic identifies import failure"
        if code == 1:
            return "SEMANTIC_REJECT", "official semantic rejection outside the exact intended contract"
        return "INFRASTRUCTURE_AUDIT_FAILURE", "official output/exit contract is unclassified"
    return "INFRASTRUCTURE_AUDIT_FAILURE", "unknown observer profile"


@contextmanager
def _launch_lock(root: Path) -> Iterator[None]:
    path = root / BASE / ".stage-1-launch.lock"
    stream = path.open("a+")
    try:
        fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as error:
        stream.close()
        raise PilotError("another Stage-1 launch owns the lock") from error
    try:
        yield
    finally:
        fcntl.flock(stream, fcntl.LOCK_UN)
        stream.close()


def execute_stage_1(root: Path = ROOT,
                    runner: Callable[..., dict[str, Any]] = run_supervised) -> dict[str, Any]:
    root = Path(root).resolve()
    manifest = validate_execution_manifest(root, require_commit=True)
    run_dir = root / RUN_DIR
    if run_dir.exists():
        raise PilotError("refuse to overwrite Stage-1 run")
    artifacts = {name: verify_binding(row, root) for name, row in manifest["artifacts"].items()}
    profiles = manifest["profiles"]
    results: list[dict[str, Any]] = []
    with _launch_lock(root):
        run_dir.mkdir(parents=True)
        for cell in manifest["cells"]:
            profile_id = cell["profile_id"]
            artifact = artifacts[cell["artifact_id"]]
            binary = verify_binding(profiles[profile_id]["binary"], root)
            raw_prefix = run_dir / "raw" / f"{cell['ordinal']:02d}-{profile_id}-{cell['artifact_id']}"
            receipt = runner(
                argv=[str(binary), str(artifact)], cwd=root, stdin=None,
                env=dict(manifest["environment"]), timeout_seconds=manifest["timeout_seconds_each"],
                memory_bytes=manifest["memory_bytes_each"], raw_prefix=raw_prefix,
            )
            stdout, stderr = _verify_raw(receipt, root)
            outcome, reason = classify(profile_id, receipt, stdout, stderr)
            row = {"cell": cell, "artifact": manifest["artifacts"][cell["artifact_id"]],
                   "outcome": outcome, "reason": reason, "receipt": receipt}
            results.append(row)
            with (run_dir / "events.jsonl").open("a", encoding="utf-8") as output:
                output.write(json.dumps(row, sort_keys=True) + "\n")
            partial = {
                "schema_version": 1, "item_id": ITEM,
                "execution_manifest": binding(EXECUTION_MANIFEST, root),
                "cells": results, "checker_attempts": len(results),
                "process_seconds": sum(value["receipt"]["elapsed_seconds"] for value in results),
                "status": "RUNNING",
            }
            _write_json(run_dir / "result.json", partial)
            if outcome == "INFRASTRUCTURE_AUDIT_FAILURE":
                raise PilotError(f"cell {cell['cell_id']} infrastructure failure: {reason}")
    observed = {row["cell"]["cell_id"]: row["outcome"] for row in results}
    gate_passed = observed == manifest["expected_premise_gate"]
    result = {
        "schema_version": 1,
        "item_id": ITEM,
        "execution_manifest": binding(EXECUTION_MANIFEST, root),
        "cells": results,
        "checker_attempts": len(results),
        "process_seconds": sum(row["receipt"]["elapsed_seconds"] for row in results),
        "status": "COMPLETE",
        "premise_gate": {
            "status": "PASS" if gate_passed else "FAIL",
            "expected": manifest["expected_premise_gate"],
            "observed": observed,
            "stage_2_authorized": gate_passed,
        },
    }
    _write_json(run_dir / "result.json", result)
    return result


def validate_stage_1_result(root: Path = ROOT, *, require_commit: bool = False) -> dict[str, Any]:
    root = Path(root).resolve()
    manifest = validate_execution_manifest(root, require_commit=require_commit)
    result = load_json(root / RUN_RESULT)
    if result.get("status") != "COMPLETE" or result.get("checker_attempts") != 4:
        raise PilotError("Stage-1 result is incomplete")
    if [row.get("cell") for row in result.get("cells", [])] != manifest["cells"]:
        raise PilotError("Stage-1 result cells differ from frozen order")
    for row in result["cells"]:
        verify_binding(row["artifact"], root)
        receipt = row.get("receipt")
        if not isinstance(receipt, dict):
            raise PilotError("Stage-1 cell lacks receipt")
        stdout, stderr = _verify_raw(receipt, root)
        expected = classify(row["cell"]["profile_id"], receipt, stdout, stderr)
        if (row.get("outcome"), row.get("reason")) != expected:
            raise PilotError("Stage-1 cell classification differs")
        if require_commit:
            for kind in ("stdout", "stderr"):
                committed(root, receipt[f"raw_{kind}_path"])
    observed = {row["cell"]["cell_id"]: row["outcome"] for row in result["cells"]}
    gate = result.get("premise_gate")
    if (not isinstance(gate, dict) or gate.get("observed") != observed
            or gate.get("expected") != EXPECTED_GATE
            or gate.get("stage_2_authorized") != (observed == EXPECTED_GATE)):
        raise PilotError("Stage-1 premise gate differs")
    if require_commit:
        committed(root, RUN_RESULT.as_posix())
        committed(root, (RUN_DIR / "events.jsonl").as_posix())
    return result


def validate_preparation(root: Path = ROOT, *, require_commit: bool = False) -> dict[str, Any]:
    root = Path(root).resolve()
    _active(root)
    pair_audit.check(root)
    source.inspect_environment(root)
    value: dict[str, Any] = {"schema_version": 1, "item_id": ITEM,
                             "pair_audit": "PASS", "source_environment": "PASS"}
    if (root / BUILD_MANIFEST).exists():
        validate_build_manifest(root, require_commit=require_commit)
        value["build_manifest"] = "PASS"
    if (root / BUILD_RESULT).exists():
        validate_build_result(root, require_commit=require_commit)
        value["build_result"] = "PASS"
    if (root / EXECUTION_MANIFEST).exists():
        validate_execution_manifest(root, require_commit=require_commit)
        value["execution_manifest"] = "PASS"
    if (root / RUN_RESULT).exists():
        result = validate_stage_1_result(root, require_commit=require_commit)
        value["stage_1_result"] = result["premise_gate"]["status"]
    return value
