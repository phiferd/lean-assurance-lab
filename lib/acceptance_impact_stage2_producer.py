"""Deterministic Stage-2 artifact producer for ACCEPTANCE-IMPACT-PILOT-1."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
from typing import Any

from lib.cvc_prep import committed


ROOT = Path(__file__).resolve().parents[1]
ITEM = "ACCEPTANCE-IMPACT-PILOT-1"
CONTRACT = Path("results/research/acceptance-impact-pilot-1/consequence-contract.json")
MODULE = "lib/acceptance_impact_stage2_producer.py"

EXPECTED_ARTIFACTS = {
    "candidate_use": "corpus/acceptance-impact-pilot-1/five-app-candidate.ndjson",
    "control_use": "corpus/acceptance-impact-pilot-1/five-app-control.ndjson",
}
EXPECTED_BASE_BINDINGS = {
    "candidate_use": {
        "path": "corpus/generated/nanoda-gen-7b603be7dc87-valid-aux-type.ndjson",
        "bytes": 6332,
        "sha256": "13900d3c26371111800a6c85ba8a9cc3d472beb384cf2c5fde574b8a9e7f36bd",
    },
    "control_use": {
        "path": "corpus/generated/nanoda-gen-7b603be7dc87-valid-control.ndjson",
        "bytes": 6332,
        "sha256": "3b66763082822a74a203fb4dda773ff473e853e73077b8f564c603b56e9610ae",
    },
}
EXPECTED_FIXED_DECLARATION = {
    "name_id": 20,
    "name": "LALNest.rec_1_impact",
    "name_record": {"in": 20, "str": {"pre": 10, "str": "rec_1_impact"}},
    "level_parameters": [],
    "constant": {"name": 13, "universes": [1]},
    "first_four_arguments": [81, 82, 84, 86],
    "fifth_argument": 2,
    "application_spine": [88, 89, 90, 91, 92],
    "value_expression": 93,
    "type_expression": 94,
    "declaration_record_index": 120,
    "total_records": 121,
}
EXPECTED_COMMON = [
    {"in": 20, "str": {"pre": 10, "str": "rec_1_impact"}},
    {"ie": 81, "lam": {"binderInfo": "default", "body": 28, "name": 8, "type": 28}},
    {"ie": 82, "lam": {"binderInfo": "default", "body": 28, "name": 8, "type": 29}},
    {"ie": 83, "lam": {"binderInfo": "default", "body": 2, "name": 17, "type": 28}},
    {"ie": 84, "lam": {"binderInfo": "default", "body": 83, "name": 12, "type": 29}},
    {"ie": 85, "lam": {"binderInfo": "default", "body": 2, "name": 18, "type": 28}},
    {"ie": 86, "lam": {"binderInfo": "default", "body": 85, "name": 4, "type": 28}},
    {"const": {"name": 13, "us": [1]}, "ie": 87},
    {"app": {"arg": 81, "fn": 87}, "ie": 88},
    {"app": {"arg": 82, "fn": 88}, "ie": 89},
    {"app": {"arg": 84, "fn": 89}, "ie": 90},
    {"app": {"arg": 86, "fn": 90}, "ie": 91},
    {"app": {"arg": 2, "fn": 91}, "ie": 92},
]
EXPECTED_TAILS = {
    "candidate_use": [
        {"ie": 93, "lam": {"binderInfo": "default", "body": 92, "name": 8, "type": 28}},
        {"forallE": {"binderInfo": "default", "body": 28, "name": 8, "type": 28},
         "ie": 94},
        {"def": {"all": [20], "hints": "opaque", "levelParams": [], "name": 20,
                 "safety": "safe", "type": 94, "value": 93}},
    ],
    "control_use": [
        {"ie": 93, "lam": {"binderInfo": "default", "body": 92, "name": 8, "type": 29}},
        {"forallE": {"binderInfo": "default", "body": 28, "name": 8, "type": 29},
         "ie": 94},
        {"def": {"all": [20], "hints": "opaque", "levelParams": [], "name": 20,
                 "safety": "safe", "type": 94, "value": 93}},
    ],
}


class ProducerError(ValueError):
    """A frozen input or deterministic-output invariant failed."""


def _pairs(rows: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in rows:
        if key in result:
            raise ProducerError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _nonfinite(value: str) -> None:
    raise ProducerError(f"non-finite JSON value: {value}")


def _load_json(raw: bytes, label: str) -> Any:
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs,
                          parse_constant=_nonfinite)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise ProducerError(f"invalid JSON in {label}: {error}") from error


def _load_ndjson(raw: bytes, label: str) -> list[dict[str, Any]]:
    if not raw.endswith(b"\n") or raw.endswith(b"\n\n"):
        raise ProducerError(f"{label} must end with exactly one newline")
    records = [_load_json(line, f"{label}:{index}")
               for index, line in enumerate(raw.splitlines(), 1)]
    if not records or any(not isinstance(record, dict) for record in records):
        raise ProducerError(f"{label} must contain object records")
    return records


def _safe_repo_path(root: Path, relative: Any) -> Path:
    if (not isinstance(relative, str) or not relative
            or Path(relative).is_absolute() or ".." in Path(relative).parts):
        raise ProducerError("contract path must be repository-relative")
    path = root.joinpath(relative)
    resolved = path.resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError as error:
        raise ProducerError(f"contract path escapes repository: {relative}") from error
    return path


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _contract(root: Path) -> dict[str, Any]:
    root = Path(root).resolve()
    try:
        committed(root, CONTRACT.as_posix())
    except (OSError, ValueError) as error:
        raise ProducerError(f"committed consequence contract required: {error}") from error
    path = _safe_repo_path(root, CONTRACT.as_posix())
    if not path.is_file() or path.is_symlink():
        raise ProducerError("consequence contract is missing or linked")
    contract = _load_json(path.read_bytes(), CONTRACT.as_posix())
    if not isinstance(contract, dict):
        raise ProducerError("consequence contract must be an object")
    if (contract.get("schema_version") != 1 or contract.get("item_id") != ITEM
            or contract.get("stage") != "STAGE_2"
            or contract.get("status") != "FROZEN_BEFORE_CONSTRUCTION"
            or contract.get("producer") != MODULE):
        raise ProducerError("consequence contract identity or state differs")
    if contract.get("artifacts") != EXPECTED_ARTIFACTS:
        raise ProducerError("consequence contract artifact paths differ")
    if contract.get("base_bindings") != EXPECTED_BASE_BINDINGS:
        raise ProducerError("consequence contract base bindings differ")
    if contract.get("fixed_declaration") != EXPECTED_FIXED_DECLARATION:
        raise ProducerError("consequence contract declaration identity differs")
    if contract.get("fixed_append_records_common") != EXPECTED_COMMON:
        raise ProducerError("consequence contract common suffix differs")
    if (contract.get("candidate_tail") != EXPECTED_TAILS["candidate_use"]
            or contract.get("control_tail") != EXPECTED_TAILS["control_use"]):
        raise ProducerError("consequence contract artifact tail differs")
    return contract


def _bound_base(root: Path, binding: dict[str, Any]) -> bytes:
    if (set(binding) != {"path", "bytes", "sha256"}
            or type(binding["bytes"]) is not int or binding["bytes"] < 0
            or not isinstance(binding["sha256"], str)
            or re.fullmatch(r"[0-9a-f]{64}", binding["sha256"]) is None):
        raise ProducerError("invalid base binding")
    path = _safe_repo_path(root, binding["path"])
    if not path.is_file() or path.is_symlink():
        raise ProducerError(f"base is missing or linked: {binding['path']}")
    raw = path.read_bytes()
    if len(raw) != binding["bytes"] or _sha256(raw) != binding["sha256"]:
        raise ProducerError(f"base binding mismatch: {binding['path']}")
    records = _load_ndjson(raw, binding["path"])
    if len(records) != 105:
        raise ProducerError(f"base must contain exactly 105 records: {binding['path']}")
    return raw


def _encode_records(records: list[dict[str, Any]]) -> bytes:
    try:
        return b"".join(
            (json.dumps(record, sort_keys=True, separators=(",", ":"),
                        ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")
            for record in records
        )
    except (TypeError, ValueError) as error:
        raise ProducerError(f"fixed suffix is not deterministic JSON: {error}") from error


def render_artifacts(root: Path = ROOT) -> dict[str, bytes]:
    """Render both frozen artifacts in memory without writing them."""
    root = Path(root).resolve()
    contract = _contract(root)
    rendered: dict[str, bytes] = {}
    for artifact_id, tail_key in (("candidate_use", "candidate_tail"),
                                  ("control_use", "control_tail")):
        base = _bound_base(root, contract["base_bindings"][artifact_id])
        suffix = contract["fixed_append_records_common"] + contract[tail_key]
        if len(suffix) != 16:
            raise ProducerError("fixed suffix must contain exactly 16 records")
        raw = base + _encode_records(suffix)
        records = _load_ndjson(raw, artifact_id)
        if len(records) != EXPECTED_FIXED_DECLARATION["total_records"]:
            raise ProducerError("rendered artifact must contain exactly 121 records")
        if not raw.startswith(base):
            raise ProducerError("rendered artifact does not preserve its exact base bytes")
        if records[105:] != suffix or records[120] != tail_key_to_declaration(contract, tail_key):
            raise ProducerError("rendered artifact suffix differs from the frozen contract")
        rendered[artifact_id] = raw
    return rendered


def tail_key_to_declaration(contract: dict[str, Any], tail_key: str) -> dict[str, Any]:
    """Return the terminal declaration record for one validated contract tail."""
    tail = contract[tail_key]
    if not isinstance(tail, list) or len(tail) != 3 or not isinstance(tail[-1], dict):
        raise ProducerError("invalid frozen artifact tail")
    return tail[-1]


def _destinations(root: Path, contract: dict[str, Any],
                  output_directory: Path | None) -> dict[str, Path]:
    if output_directory is None:
        return {key: _safe_repo_path(root, relative)
                for key, relative in contract["artifacts"].items()}
    directory = Path(output_directory)
    if not directory.is_absolute():
        raise ProducerError("test output directory must be absolute")
    if directory.exists() and (not directory.is_dir() or directory.is_symlink()):
        raise ProducerError("test output directory is not a plain directory")
    return {key: directory / Path(relative).name
            for key, relative in contract["artifacts"].items()}


def produce(root: Path = ROOT, *, output_directory: Path | None = None) -> dict[str, Any]:
    """Write the exact pair once, refusing any existing destination."""
    root = Path(root).resolve()
    contract = _contract(root)
    rendered = render_artifacts(root)
    destinations = _destinations(root, contract, output_directory)
    temporary: dict[str, Path] = {}
    created: list[Path] = []
    try:
        for artifact_id, destination in destinations.items():
            destination.parent.mkdir(parents=True, exist_ok=True)
            if destination.parent.is_symlink():
                raise ProducerError(f"output parent is linked: {destination.parent}")
            if destination.exists() or destination.is_symlink():
                raise ProducerError(f"output already exists: {destination}")
            temp = destination.with_name("." + destination.name + ".tmp")
            if temp.exists() or temp.is_symlink():
                raise ProducerError(f"temporary output already exists: {temp}")
            temporary[artifact_id] = temp
        for artifact_id, temp in temporary.items():
            with temp.open("xb") as stream:
                stream.write(rendered[artifact_id])
                stream.flush()
                os.fsync(stream.fileno())
        for artifact_id, destination in destinations.items():
            os.link(temporary[artifact_id], destination)
            created.append(destination)
    except (OSError, ProducerError) as error:
        for path in created:
            try:
                path.unlink()
            except FileNotFoundError:
                pass
        if isinstance(error, ProducerError):
            raise
        raise ProducerError(f"artifact write failed: {error}") from error
    finally:
        for temp in temporary.values():
            try:
                temp.unlink()
            except FileNotFoundError:
                pass
    return {
        artifact_id: {
            "path": str(destinations[artifact_id]),
            "bytes": len(raw),
            "sha256": _sha256(raw),
            "records": EXPECTED_FIXED_DECLARATION["total_records"],
        }
        for artifact_id, raw in rendered.items()
    }
