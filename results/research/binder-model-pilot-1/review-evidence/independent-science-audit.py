"""Read-only independent replay of binder pilot scientific raw evidence."""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[4]
BASE = ROOT / "results/research/binder-model-pilot-1"


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def pairs(items):
    out = {}
    for key, value in items:
        assert key not in out, "duplicate JSON key"
        out[key] = value
    return out


def reject_constant(value):
    raise AssertionError("nonfinite JSON constant: " + value)


def parse(raw):
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=reject_constant)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def read(path):
    return parse(path.read_bytes())


def bound(row):
    path = ROOT / row["path"]
    raw = path.read_bytes()
    assert len(raw) == row["bytes"] and digest(raw) == row["sha256"], row["path"]
    return raw


def lines(raw):
    assert raw.endswith(b"\n"), "missing final newline"
    values = raw.splitlines()
    assert all(values), "blank NDJSON row"
    return [parse(value) for value in values]


execution = read(BASE / "execution-manifest.json")
result = read(BASE / "runs/attempt-0001/result.json")
for key, name in [("scientific_manifest_sha256", "scientific-manifest.json"),
                  ("execution_manifest_sha256", "execution-manifest.json"),
                  ("corpus_lock_sha256", "corpus-lock.json"),
                  ("prelaunch_review_sha256", "independent-prelaunch-review.json")]:
    assert result[key] == digest((BASE / name).read_bytes()), key
lock = read(BASE / "corpus-lock.json")
for row in lock["files"]:
    bound(row)
full = (BASE / "corpus/vectors.ndjson").read_bytes().splitlines(keepends=True)
assert len(full) == 10000
expected_order = [(profile, batch) for profile in execution["profiles"] for batch in range(20)]
assert [(cell["profile"], cell["batch"]) for cell in result["cells"]] == expected_order
metrics = {}
for cell in result["cells"]:
    profile, batch = cell["profile"], cell["batch"]
    raw_input = bound(cell["input"])
    assert raw_input == b"".join(full[batch * 500:(batch + 1) * 500])
    inputs = lines(raw_input)
    assert len(inputs) == 500
    receipt = parse(bound(cell["receipt"]))
    assert receipt["exit_code"] == 0 and receipt["stderr_bytes"] == 0
    for key in ("timed_out", "memory_exceeded"):
        assert receipt[key] is False, key
    assert receipt["memory_monitor_error"] is None
    assert receipt["cleanup_complete"] is True
    assert receipt["memory_monitor_samples"] > 0
    assert 0 < receipt["maximum_observed_rss_bytes"] <= execution["process_safety"]["rss_ceiling_bytes"]
    assert receipt["memory_limit_bytes"] == execution["process_safety"]["rss_ceiling_bytes"]
    assert 0 < receipt["elapsed_seconds"] <= execution["process_safety"]["timeout_seconds"]
    assert receipt["memory_backend"]["backend"] == "macos-ps-process-group-rss-v2"
    assert receipt["memory_backend"]["preflight_samples"] > 0
    assert receipt["memory_backend"]["preflight_maximum_rss_bytes"] > 0
    original_root = receipt["cwd"]
    prefix = original_root + "/results/research/binder-model-pilot-1/"
    input_arg = prefix + f"corpus/batch-{batch:02d}.ndjson"
    if profile == "official-lean-4.33.0":
        expected_argv = [execution["runtime"][0]["path"], "--run", prefix + "BinderObserver.lean", input_arg]
    else:
        expected_argv = [prefix + "bin/kiota-observer", input_arg]
    assert receipt["argv"] == expected_argv
    raw = {}
    for role in ("stdout", "stderr"):
        raw[role] = (ROOT / receipt[f"raw_{role}_path"]).read_bytes()
        assert len(raw[role]) == receipt[f"{role}_bytes"]
        assert digest(raw[role]) == receipt[f"{role}_sha256"]
    observed = lines(raw["stdout"])
    assert len(observed) == 500
    stages = 0
    for source, actual in zip(inputs, observed):
        assert type(actual) is dict and set(actual) == {"id", "outputs"}
        expected = {"id": source["id"], "outputs": source["expected"]}
        assert canonical(actual) == canonical(expected), source["id"]
        stages += len(expected["outputs"])
    comparison = {"status": "MATCH", "vectors": 500, "stage_outputs": stages, "mismatches": []}
    assert cell["comparison"] == comparison
    comparison_path = ROOT / cell["receipt"]["path"]
    assert read(comparison_path.with_name("comparison.json")) == comparison
    item = metrics.setdefault(profile, {"processes": 0, "vectors": 0, "stage_outputs": 0,
                                       "elapsed_seconds": 0.0, "maximum_observed_rss_bytes": 0})
    item["processes"] += 1
    item["vectors"] += 500
    item["stage_outputs"] += stages
    item["elapsed_seconds"] += receipt["elapsed_seconds"]
    item["maximum_observed_rss_bytes"] = max(item["maximum_observed_rss_bytes"], receipt["maximum_observed_rss_bytes"])
assert result["status"] == "COMPLETE_MATCH" and result["mismatches"] == []
assert result["vector_observations"] == 20000 and result["stage_outputs"] == 30000
assert all(m["processes"] == 20 and m["vectors"] == 10000 and m["stage_outputs"] == 15000 for m in metrics.values())
print(json.dumps({"status": "PASS", "profiles": metrics, "scientific_processes": 40,
                  "vector_observations": 20000, "stage_outputs": 30000, "mismatches": 0}, indent=2))
