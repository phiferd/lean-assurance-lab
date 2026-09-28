"""Discover all recorded process families and check replay portability custody.

Absolute command and working-directory values remain recorded evidence. This
audit never resolves them against the current host. It checks their syntax,
repository-local raw streams, and the mandatory replay-test registration.
"""
from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
import importlib
import json
from pathlib import Path
import sys
import unittest


BASELINE_FAMILIES = frozenset({
    "acceptance-impact-pilot-1",
    "child-panic-confirmation-1",
    "kiota-recursor-pr-refinement-1",
    "kiota-recursor-type-repair-1",
    "lazy-reduction-conformance-pilot-1",
    "metamorphic-representation-pilot-2",
    "pipeline-completeness-pilot-1",
    "pipeline-completeness-pilot-2",
    "stateful-validation-pilot-1",
    "survivor-thread-one-child-panic-regression-1",
    "trust-assumption-pipeline-pilot-1",
    "valid-dependent-term-pilot-1",
    "workflow-closure-automation-1",
})
BASELINE_PATH_HASHES = {
    "acceptance-impact-pilot-1": "fe216a098c39a67334dfe27c4820f4e05998f56c06e7da9861f17f4fe37ee34a",
    "child-panic-confirmation-1": "94d6b492395fdcd79b1789d5c816646eade76c50674e03ab1aaac399053a3759",
    "kiota-recursor-pr-refinement-1": "735008744330d3962652fdae182e834d3572515816693ce0b241e9dbe874cd89",
    "kiota-recursor-type-repair-1": "429bd7bb762481f79e241a77974e9a0cde0b5208a76579762582ba1a46e5ab68",
    "lazy-reduction-conformance-pilot-1": "7990b69fe06b06f889c7cd786588ce39926ebb6cf611c58bbad4a6acceb9f2ee",
    "metamorphic-representation-pilot-2": "4e81b59dbdb3c7a2b068f78d1e06eba0a9215ceff94107f32f50a912a9ba7d7d",
    "pipeline-completeness-pilot-1": "e72569dde5ee1bc8069737e48190667f68912601d27ec31a32a16b86f2d8d0cc",
    "pipeline-completeness-pilot-2": "9a37399a484b0be3d6ea4f8d8050bfb3a0ccb1b7b59537980cf200d03bf7d461",
    "stateful-validation-pilot-1": "af32cc3289aaf97567c185b46c5318940340f2528df0cde2667e219017294c17",
    "survivor-thread-one-child-panic-regression-1": "41cc2cebb4a63d59301058342e00ffcaf1f4a7774d81917a8ad2a63c926cc404",
    "trust-assumption-pipeline-pilot-1": "0ce1b525ddb50951d113f9132b792e6cca4b7021074faaf3e20e877a852ad5d3",
    "valid-dependent-term-pilot-1": "f2a369632a0af99cc5938933a46e6486de74c06fdedef2eeda20eec0f08f0a20",
    "workflow-closure-automation-1": "16d58fc46534d98f7921b1417e1dfa897d79f48de3254d04a09db8e069e81dbd",
}
def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _receipts(value):
    if isinstance(value, dict):
        if (isinstance(value.get("cwd"), str)
                and isinstance(value.get("argv"), list)
                and type(value.get("exit_code")) is int):
            yield value
        for child in value.values():
            yield from _receipts(child)
    elif isinstance(value, list):
        for child in value:
            yield from _receipts(child)


def discover(root: Path):
    root = root.resolve()
    research = root / "results/research"
    groups = defaultdict(set)
    receipts = []
    for path in research.rglob("*.json"):
        raw = path.read_bytes()
        if b'"cwd"' not in raw:
            continue
        document = json.loads(raw, object_pairs_hook=_unique_object)
        found = list(_receipts(document))
        if not found:
            continue
        relative = path.relative_to(root).as_posix()
        groups[path.relative_to(research).parts[0]].add(relative)
        receipts.extend((relative, row) for row in found)
    return {key: sorted(value) for key, value in groups.items()}, receipts


def _digest(paths):
    return sha256(("\n".join(paths) + "\n").encode()).hexdigest()


