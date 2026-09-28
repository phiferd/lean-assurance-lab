"""Validate the bounded BINDER-MODEL-PILOT-1 result without launching tools."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

from lib.binder_model_audit import audit_corpus
from lib.binder_model_replay import BASE, replay


class ClosureError(ValueError):
    pass


def _json(path: Path):
    return json.loads(path.read_bytes())


def _bound(root: Path, row: dict) -> None:
    if set(row) != {"path", "sha256"}:
        raise ClosureError("invalid result evidence binding")
    path = Path(row["path"])
    if path.is_absolute() or ".." in path.parts:
        raise ClosureError("unsafe result evidence path")
    if sha256((root / path).read_bytes()).hexdigest() != row["sha256"]:
        raise ClosureError(f"result evidence changed: {path}")


def _distinct_inputs(path: Path) -> int:
    distinct = set()
    for line in path.read_bytes().splitlines():
        row = json.loads(line)
        projection = {"operation": row["operation"], "context_length": len(row["context"]),
                      "source": row["source"], "arguments": row["arguments"],
                      "parameters": row["parameters"]}
        distinct.add(json.dumps(projection, sort_keys=True, separators=(",", ":")))
    return len(distinct)


def validate(root: Path) -> dict:
    root = Path(root)
    result = _json(root / BASE / "result.json")
    review = _json(root / BASE / "independent-observation-review.json")
    corpus_review = _json(root / BASE / "independent-corpus-review.json")
    if (result.get("item_id") != "BINDER-MODEL-PILOT-1"
            or result.get("status") != "COMPLETE"
            or result.get("outcome") != "NO_OBSERVED_DIFFERENCE"
            or result.get("question_answered") is not True):
        raise ClosureError("result disposition differs")
    if (review.get("verdict") != "PASS_OBSERVATIONS_NO_DIFFERENCE"
            or corpus_review.get("verdict") != "PASS_FOR_CORPUS_SEALING"):
        raise ClosureError("independent review disposition differs")
    for row in result["evidence"].values():
        if isinstance(row, dict):
            _bound(root, row)
    raw = (root / BASE / "runs/attempt-0001/result.json").read_bytes()
    if review.get("result_sha256") != sha256(raw).hexdigest():
        raise ClosureError("observation review does not bind raw result")
    if corpus_review.get("metrics", {}).get("distinct_structural_operation_inputs") != 5091:
        raise ClosureError("distinct-input audit differs")
    audit = audit_corpus(root / BASE / "corpus/vectors.ndjson")
    if audit != _json(root / BASE / "corpus/audit.json") or audit["status"] != "PASS":
        raise ClosureError("corpus audit replay differs")
    if _distinct_inputs(root / BASE / "corpus/vectors.ndjson") != 5091:
        raise ClosureError("distinct structural input count differs")
    observed = replay(root)
    scope = result["scope"]
    if (scope.get("vector_rows"), scope.get("distinct_structural_operation_inputs"),
            scope.get("capture_collision_rows"), scope.get("stage_outputs_total")) != (
            10000, 5091, 2000, 30000):
        raise ClosureError("reported scope differs")
    if (scope.get("operation_family_strata") != audit["operation_family_strata"]
            or scope.get("capture_collision_rows") != audit["capture_collision_vectors"]
            or scope.get("stage_outputs_per_profile") != 15000
            or scope.get("profiles") != ["official-lean-4.33.0", "kiota-2d2a9fa"]):
        raise ClosureError("reported operation/profile scope differs")
    for profile in scope["profiles"]:
        stated = result["observations"][profile]
        counted = observed["profiles"][profile]
        if (stated.get("processes") != counted["processes"]
                or stated.get("vector_observations") != counted["vector_observations"]
                or stated.get("stage_outputs") != counted["stage_outputs"]
                or counted != {"processes": 20, "vector_observations": 10000,
                               "stage_outputs": 15000}):
            raise ClosureError(f"reported profile accounting differs: {profile}")
    if (result["observations"].get("mismatches") != 0
            or observed["processes"] != scope["observer_processes"]
            or observed["vector_observations"] != scope["vector_observations"]
            or observed["stage_outputs"] != scope["stage_outputs_total"]
            or observed["peak_rss_bytes"] != {
                profile: result["observations"][profile]["maximum_observed_rss_bytes"]
                for profile in scope["profiles"]}):
        raise ClosureError("reported observation accounting differs")
    report = (root / BASE / "report.md").read_text()
    if not all(f"## {heading}" in report for heading in (
            "What did we find?", "Is it interesting?", "Does it require more work?")):
        raise ClosureError("plain-language report opening missing")
    return {"status": "PASS", "vectors": 10000, "distinct_structural_inputs": 5091,
            "stage_outputs": 30000, "mismatches": 0, "host_launches": 0}
