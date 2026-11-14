"""Execute one frozen E1 phase in fresh per-cell containers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import freeze_manifest
from confirmation_common import (
    HERE, IMAGE, LEAN_PATH, ROOT, assert_container_absent, cell_label,
    container_name, container_prefix, docker, load_manifest, require_supervision,
    sha256, verify_file_bindings, write_attempt,
)

FAMILY_BASE = {
    "expression": ROOT / "explorations/runs/EXPLORE-EXPRESSION-PRECONDITION-1",
    "pi": ROOT / "explorations/runs/EXPLORE-PI-CODOMAIN-ADMISSION-1",
}


def cell_argv(phase: str, cell: dict) -> tuple[str, list[str]]:
    family = cell["family"]
    base = FAMILY_BASE[family]
    mount = "/expression-in" if family == "expression" else "/pi-in"
    name = container_name(phase, cell)
    args = container_prefix(name)
    args += [
        "--user", "1001:1001",
        "--workdir", mount,
        "--env", f"LEAN_PATH={LEAN_PATH}",
        "--mount", f"type=bind,src={base / 'inputs'},dst={mount},readonly",
        "--mount", f"type=bind,src={FAMILY_BASE['expression'] / 'Replay.lean'},dst=/Replay.lean,readonly",
        IMAGE,
        "timeout", "--kill-after=10", "120",
    ]
    ident = cell["source_case_id"]
    if cell["checker"] == "lean":
        args += ["/opt/lean-fast/bin/lean", "--run", "/Replay.lean", f"{mount}/{ident}.ndjson"]
    else:
        args += ["/opt/nanoda/target/release/nanoda_bin", f"{mount}/{ident}.json"]
    return name, args


def verify_archive(manifest: dict) -> None:
    record = manifest["runtime"]["archive"]
    path = ROOT / record["path"]
    if not path.is_file() or path.stat().st_size != record["size_bytes"]:
        raise RuntimeError("portable runtime archive is missing or has the wrong size")
    if sha256(path) != record["sha256"]:
        raise RuntimeError("portable runtime archive hash mismatch")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", required=True, choices=("initial", "replay"))
    args = parser.parse_args()
    phase = args.phase
    manifest_path = HERE / "execution-manifest.json"
    if manifest_path.read_bytes() != freeze_manifest.encoded():
        raise RuntimeError("execution manifest or a bound file is stale")
    manifest = load_manifest()
    verify_file_bindings(manifest)
    verify_archive(manifest)

    target = HERE / phase
    attempts = target / "attempts"
    attempts.mkdir(parents=True, exist_ok=False)
    image = write_attempt(
        attempts,
        "00-image-id",
        [docker(), "image", "inspect", IMAGE, "--format", "{{.Id}} {{.Os}}/{{.Architecture}}"],
        30,
    )
    require_supervision(image.receipt)
    assert image.receipt["exit_code"] == 0
    assert image.stdout.decode().strip() == IMAGE + " linux/arm64"

    launched = []
    for cell in manifest["cases"]:
        name, argv = cell_argv(phase, cell)
        label = cell_label(cell)
        result = write_attempt(attempts, label, argv, 145)
        try:
            require_supervision(result.receipt)
        finally:
            assert_container_absent(attempts, "post-" + label, name)
        launched.append({
            "id": cell["id"],
            "container_name": name,
            "exit_code": result.receipt["exit_code"],
            "elapsed_seconds": result.receipt["elapsed_seconds"],
            "receipt": f"attempts/{label}/receipt.json",
            "stdout": f"attempts/{label}/stdout.log",
            "stderr": f"attempts/{label}/stderr.log",
        })

    verify_file_bindings(manifest)
    assert len(launched) == manifest["cells_per_phase"]
    result = {
        "schema_version": 1,
        "item_id": manifest["item_id"],
        "evidence_class": "E1",
        "phase": phase,
        "image": IMAGE,
        "fresh_containers": len(launched),
        "all_containers_removed": True,
        "cells": launched,
        "classification_pending": True,
    }
    (target / "execution.json").write_text(json.dumps(result, indent=2) + "\n")
    print(f"PASS: launched {len(launched)} fresh {phase} cells; classify retained raw outputs next")


if __name__ == "__main__":
    main()
