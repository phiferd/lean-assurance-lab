"""Structure-aware NDJSON witness candidates, minimization, and classification."""

from __future__ import annotations

import copy
import hashlib
import json
import random
from pathlib import Path
from typing import Any, Iterable

from nanoda_differential import DifferentialSession


DECLARATION_KEYS = {"axiom", "def", "thm", "opaque", "inductive", "quot"}
IDENTITY_KEYS = {"in", "il", "ie"}
DISCRIMINANT_KEYS = {
    "meta", "str", "num", "param", "succ", "max", "imax", "sort", "bvar",
    "const", "app", "lam", "forallE", "letE", "proj", "lit", "mdata",
    *DECLARATION_KEYS,
}


def canonical_ndjson(records: list[dict[str, Any]]) -> bytes:
    return ("\n".join(json.dumps(row, sort_keys=True, separators=(",", ":")) for row in records) + "\n").encode()


def read_ndjson(path: Path) -> list[dict[str, Any]]:
    records = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line:
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_no}: NDJSON record must be an object")
        records.append(value)
    return records


def undeclared_universe_template() -> list[dict[str, Any]]:
    return [
        {"meta": {"exporter": {"name": "lean4export", "version": "3.1.0"}, "format": {"version": "3.1.0"}, "lean": {"githash": "f72c35b3f637c8c6571d353742168ab66cc22c00", "version": "4.29.1"}}},
        {"in": 1, "str": {"pre": 0, "str": "unused"}},
        {"in": 2, "str": {"pre": 0, "str": "u"}},
        {"il": 1, "param": 2},
        {"ie": 0, "sort": 0},
        {"axiom": {"isUnsafe": False, "levelParams": [2], "name": 1, "type": 0}},
        {"in": 3, "str": {"pre": 0, "str": "bad"}},
        {"const": {"name": 1, "us": [1]}, "ie": 1},
        {"def": {"all": [3], "hints": "opaque", "levelParams": [], "name": 3, "safety": "safe", "type": 0, "value": 1}},
    ]


