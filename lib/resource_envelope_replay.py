"""Read-only, host-independent custody replay of resource process receipts.

Recorded absolute commands and cwd values are historical strings. Replay opens
only copied repository evidence; it never invokes an observer or a host tool.
"""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from lib.resource_envelope_observe import _validate_accounting, ObservationError


REL = Path("results/research/resource-envelope-pilot-1")


class ReplayError(ValueError):
    pass


def _unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    row: dict[str, Any] = {}
    for key, value in pairs:
        if key in row:
            raise ReplayError(f"duplicate JSON key: {key}")
        row[key] = value
    return row


def _load(path: Path) -> dict[str, Any]:
    try:
        row = json.loads(path.read_bytes(), object_pairs_hook=_unique,
                         parse_constant=lambda x: (_ for _ in ()).throw(ReplayError(x)))
    except (OSError, ValueError) as exc:
        raise ReplayError(f"cannot parse {path}") from exc
    if type(row) is not dict:
        raise ReplayError(f"expected object: {path}")
    return row


def _bound(root: Path, row: dict[str, Any]) -> Path:
    if set(row) != {"path", "bytes", "sha256"} or type(row["path"]) is not str:
        raise ReplayError("invalid repository file binding")
    relative = Path(row["path"])
    if relative.is_absolute() or not relative.parts or ".." in relative.parts:
        raise ReplayError("nonportable repository file binding")
    path = root / relative
    if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(root.resolve()):
        raise ReplayError(f"missing bound file: {relative}")
    raw = path.read_bytes()
    if (type(row["bytes"]) is not int or row["bytes"] != len(raw)
            or row["sha256"] != sha256(raw).hexdigest()):
        raise ReplayError(f"bound bytes differ: {relative}")
    return path


def _raw(root: Path, receipt: dict[str, Any], stream: str,
         preflight_path: Path | None) -> bytes:
    if preflight_path is not None:
        relative = preflight_path.parent.relative_to(root) / f"{stream}.raw"
    else:
        key = f"raw_{stream}_path"
        relative = Path(receipt.get(key, ""))
        if relative.is_absolute() or not relative.parts or ".." in relative.parts:
            raise ReplayError(f"invalid {stream} path")
    path = root / relative
    if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(root.resolve()):
        raise ReplayError(f"missing {stream} raw stream: {relative}")
    raw = path.read_bytes()
    if (receipt.get(f"{stream}_bytes") != len(raw)
            or receipt.get(f"{stream}_sha256") != sha256(raw).hexdigest()):
        raise ReplayError(f"{stream} raw custody differs: {relative}")
    return raw


def replay(root: Path) -> dict[str, Any]:
    root = root.resolve()
    base = root / REL
    preflight = base / "preflight-run-0001/process-receipt.json"
    attestation = _load(base / "preflight-run-0001/provenance-attestation.json")
    if attestation.get("status") != "POST_RUN_PROVENANCE_ATTESTATION":
        raise ReplayError("preflight provenance status differs")
    for row in attestation.get("attempt_files", []):
        _bound(root, row)
    if preflight not in [_bound(root, row) for row in attestation["attempt_files"]]:
        raise ReplayError("preflight receipt absent from provenance")
    preflights = sorted(base.glob("preflight-run-*/process-receipt.json"))
    receipt_paths = [*preflights, *sorted(base.glob("construction-run-*/processes/*.receipt.json")),
                     *sorted(base.glob("smoke-run-*/processes/*.receipt.json")),
                     *sorted(base.glob("science-run-*/processes/*.receipt.json"))]
    if len(set(receipt_paths)) != len(receipt_paths):
        raise ReplayError("duplicate process receipt path")
    discovered: set[Path] = set()
    for candidate in base.rglob("*.json"):
        value = _load(candidate)
        def visit(item: Any) -> bool:
            if type(item) is dict:
                if (type(item.get("cwd")) is str and type(item.get("argv")) is list
                        and "exit_code" in item):
                    return True
                return any(visit(child) for child in item.values())
            return type(item) is list and any(visit(child) for child in item)
        if visit(value):
            discovered.add(candidate)
    if discovered != set(receipt_paths):
        raise ReplayError("process receipt discovery differs from replay coverage")
    checked = 0
    streams = 0
    healthy = 0
    repair_faults = 0
    for path in receipt_paths:
        row = _load(path)
        accounting_error = row.get("accounting_error")
        reap_complete = row.get("reap_complete")
        if (type(row.get("cwd")) is not str or not Path(row["cwd"]).is_absolute()
                or type(row.get("argv")) is not list or not row["argv"]
                or not all(type(arg) is str for arg in row["argv"])
                or type(reap_complete) is not bool
                or not (accounting_error is None
                        or (type(accounting_error) is str and bool(accounting_error)))
                or (type(row.get("exit_code")) is not int
                    and not (row.get("exit_code") is None
                             and (accounting_error is not None or reap_complete is False)))):
            raise ReplayError(f"invalid recorded process identity: {path}")
        preflight_path = path if path in preflights else None
        out = _raw(root, row, "stdout", preflight_path)
        err = _raw(root, row, "stderr", preflight_path)
        streams += 2
        if accounting_error is not None or not reap_complete:
            repair_faults += 1
        else:
            try:
                _validate_accounting(row, out, err)
            except ObservationError as exc:
                raise ReplayError(f"process accounting differs: {path}") from exc
            healthy += 1
        checked += 1
    if checked == 0 or healthy == 0:
        raise ReplayError("positive preflight process absent")
    preflight_row = _load(preflight)
    if (preflight_row.get("exit_code") != 0 or not preflight_row.get("cleanup_complete")
            or preflight_row.get("sample_count", 0) <= 0
            or _raw(root, preflight_row, "stdout", preflight) != b"preflight-ok"
            or _raw(root, preflight_row, "stderr", preflight)):
        raise ReplayError("positive preflight outcome differs")
    return {"status": "PASS", "process_receipts": checked,
            "raw_streams": streams, "accounting_valid": healthy,
            "preserved_accounting_faults": repair_faults, "host_launches": 0}
