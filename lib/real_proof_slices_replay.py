"""Portable replay of the fixed real-proof-slices process evidence.

Recorded host paths are historical data. Replaying them never opens or runs
the original executable; repository-relative inputs and raw streams are read
from the supplied checkout.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import re

from lib.metamorphic_pilot_runner import classify


BASE = Path("results/research/real-proof-slices-pilot-1")


class ReplayError(ValueError):
    pass


def _read(root: Path, relative: Path | str) -> bytes:
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts:
        raise ReplayError(f"unsafe repository path: {relative}")
    target = (root / path).resolve()
    if not target.is_relative_to(root.resolve()) or not target.is_file():
        raise ReplayError(f"missing repository file: {relative}")
    return target.read_bytes()


def _json(root: Path, relative: Path | str) -> dict:
    return json.loads(_read(root, relative))


def _bound(root: Path, relative: Path | str, digest: str, size: int | None = None) -> bytes:
    raw = _read(root, relative)
    if sha256(raw).hexdigest() != digest or (size is not None and len(raw) != size):
        raise ReplayError(f"bound bytes differ: {relative}")
    return raw


def _safe_process(root: Path, receipt: dict) -> tuple[bytes, bytes]:
    if (receipt["exit_code"] != 0 or receipt["timed_out"] or receipt["memory_exceeded"]
            or receipt["memory_monitor_error"] or not receipt["cleanup_complete"]
            or receipt["memory_monitor_samples"] <= 0
            or receipt["maximum_observed_rss_bytes"] <= 0):
        raise ReplayError("unsafe recorded process")
    streams = []
    for kind in ("stdout", "stderr"):
        streams.append(_bound(root, receipt[f"raw_{kind}_path"],
                              receipt[f"{kind}_sha256"], receipt[f"{kind}_bytes"]))
    return streams[0], streams[1]


def replay(root: Path) -> dict:
    root = root.absolute()
    controls = _json(root, BASE / "execution-controls.json")
    manifest = _json(root, BASE / "execution-manifest.json")
    result = _json(root, BASE / "execution/attempt-0001/result.json")
    preflight = _json(root, BASE / "rss-preflight.json")
    if (controls.get("schema") != "real-proof-slices-execution-controls-v1"
            or manifest.get("schema") != "real-proof-slices-execution-manifest-v1"
            or result.get("schema") != "real-proof-slices-execution-result-v1"
            or result.get("status") != "COMPLETE" or preflight.get("status") != "PASS"):
        raise ReplayError("incomplete fixed execution evidence")
    _bound(root, BASE / "execution-controls.json", manifest["control_sha256"])
    _bound(root, BASE / "execution-manifest.json", preflight["manifest_sha256"])
    runtime = controls["runtime"]
    profiles = {row["id"]: row for row in controls["profiles"]}
    if set(profiles) != {"official-lean-4.33.0", "nanoda-6ae1f0c"}:
        raise ReplayError("profile set differs")
    pre = preflight["receipt"]
    original_root = Path(pre["cwd"])
    if (not original_root.is_absolute() or pre["argv"] != [runtime["python_path"],
            "-c", "import time; time.sleep(0.1)"]):
        raise ReplayError("preflight invocation differs")
    _safe_process(root, pre)
    artifacts = {row["case"]: row for row in manifest["artifacts"]}
    cases = controls["case_order"]
    if (len(cases) != 12 or len(set(cases)) != 12 or set(artifacts) != set(cases)
            or len(manifest["artifacts"]) != 12):
        raise ReplayError("fixed case inventory differs")
    ready = set()
    for case in cases:
        artifact = artifacts[case]
        receipt = _json(root, artifact["receipt_path"])
        _bound(root, artifact["receipt_path"], artifact["receipt_sha256"])
        if receipt["case"] != case or receipt["disposition"] != artifact["disposition"]:
            raise ReplayError(f"slice receipt identity differs: {case}")
        if receipt["disposition"] == "READY":
            _bound(root, artifact["path"], artifact["sha256"], artifact["bytes"])
            ready.add(case)
        elif receipt["disposition"] != "OVERSIZE":
            raise ReplayError(f"unresolved slice: {case}")
    expected = [cell for cell in controls["matrix"] if cell["case"] in ready]
    if (len(ready) != 9 or len(expected) != 18 or manifest["matrix"] != expected
            or len(result["cells"]) != 18):
        raise ReplayError("fixed process projection differs")
    for cell, observed in zip(expected, result["cells"]):
        if any(observed.get(key) != cell[key] for key in ("ordinal", "case", "profile")):
            raise ReplayError("observed process order differs")
        receipt = observed["process_receipt"]
        profile = profiles[cell["profile"]]
        if cell["profile"] == "official-lean-4.33.0":
            argv = [str(original_root / profile["binary"]),
                    str(original_root / artifacts[cell["case"]]["path"])]
            cwd = str(original_root)
        else:
            argv = profile["argv"]
            cwd = str(original_root / profile["cwd"])
        if receipt["argv"] != argv or receipt["cwd"] != cwd:
            raise ReplayError("recorded command/cwd differs")
        stdout, stderr = _safe_process(root, receipt)
        if (cell["profile"] == "official-lean-4.33.0"
                and (not re.fullmatch(rb"Accepted [0-9]+ declarations[.]\n", stdout) or stderr)):
            raise ReplayError("official success output differs")
        if classify(cell["profile"], receipt, stdout, stderr) != (
                observed["outcome"], observed["reason"]):
            raise ReplayError("recorded classification differs")
        if observed["outcome"] != "ACCEPT":
            raise ReplayError("nonaccepting fixed process")
    return {"status": "PASS", "cases": 12, "ready": 9, "oversize": 3,
            "processes": 18, "accepted": 18, "host_launches": 0}
