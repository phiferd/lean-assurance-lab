"""Portable replay for the PR15373 admission-confirmation evidence family."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


REL = Path("results/research/lean-eta-admission-confirmation-1")


class ReplayError(ValueError):
    pass


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _json(path: Path):
    try:
        return json.loads(path.read_bytes())
    except (OSError, json.JSONDecodeError) as error:
        raise ReplayError(f"cannot read {path}: {error}") from error


def replay(root: Path) -> dict[str, object]:
    base = Path(root).resolve() / REL
    launch = _json(base / "launch-manifest.json")
    source = _json(base / "source-manifest.json")
    if launch.get("schema_version") != 1 or source.get("schema_version") != 1:
        raise ReplayError("unsupported manifest schema")
    if _sha(base / "source-manifest.json") != launch.get("source_manifest_sha256"):
        raise ReplayError("source manifest differs from launch binding")
    if _sha(base / "expected.json") != launch.get("expected_sha256"):
        raise ReplayError("expected record differs from launch binding")
    for relative, digest in launch.get("fixture_sources", {}).items():
        if _sha(Path(root).resolve() / relative) != digest:
            raise ReplayError(f"fixture differs: {relative}")
    for relative, digest in launch.get("generated_oleans", {}).items():
        if _sha(Path(root).resolve() / relative) != digest:
            raise ReplayError(f"generated olean differs: {relative}")
    for relative, digest in source.get("retained_exact_source", {}).items():
        if _sha(Path(root).resolve() / relative) != digest:
            raise ReplayError(f"retained source differs: {relative}")

    attempts = base / "attempts"
    receipt_paths = sorted(attempts.glob("*/receipt.json"))
    if len(receipt_paths) != 27:
        raise ReplayError("prelaunch receipt inventory differs")
    for receipt_path in receipt_paths:
        receipt = _json(receipt_path)
        command = _json(receipt_path.with_name("command.json"))
        if receipt.get("cwd") != command.get("cwd") or receipt.get("argv") != command.get("argv"):
            raise ReplayError(f"command differs from receipt: {receipt_path.parent.name}")
        if not receipt.get("cleanup_complete"):
            raise ReplayError(f"cleanup incomplete: {receipt_path.parent.name}")
        if receipt.get("accounting_error") or receipt.get("monitor_errors"):
            raise ReplayError(f"control fault: {receipt_path.parent.name}")
        for stream in ("stdout", "stderr"):
            raw = receipt_path.with_name(f"{stream}.log")
            data = raw.read_bytes()
            if receipt.get(f"{stream}_bytes") != len(data):
                raise ReplayError(f"{stream} length differs: {receipt_path.parent.name}")
            if receipt.get(f"{stream}_sha256") != hashlib.sha256(data).hexdigest():
                raise ReplayError(f"{stream} hash differs: {receipt_path.parent.name}")

    successful = source.get("successful_preparation_receipts", {})
    if len(successful) != 12:
        raise ReplayError("successful preparation receipt inventory differs")
    for name, digest in successful.items():
        receipt_path = attempts / name / "receipt.json"
        if _sha(receipt_path) != digest or _json(receipt_path).get("exit_code") != 0:
            raise ReplayError(f"successful preparation binding differs: {name}")

    identities = {
        "head-identity-3": "revision=015d54649bcaaa0861f355b59761ce308e629fbb",
        "parent-identity-3": "revision=2c2bdd9630a7a6c51d7620d5efefcdba104f38f3",
    }
    for name, marker in identities.items():
        if marker.encode() not in (attempts / name / "stdout.log").read_bytes():
            raise ReplayError(f"runtime identity missing: {name}")
    return {
        "status": "PASS",
        "receipts": len(receipt_paths),
        "successful_preparation_receipts": len(successful),
        "fixture_sources": len(launch["fixture_sources"]),
        "generated_oleans": len(launch["generated_oleans"]),
        "host_launches": 0,
    }
