"""Mechanical validation for community contribution manifests."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import jsonschema


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_catalog(catalog: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors = [error.message for error in jsonschema.Draft202012Validator(schema).iter_errors(catalog)]
    ids = [row.get("id") for row in catalog.get("contribution_types", [])]
    if len(ids) != len(set(ids)):
        errors.append("contribution type ids must be unique")
    return sorted(errors)


def validate_manifest(
    root: Path,
    manifest: dict[str, Any],
    manifest_schema: dict[str, Any],
    catalog: dict[str, Any],
) -> list[str]:
    errors = [error.message for error in jsonschema.Draft202012Validator(manifest_schema).iter_errors(manifest)]
    by_type = {row["id"]: row for row in catalog["contribution_types"]}
    contribution_type = manifest.get("contribution_type")
    if contribution_type not in by_type:
        errors.append(f"unknown contribution_type: {contribution_type}")
        return sorted(errors)
    metadata = manifest.get("type_metadata", {})
    required_metadata = by_type[contribution_type]["required_type_metadata"]
    missing = sorted(
        name for name in required_metadata
        if name not in metadata
        or metadata[name] is None
        or (isinstance(metadata[name], (str, list, dict)) and not metadata[name])
    )
    if missing:
        errors.append(f"missing or empty type_metadata: {', '.join(missing)}")
    bound_records = list(manifest.get("artifacts", []))
    bound_records.extend(row.get("result", {}) for row in manifest.get("evidence", []))
    for record in bound_records:
        if not isinstance(record, dict) or "path" not in record or "sha256" not in record:
            continue
        path = (root / record["path"]).resolve()
        try:
            path.relative_to(root.resolve())
        except ValueError:
            errors.append(f"bound file outside repository: {record['path']}")
            continue
        if not path.is_file():
            errors.append(f"bound file missing: {record['path']}")
        elif sha256_file(path) != record["sha256"]:
            errors.append(f"bound file hash mismatch: {record['path']}")
    return sorted(errors)