def _walk(value: Any, path: tuple[Any, ...] = ()) -> Iterable[tuple[tuple[Any, ...], Any]]:
    yield path, value
    if isinstance(value, dict):
        for key, child in value.items():
            yield from _walk(child, (*path, key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk(child, (*path, index))


def _set_path(value: Any, path: tuple[Any, ...], replacement: Any) -> Any:
    result = copy.deepcopy(value)
    cursor = result
    for part in path[:-1]:
        cursor = cursor[part]
    cursor[path[-1]] = replacement
    return result


def _delete_path(value: Any, path: tuple[Any, ...]) -> Any:
    result = copy.deepcopy(value)
    cursor = result
    for part in path[:-1]:
        cursor = cursor[part]
    del cursor[path[-1]]
    return result


def structural_candidates(seed: Path) -> list[dict[str, Any]]:
    records = read_ndjson(seed)
    candidates: list[dict[str, Any]] = []
    declaration_indexes = [
        index for index, row in enumerate(records) if DECLARATION_KEYS & set(row)
    ]
    for index in declaration_indexes:
        candidates.append(
            {
                "records": records[: index + 1],
                "strategy": "declaration-prefix",
                "transformation": f"prefix-through-record-{index}",
                "seed": str(seed),
            }
        )
    for record_index, record in enumerate(records):
        for path, value in _walk(record):
            if not path:
                continue
            key = path[-1]
            replacements: list[tuple[str, Any]] = []
            if key == "levelParams" and isinstance(value, list) and value:
                replacements.append(("remove-level-parameter", value[:-1]))
            elif key == "us" and isinstance(value, list):
                replacements.append(("clear-universe-arguments", []))
                if value:
                    replacements.append(("duplicate-universe-argument", [value[0], value[0]]))
            elif key == "sort" and isinstance(value, int) and value != 0:
                replacements.append(("replace-sort-level-with-zero", 0))
            elif key in {"type", "value", "fn", "arg", "body"} and isinstance(value, int) and value != 0:
                replacements.append((f"replace-{key}-reference-with-zero", 0))
            for label, replacement in replacements:
                changed = copy.deepcopy(records)
                changed[record_index] = _set_path(record, path, replacement)
                candidates.append(
                    {
                        "records": changed,
                        "strategy": "structured-field-mutation",
                        "transformation": f"record-{record_index}:{label}:{'.'.join(map(str, path))}",
                        "seed": str(seed),
                    }
                )
    return candidates


def inductive_metadata_candidates(seed: Path) -> list[dict[str, Any]]:
    """Mutate serialized fields consumed by inductive auxiliary-data checks."""
    records = read_ndjson(seed)
    candidates: list[dict[str, Any]] = []
    numeric_fields = {
        "numParams", "numIndices", "numNested", "numFields", "cidx",
        "nfields", "numMotives", "numMinors", "induct",
    }
    boolean_fields = {"isRec", "isReflexive", "k"}
    membership_fields = {"all", "ctors"}
    for record_index, record in enumerate(records):
        for path, value in _walk(record):
            if not path:
                continue
            key = path[-1]
            replacements: list[tuple[str, Any]] = []
            if key in numeric_fields and isinstance(value, int) and not isinstance(value, bool):
                replacements.append(("increment", value + 1))
                if value > 0:
                    replacements.append(("decrement", value - 1))
            elif key in boolean_fields and isinstance(value, bool):
                replacements.append(("toggle", not value))
            elif key in membership_fields and isinstance(value, list) and value:
                for index in range(len(value)):
                    replacements.append((f"remove-member-{index}", value[:index] + value[index + 1 :]))
            for label, replacement in replacements:
                changed = copy.deepcopy(records)
                changed[record_index] = _set_path(record, path, replacement)
                candidates.append(
                    {
                        "records": changed,
                        "strategy": "inductive-metadata-mutation",
                        "transformation": (
                            f"record-{record_index}:{key}:{label}:{'.'.join(map(str, path))}"
                        ),
                        "seed": str(seed),
                    }
                )
    return candidates


def generate_candidates(
    subsystem: str,
    seed_paths: list[Path],
    random_seed: int,
) -> list[dict[str, Any]]:
    candidates = []
    if subsystem == "universes":
        candidates.append(
            {
                "records": undeclared_universe_template(),
                "strategy": "universe-ownership-template",
                "transformation": "reference-constant-with-undeclared-universe",
                "seed": None,
            }
        )
    if subsystem == "inductive-declarations":
        targeted = []
        generic = []
        for seed in seed_paths:
            targeted.extend(inductive_metadata_candidates(seed))
            generic.extend(structural_candidates(seed))
        randomizer = random.Random(random_seed)
        randomizer.shuffle(targeted)
        randomizer.shuffle(generic)
        candidates.extend(targeted)
        candidates.extend(generic)
    else:
        for seed in seed_paths:
            candidates.extend(structural_candidates(seed))
    if candidates and subsystem != "inductive-declarations":
        first, rest = candidates[0], candidates[1:]
        random.Random(random_seed).shuffle(rest)
        candidates = [first, *rest]
    seen = set()
    unique = []
    for candidate in candidates:
        payload = canonical_ndjson(candidate["records"])
        digest = hashlib.sha256(payload).hexdigest()
        if digest in seen:
            continue
        seen.add(digest)
        candidate["payload"] = payload
        candidate["sha256"] = digest
        unique.append(candidate)
    return unique


def _structural_reductions(records: list[dict[str, Any]]) -> Iterable[list[dict[str, Any]]]:
    for record_index, record in enumerate(records):
        if "meta" in record:
            continue
        for path, value in _walk(record):
            if not path:
                continue
            key = path[-1]
            if isinstance(value, list) and value:
                for index in range(len(value)):
                    changed_record = _set_path(record, path, value[:index] + value[index + 1 :])
                    changed = copy.deepcopy(records)
                    changed[record_index] = changed_record
                    yield changed
            if isinstance(key, str) and key not in IDENTITY_KEYS | DISCRIMINANT_KEYS:
                changed = copy.deepcopy(records)
                changed[record_index] = _delete_path(record, path)
                yield changed


def minimize_witness(
    records: list[dict[str, Any]],
    scratch: Path,
    session: DifferentialSession,
    max_checks: int = 200,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    checks = 0
    metadata_records = [row for row in records if "meta" in row]

    def holds(candidate: list[dict[str, Any]]) -> bool:
        nonlocal checks
        if checks >= max_checks or not candidate:
            return False
        if metadata_records and not all(row in candidate for row in metadata_records):
            return False
        scratch.write_bytes(canonical_ndjson(candidate))
        checks += 1
        return session.evaluate(scratch)["different"]

    current = copy.deepcopy(records)
    granularity = 2
    while len(current) >= 2 and checks < max_checks:
        chunk_size = max(1, len(current) // granularity)
        reduced = False
        for start in range(0, len(current), chunk_size):
            complement = current[:start] + current[start + chunk_size :]
            if holds(complement):
                current = complement
                granularity = max(2, granularity - 1)
                reduced = True
                break
        if not reduced:
            if granularity >= len(current):
                break
            granularity = min(len(current), granularity * 2)

    changed = True
    while changed and checks < max_checks:
        changed = False
        for candidate in _structural_reductions(current):
            if holds(candidate):
                current = candidate
                changed = True
                break
    return current, {"predicate_checks": checks, "max_checks": max_checks}


def semantic_classification(
    baseline_outcome: str,
    candidate_sha256: str,
    expected_outcome: str | None,
    evidence: dict[str, Any] | None,
) -> dict[str, Any]:
    if expected_outcome is None or evidence is None:
        return {"status": "AMBIGUOUS_SEMANTICS", "reason": "NO_MECHANICAL_EXPECTED_OUTCOME_EVIDENCE"}
    witness = evidence.get("witness", {})
    reference_outcome = witness.get("result", {}).get("normalized_outcome")
    evidence_sha = witness.get("sha256")
    if evidence_sha != candidate_sha256:
        return {"status": "AMBIGUOUS_SEMANTICS", "reason": "EXPECTED_OUTCOME_EVIDENCE_BINDS_DIFFERENT_ARTIFACT"}
    if reference_outcome != baseline_outcome:
        return {
            "status": "CHECKER_DISAGREEMENT",
            "reason": "REFERENCE_CHECKER_DIFFERS_FROM_BASELINE",
            "reference_outcome": reference_outcome,
        }
    if reference_outcome != expected_outcome:
        return {"status": "AMBIGUOUS_SEMANTICS", "reason": "REFERENCE_RESULT_DIFFERS_FROM_EXPECTATION"}
    return {
        "status": "CONFIRMED_EXPECTED_OUTCOME",
        "reason": "REFERENCE_EVIDENCE_MATCHES_ARTIFACT_AND_BASELINE",
        "reference_outcome": reference_outcome,
    }
