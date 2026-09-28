"""Read-only portable replay of the committed binder observer process evidence.

Recorded absolute commands are historical data. Only paths under the supplied
checkout are opened, so replay does not need the original host or toolchain.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path


BASE = Path("results/research/binder-model-pilot-1")
PROFILES = ("official-lean-4.33.0", "kiota-2d2a9fa")


class ReplayError(ValueError):
    pass


def _object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ReplayError(f"duplicate key: {key}")
        value[key] = item
    return value


def _constant(value):
    raise ReplayError(f"nonfinite JSON: {value}")


def _loads(data: bytes):
    try:
        return json.loads(data, object_pairs_hook=_object, parse_constant=_constant)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ReplayError(f"malformed retained JSON: {exc}") from exc


def _read(root: Path, relative: Path) -> bytes:
    if relative.is_absolute() or not relative.parts or ".." in relative.parts:
        raise ReplayError(f"unsafe retained path: {relative}")
    path = root / relative
    if not path.is_file():
        raise ReplayError(f"missing retained file: {relative}")
    return path.read_bytes()


def _json(root: Path, relative: Path):
    return _loads(_read(root, relative))


def _bound(root: Path, row: dict) -> bytes:
    if set(row) != {"path", "bytes", "sha256"}:
        raise ReplayError("invalid retained binding")
    data = _read(root, Path(row["path"]))
    if len(data) != row["bytes"] or sha256(data).hexdigest() != row["sha256"]:
        raise ReplayError(f"retained binding differs: {row['path']}")
    return data


def _lines(data: bytes, count: int):
    if not data.endswith(b"\n"):
        raise ReplayError("retained stream lacks final newline")
    lines = data.splitlines()
    if len(lines) != count:
        raise ReplayError(f"retained stream has {len(lines)} rows, expected {count}")
    return [_loads(line) for line in lines]


def _canonical(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode()


def replay(root: Path) -> dict:
    """Recompute all forty retained raw observations without launching a tool."""
    root = Path(root)
    execution = _json(root, BASE / "execution-manifest.json")
    science = _json(root, BASE / "scientific-manifest.json")
    lock = _json(root, BASE / "corpus-lock.json")
    smoke = _json(root, BASE / "smoke/result.json")
    review = _json(root, BASE / "independent-prelaunch-review.json")
    result = _json(root, BASE / "runs/attempt-0001/result.json")
    for name, document in (("scientific-manifest.json", science),
                           ("execution-manifest.json", execution),
                           ("corpus-lock.json", lock), ("smoke/result.json", smoke),
                           ("independent-prelaunch-review.json", review)):
        if not isinstance(document, dict):
            raise ReplayError(f"invalid retained document: {name}")
    if execution["scientific_manifest"] != {
                "path": str(BASE / "scientific-manifest.json"),
                "bytes": len(_read(root, BASE / "scientific-manifest.json")),
                "sha256": sha256(_read(root, BASE / "scientific-manifest.json")).hexdigest(),
            }:
        raise ReplayError("scientific manifest binding differs")
    for field, path in (("scientific_manifest_sha256", BASE / "scientific-manifest.json"),
                        ("execution_manifest_sha256", BASE / "execution-manifest.json"),
                        ("corpus_lock_sha256", BASE / "corpus-lock.json"),
                        ("smoke_result_sha256", BASE / "smoke/result.json")):
        if review.get(field) != sha256(_read(root, path)).hexdigest():
            raise ReplayError(f"prelaunch binding differs: {field}")
    if review.get("verdict") != "PASS_FOR_SCIENTIFIC_LAUNCH":
        raise ReplayError("prelaunch verdict differs")
    if (science.get("fixed_vector_count") != 10000
            or science.get("comparison_count_per_observer") != 15000
            or lock.get("scientific_manifest_sha256")
            != sha256(_read(root, BASE / "scientific-manifest.json")).hexdigest()
            or lock.get("execution_manifest_sha256")
            != sha256(_read(root, BASE / "execution-manifest.json")).hexdigest()
            or smoke.get("status") != "PASS"):
        raise ReplayError("retained science/corpus/smoke scope differs")
    if (result.get("status") != "COMPLETE_MATCH" or result.get("attempt") != 1
            or len(result.get("cells", [])) != 40 or result.get("mismatches") != []):
        raise ReplayError("retained result envelope differs")
    for field, path in (("scientific_manifest_sha256", BASE / "scientific-manifest.json"),
                        ("execution_manifest_sha256", BASE / "execution-manifest.json"),
                        ("corpus_lock_sha256", BASE / "corpus-lock.json"),
                        ("prelaunch_review_sha256", BASE / "independent-prelaunch-review.json")):
        if result.get(field) != sha256(_read(root, path)).hexdigest():
            raise ReplayError(f"retained result binding differs: {field}")
    if execution.get("profiles") != list(PROFILES) or execution.get("batch_count") != 20:
        raise ReplayError("retained execution scope differs")
    files = {row["path"]: row for row in lock["files"]}
    if len(files) != 23:
        raise ReplayError("retained corpus inventory differs")
    for row in lock["files"]:
        _bound(root, row)
    full = _read(root, BASE / "corpus/vectors.ndjson").splitlines(keepends=True)
    if len(full) != 10000 or any(not line.endswith(b"\n") for line in full):
        raise ReplayError("retained corpus length differs")
    stages = 0
    observations = 0
    peak_rss = {}
    profile_counts = {profile: {"processes": 0, "vector_observations": 0,
                                "stage_outputs": 0} for profile in PROFILES}
    recorded_root = None
    for cell_index, (profile, batch) in enumerate(
            (profile, batch) for profile in PROFILES for batch in range(20)):
        cell = result["cells"][cell_index]
        if (cell.get("profile"), cell.get("batch")) != (profile, batch):
            raise ReplayError("retained cell order differs")
        input_rel = BASE / f"corpus/batch-{batch:02d}.ndjson"
        if cell.get("input") != files[str(input_rel)]:
            raise ReplayError("retained cell input binding differs")
        inputs_raw = _bound(root, files[str(input_rel)])
        if inputs_raw != b"".join(full[batch * 500:(batch + 1) * 500]):
            raise ReplayError("retained batch partition differs")
        inputs = _lines(inputs_raw, 500)
        cell_rel = BASE / f"runs/attempt-0001/{profile}/batch-{batch:02d}"
        receipt_rel = cell_rel / "receipt.json"
        _bound(root, cell["receipt"])
        if cell["receipt"]["path"] != str(receipt_rel):
            raise ReplayError("retained receipt path differs")
        receipt = _json(root, receipt_rel)
        cwd = receipt.get("cwd")
        if not isinstance(cwd, str) or not Path(cwd).is_absolute():
            raise ReplayError("invalid recorded workdir")
        if recorded_root is None:
            recorded_root = cwd
        elif cwd != recorded_root:
            raise ReplayError("recorded workdir changed within matrix")
        old_root = Path(cwd)
        expected_argv = ([str(Path(execution["runtime"][0]["path"])), "--run",
                          str(old_root / BASE / "BinderObserver.lean"), str(old_root / input_rel)]
                         if profile == PROFILES[0] else
                         [str(old_root / BASE / "bin/kiota-observer"), str(old_root / input_rel)])
        if receipt.get("argv") != expected_argv:
            raise ReplayError("recorded command differs")
        if (receipt.get("exit_code") != 0 or receipt.get("timed_out") is not False
                or receipt.get("memory_exceeded") is not False
                or receipt.get("memory_monitor_error") is not None
                or receipt.get("cleanup_complete") is not True
                or receipt.get("memory_limit_bytes") != 3221225472
                or type(receipt.get("maximum_observed_rss_bytes")) is not int
                or receipt["maximum_observed_rss_bytes"] <= 0
                or receipt["maximum_observed_rss_bytes"] > 3221225472
                or type(receipt.get("memory_monitor_samples")) is not int
                or receipt["memory_monitor_samples"] <= 0):
            raise ReplayError("retained process safety differs")
        peak_rss[profile] = max(peak_rss.get(profile, 0),
                                receipt["maximum_observed_rss_bytes"])
        for stream in ("stdout", "stderr"):
            relative = cell_rel / f"process.{stream}"
            if receipt.get(f"raw_{stream}_path") != str(relative):
                raise ReplayError("retained raw path differs")
            data = _read(root, relative)
            if (receipt.get(f"{stream}_bytes") != len(data)
                    or receipt.get(f"{stream}_sha256") != sha256(data).hexdigest()):
                raise ReplayError("retained raw stream hash differs")
            if stream == "stderr" and data:
                raise ReplayError("retained stderr is nonempty")
            if stream == "stdout":
                outputs = _lines(data, 500)
        counted = 0
        for wanted, observed in zip(inputs, outputs):
            if (set(observed) != {"id", "outputs"}
                    or observed["id"] != wanted["id"]
                    or type(observed["outputs"]) is not list
                    or len(observed["outputs"]) != len(wanted["expected"])):
                raise ReplayError("retained observer row schema/order differs")
            for actual, expected in zip(observed["outputs"], wanted["expected"]):
                if _canonical(actual) != _canonical(expected):
                    raise ReplayError("retained observer output differs")
                counted += 1
        comparison = _json(root, cell_rel / "comparison.json")
        if comparison != {"status": "MATCH", "vectors": 500,
                          "stage_outputs": counted, "mismatches": []}:
            raise ReplayError("retained comparison differs")
        if cell.get("comparison") != comparison:
            raise ReplayError("retained result cell differs")
        observations += 500
        stages += counted
        profile_counts[profile]["processes"] += 1
        profile_counts[profile]["vector_observations"] += 500
        profile_counts[profile]["stage_outputs"] += counted
    if (observations, stages) != (20000, 30000):
        raise ReplayError("replayed accounting differs")
    if (result.get("vector_observations"), result.get("stage_outputs")) != (observations, stages):
        raise ReplayError("recorded accounting differs")
    return {"status": "PASS", "processes": 40, "vector_observations": observations,
            "stage_outputs": stages, "mismatches": 0, "peak_rss_bytes": peak_rss,
            "profiles": profile_counts,
            "host_launches": 0}
