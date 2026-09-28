"""Portable command and raw-output custody replay for two frozen Kiota packages."""
from hashlib import sha256
import json
from pathlib import Path


FAMILIES = {
    "kiota-recursor-type-repair-1": ("KIOTA-RECURSOR-TYPE-REPAIR-1", 31, 22),
    "kiota-recursor-pr-refinement-1": ("KIOTA-RECURSOR-PR-REFINEMENT-1", 9, 0),
}


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _relative(root: Path, name: str):
    path = Path(name)
    _require(not path.is_absolute() and ".." not in path.parts and bool(path.parts),
             "unsafe Kiota evidence path")
    resolved = (root / path).resolve()
    _require(resolved.is_relative_to(root) and resolved.is_file(),
             "missing Kiota evidence file")
    return resolved


def _read(root: Path, name: str):
    return json.loads(_relative(root, name).read_bytes())


def validate(root: Path, family: str):
    root = root.resolve()
    _require(family in FAMILIES, "unknown Kiota receipt family")
    item_id, expected_count, expected_historical_mismatches = FAMILIES[family]
    base = root / "results/research" / family / "execution"
    attempts = sorted(base.glob("attempt-*/supervisor.json"))
    _require(len(attempts) == expected_count, "Kiota attempt inventory differs")
    seen = set()
    unresolved_manifest_attempts = []
    for receipt_path in attempts:
        directory = receipt_path.parent
        relative_directory = directory.relative_to(root).as_posix()
        reservation = json.loads((directory / "reservation.json").read_bytes())
        result = json.loads((directory / "result.json").read_bytes())
        receipt = json.loads(receipt_path.read_bytes())
        _require(reservation["attempt"] == result["attempt"]
                 and reservation["cell_id"] == result["cell_id"],
                 "Kiota attempt identity differs")
        identity = (reservation["attempt"], reservation["cell_id"])
        _require(identity not in seen, "duplicate Kiota attempt identity")
        seen.add(identity)
        _require(reservation["directory"] == "execution/" + directory.name,
                 "Kiota attempt directory differs")
        _require(result["result_path"] == relative_directory + "/result.json"
                 and result["receipt"] == relative_directory + "/supervisor.json",
                 "Kiota result/receipt path differs")
        _require(result["manifest"] == reservation["manifest"]
                 and result["manifest_sha256"] == reservation["manifest_sha256"],
                 "Kiota reservation/result manifest differs")
        manifest_path = _relative(root, result["manifest"])
        manifest_bytes = manifest_path.read_bytes()
        _require(result["item_id"] == item_id, "Kiota result item differs")
        if sha256(manifest_bytes).hexdigest() == result["manifest_sha256"]:
            manifest = json.loads(manifest_bytes)
            _require(manifest["item_id"] == item_id
                     and manifest["cell_id"] == result["cell_id"],
                     "Kiota manifest identity differs")
            _require(receipt["cwd"] == manifest["cwd"]
                     and receipt["argv"] == manifest["argv"]
                     and receipt["memory_limit_bytes"] == manifest["memory_bytes"],
                     "Kiota recorded invocation differs")
        else:
            unresolved_manifest_attempts.append(reservation["attempt"])
        for stream in ("stdout", "stderr"):
            path = relative_directory + "/raw." + stream
            _require(result["raw_" + stream] == receipt["raw_" + stream + "_path"] == path,
                     "Kiota raw path differs")
            raw = _relative(root, path).read_bytes()
            _require(sha256(raw).hexdigest() == receipt[stream + "_sha256"]
                     and len(raw) == receipt[stream + "_bytes"],
                     "Kiota raw bytes differ")
    _require(sorted(unresolved_manifest_attempts) == list(range(2, expected_historical_mismatches + 2)),
             "Kiota historical manifest mismatch inventory differs")
    return {"family": family, "attempts": len(attempts),
            "manifest_bound_attempts": len(attempts) - len(unresolved_manifest_attempts),
            "historical_manifest_mismatches": len(unresolved_manifest_attempts),
            "host_launches": 0}