def _test_exists(root: Path, name: str) -> bool:
    parts = name.split(".")
    if len(parts) != 3 or not parts[0].startswith("test_") or not parts[2].startswith("test_"):
        return False
    if not (root / "tests" / (parts[0] + ".py")).is_file():
        return False
    tests_dir = str(root / "tests")
    sys.path.insert(0, tests_dir)
    try:
        module = importlib.import_module(parts[0])
        case = getattr(module, parts[1], None)
        method = getattr(case, parts[2], None)
        return (isinstance(case, type) and issubclass(case, unittest.TestCase)
                and callable(method) and not getattr(case, "__unittest_skip__", False)
                and not getattr(method, "__unittest_skip__", False))
    finally:
        sys.path.remove(tests_dir)


def validate_registration(root: Path, groups, registry):
    if registry.get("schema_version") != 1 or set(registry) != {"schema_version", "families"}:
        raise ValueError("invalid portability registry envelope")
    rows = registry["families"]
    if not isinstance(rows, list):
        raise ValueError("portability families must be a list")
    ids = [row.get("id") for row in rows]
    if ids != sorted(set(ids)):
        raise ValueError("portability families must be unique and sorted")
    if set(ids) != set(groups):
        raise ValueError(f"unregistered receipt families: {sorted(set(groups)-set(ids))}; missing evidence: {sorted(set(ids)-set(groups))}")
    if not BASELINE_FAMILIES.issubset(ids):
        raise ValueError("frozen receipt family removed")
    if set(BASELINE_PATH_HASHES) != BASELINE_FAMILIES:
        raise ValueError("baseline inventory definition differs")
    for row in rows:
        if set(row) != {"id", "receipt_files", "paths_sha256", "replay_test", "portability_test"}:
            raise ValueError(f"invalid portability row: {row.get('id')}")
        family = row["id"]
        paths = groups[family]
        if row["receipt_files"] != len(paths) or row["paths_sha256"] != _digest(paths):
            raise ValueError(f"receipt inventory changed: {family}")
        if family in BASELINE_FAMILIES and row["paths_sha256"] != BASELINE_PATH_HASHES[family]:
            raise ValueError(f"frozen receipt paths changed: {family}")
        replay = row["replay_test"]
        if not isinstance(replay, str) or not _test_exists(root, replay):
            raise ValueError(f"missing active replay test: {family}")
        portable = row["portability_test"]
        if family not in BASELINE_FAMILIES and portable is None:
            raise ValueError(f"new receipt family needs a portability test: {family}")
        if portable is not None and (not isinstance(portable, str)
                                     or not portable.startswith("test_evidence_replay_portability.")
                                     or not _test_exists(root, portable)):
            raise ValueError(f"missing dedicated portability test: {family}")
    return len(rows)


def validate_raw_custody(root: Path, receipts):
    root = root.resolve()
    streams = 0
    recorded_roots = set()
    for source, row in receipts:
        if not Path(row["cwd"]).is_absolute():
            raise ValueError(f"nonabsolute recorded cwd: {source}")
        if not row["argv"] or not all(isinstance(arg, str) for arg in row["argv"]):
            raise ValueError(f"invalid recorded argv: {source}")
        recorded_roots.add(row["cwd"])
        for stream in ("stdout", "stderr"):
            field = f"raw_{stream}_path"
            if field not in row:
                continue
            relative = Path(row[field])
            if relative.is_absolute() or ".." in relative.parts or not relative.parts:
                raise ValueError(f"unsafe raw path: {source}")
            path = (root / relative).resolve()
            if not path.is_relative_to(root) or not path.is_file():
                raise ValueError(f"missing repository raw stream: {source}")
            data = path.read_bytes()
            if (row.get(f"{stream}_sha256") != sha256(data).hexdigest()
                    or row.get(f"{stream}_bytes") != len(data)):
                raise ValueError(f"raw stream differs: {source}")
            streams += 1
    return streams, recorded_roots


def validate(root: Path, *, require_foreign_checkout=False):
    root = root.resolve()
    groups, receipts = discover(root)
    registry = json.loads((root / "config/evidence-replay-portability.json").read_bytes(),
                          object_pairs_hook=_unique_object)
    families = validate_registration(root, groups, registry)
    streams, recorded_roots = validate_raw_custody(root, receipts)
    if require_foreign_checkout and str(root) in recorded_roots:
        raise ValueError("CI checkout equals a recorded evidence-production root")
    return {"families": families, "receipt_files": sum(map(len, groups.values())),
            "receipts": len(receipts), "raw_streams": streams}
