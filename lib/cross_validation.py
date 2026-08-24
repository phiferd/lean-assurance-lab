"""Validator-neutral compatibility, execution, and cross-check classification."""

from __future__ import annotations

import hashlib
import json
import subprocess
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "config" / "validators.json"
OUTCOMES = {"ACCEPT", "REJECT", "DECLINE", "CRASH", "TIMEOUT", "PARSE_ERROR", "UNKNOWN"}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def load_catalog() -> dict[str, Any]:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def profiles_by_id(catalog: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {profile["id"]: profile for profile in catalog["validators"]}


def tree_digest(root: Path, relative_files: list[str]) -> str | None:
    if not root.exists() or any(not (root / name).is_file() for name in relative_files):
        return None
    digest = hashlib.sha256()
    for name in sorted(relative_files):
        digest.update(name.encode())
        digest.update(b"\0")
        digest.update((root / name).read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def inspect_export(path: Path) -> dict[str, Any]:
    metadata = None
    parse_errors = []
    nonempty_records = 0
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as error:
            parse_errors.append({"line": line_no, "error": str(error)})
            continue
        nonempty_records += 1
        if isinstance(row, dict) and isinstance(row.get("meta"), dict) and metadata is None:
            metadata = row["meta"]
    return {
        "record_count": nonempty_records,
        "parse_errors": parse_errors,
        "format_version": (metadata or {}).get("format", {}).get("version"),
        "exporter_version": (metadata or {}).get("exporter", {}).get("version"),
        "lean_version": (metadata or {}).get("lean", {}).get("version"),
        "lean_githash": (metadata or {}).get("lean", {}).get("githash"),
    }


def checker_identity(profile: dict[str, Any]) -> dict[str, Any]:
    definition = ROOT / profile["arena_definition"]
    binary = ROOT / profile["binary"]
    identity = {
        "id": profile["id"],
        "display_name": profile["display_name"],
        "version": profile["version"],
        "role": profile["role"],
        "implementation_family": profile["implementation_family"],
        "independent_from_nanoda": profile["independent_from_nanoda"],
        "arena_definition": relative(definition),
        "arena_definition_sha256": sha256_file(definition) if definition.exists() else None,
        "binary": relative(binary),
        "binary_sha256": sha256_file(binary) if binary.exists() else None,
    }
    arena = ROOT / "external" / "lean-kernel-arena"
    arena_proc = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=arena, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    identity["arena_revision"] = arena_proc.stdout.strip() if arena_proc.returncode == 0 else None
    source_checkout = profile.get("source_checkout")
    expected_revision = profile.get("expected_source_revision")
    if source_checkout and expected_revision:
        checkout = ROOT / source_checkout
        proc = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=checkout, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        ) if checkout.exists() else None
        identity["source_revision"] = proc.stdout.strip() if proc and proc.returncode == 0 else None
        identity["expected_source_revision"] = expected_revision
        status_proc = subprocess.run(
            ["git", "status", "--porcelain"], cwd=checkout, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        ) if checkout.exists() else None
        identity["source_clean"] = bool(status_proc and status_proc.returncode == 0 and not status_proc.stdout)
    source_template = profile.get("source_template")
    source_files = profile.get("source_files", [])
    if source_checkout and source_template and source_files:
        identity["source_template_sha256"] = tree_digest(ROOT / source_template, source_files)
        identity["built_source_sha256"] = tree_digest(ROOT / source_checkout, source_files)
        identity["built_source_matches_template"] = (
            identity["source_template_sha256"] is not None
            and identity["source_template_sha256"] == identity["built_source_sha256"]
        )
    expected_toolchain = profile.get("expected_built_toolchain")
    if source_checkout and expected_toolchain:
        toolchain = ROOT / source_checkout / "lean-toolchain"
        identity["built_toolchain"] = toolchain.read_text(encoding="utf-8").strip() if toolchain.exists() else None
        identity["expected_built_toolchain"] = expected_toolchain
    return identity


def static_compatibility(profile: dict[str, Any], metadata: dict[str, Any]) -> dict[str, Any]:
    reasons = []
    identity = checker_identity(profile)
    if identity["arena_definition_sha256"] is None:
        reasons.append("CHECKER_DEFINITION_MISSING")
    if identity["binary_sha256"] is None:
        reasons.append("CHECKER_BINARY_MISSING")
    if metadata["parse_errors"]:
        reasons.append("ARTIFACT_NDJSON_PARSE_ERROR")
    if metadata["format_version"] not in profile["compatible_export_formats"]:
        reasons.append("UNSUPPORTED_OR_MISSING_FORMAT_VERSION")
    if metadata["exporter_version"] not in profile["compatible_exporter_versions"]:
        reasons.append("UNSUPPORTED_OR_MISSING_EXPORTER_VERSION")
    if metadata["lean_version"] not in profile["empirically_compatible_lean_versions"]:
        reasons.append("UNTESTED_OR_MISSING_LEAN_VERSION")
    expected_revision = identity.get("expected_source_revision")
    if expected_revision and identity.get("source_revision") != expected_revision:
        reasons.append("CHECKER_SOURCE_REVISION_MISMATCH")
    if expected_revision and not identity.get("source_clean"):
        reasons.append("CHECKER_SOURCE_DIRTY")
    if "built_source_matches_template" in identity and not identity["built_source_matches_template"]:
        reasons.append("BUILT_SOURCE_DIFFERS_FROM_ARENA_TEMPLATE")
    if "expected_built_toolchain" in identity and identity.get("built_toolchain") != identity["expected_built_toolchain"]:
        reasons.append("BUILT_TOOLCHAIN_MISMATCH")
    return {
        "status": "COMPATIBLE" if not reasons else "INCOMPATIBLE",
        "reasons": reasons,
        "rule": "exact export metadata, pinned checker identity, built binary, then positive-control acceptance",
        "checker_identity": identity,
    }


def normalize_process(adapter: str, returncode: int, stdout: bytes, stderr: bytes) -> tuple[str, str]:
    text = (stdout + b"\n" + stderr).decode(errors="replace").lower()
    if returncode == 0:
        return "ACCEPT", "PARSED_OR_IGNORED"
    if returncode == 2:
        return "DECLINE", "NOT_EVALUATED"
    if returncode < 0:
        return "CRASH", "UNKNOWN"
    parse_markers = ("json parse", "parse error", "invalid json", "unexpected token")
    if any(marker in text for marker in parse_markers):
        return "PARSE_ERROR", "PARSE_ERROR"
    if returncode == 1:
        semantic_markers = ("(kernel)", "invalid reference", "defninfo invalid", "type mismatch")
        parse_behavior = "REACHED_VALIDATION" if any(marker in text for marker in semantic_markers) else "UNKNOWN"
        return "REJECT", parse_behavior
    return "UNKNOWN", "UNKNOWN"


def run_validator(profile: dict[str, Any], artifact: Path, timeout: float) -> dict[str, Any]:
    binary = ROOT / profile["binary"]
    command = [
        token.replace("{binary}", str(binary)).replace("{artifact}", str(artifact.resolve()))
        for token in profile["command"]
    ]
    recorded_command = [relative(Path(token)) if Path(token).is_absolute() else token for token in command]
    started = time.monotonic()
    try:
        proc = subprocess.run(
            command, cwd=binary.parent, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=timeout,
        )
        outcome, parse_behavior = normalize_process(
            profile["adapter"], proc.returncode, proc.stdout, proc.stderr
        )
        return {
            "normalized_outcome": outcome,
            "parse_behavior": parse_behavior,
            "exit_code": proc.returncode,
            "signal": -proc.returncode if proc.returncode < 0 else None,
            "seconds": time.monotonic() - started,
            "stdout_sha256": hashlib.sha256(proc.stdout).hexdigest(),
            "stderr_sha256": hashlib.sha256(proc.stderr).hexdigest(),
            "stdout_tail": proc.stdout.decode(errors="replace")[-2000:],
            "stderr_tail": proc.stderr.decode(errors="replace")[-2000:],
            "command": recorded_command,
        }
    except subprocess.TimeoutExpired as error:
        stdout = error.stdout or b""
        stderr = error.stderr or b""
        return {
            "normalized_outcome": "TIMEOUT", "parse_behavior": "UNKNOWN",
            "exit_code": None, "signal": None, "seconds": time.monotonic() - started,
            "stdout_sha256": hashlib.sha256(stdout).hexdigest(),
            "stderr_sha256": hashlib.sha256(stderr).hexdigest(),
            "stdout_tail": stdout.decode(errors="replace")[-2000:],
            "stderr_tail": stderr.decode(errors="replace")[-2000:],
            "command": recorded_command,
        }


def result_classification(outcome: str, expected_outcome: str | None) -> str:
    if outcome == "DECLINE":
        return "DECLINED"
    if outcome == "CRASH":
        return "CRASHED"
    if outcome == "TIMEOUT":
        return "TIMED_OUT"
    if outcome == "PARSE_ERROR":
        return "PARSE_ERROR"
    if outcome == "UNKNOWN":
        return "UNRESOLVED"
    if expected_outcome is None:
        return "UNRESOLVED"
    return "CONFIRMED" if outcome == expected_outcome else "CHECKER_DISAGREEMENT"


def aggregate_classification(results: list[dict[str, Any]], expected_outcome: str | None) -> str:
    classifications = [row["classification"] for row in results]
    compatible_outcomes = {
        row["result"]["normalized_outcome"]
        for row in results
        if row["compatibility"]["status"] in {"COMPATIBLE", "PROBE_ONLY"} and row.get("result")
    }
    if "CHECKER_DISAGREEMENT" in classifications:
        return "CHECKER_DISAGREEMENT"
    if expected_outcome is None and len(compatible_outcomes) > 1:
        return "CHECKER_DISAGREEMENT"
    for status in ("CRASHED", "TIMED_OUT", "PARSE_ERROR", "DECLINED", "INCOMPATIBLE"):
        if status in classifications:
            return status
    if expected_outcome is not None and "CONFIRMED" in classifications:
        return "CONFIRMED"
    return "UNRESOLVED"
