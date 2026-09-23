"""Validate the RECURSOR-TYPE-TRUST-BOUNDARY-1 adjudication package.

The package freezes a regression target without manufacturing a new checker
observation or guessing an under-specified production repair.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
from typing import Any

from lib.research_queue_v4 import load_queue, queue_digest


ROOT = Path(__file__).resolve().parents[1]
ITEM = "RECURSOR-TYPE-TRUST-BOUNDARY-1"
BASE = Path("results/research/recursor-type-trust-boundary-1")
POLICY = BASE / "source-policy.json"
CONTRACT = BASE / "regression-contract.json"
RESULT = BASE / "result.json"
CLOSURE = BASE / "closure.json"
REPORT = BASE / "report.md"
WORK = BASE / "work-record.json"
PROTOCOL = BASE / "protocol.json"
QUEUE = Path("config/research-queue.json")
SUCCESSOR = "KIOTA-RECURSOR-TYPE-DESIGN-1"
REVIEW = Path("results/research/queue-reviews/2026-09-22-recursor-type-trust-boundary-1-closure.json")
SNAPSHOT = "bd0e637267d51f6c7f684038b84c840a59f1c03a"

EXPECTED_POLICY = (
    "For an imported inductive block, a local checker must not make downstream "
    "typing depend on an unvalidated serialized recursor type. It should validate "
    "that type against, or replace it with, a recursor type reconstructed from the "
    "same accepted inductive and constructor group; unchanged inputs that agree "
    "must remain accepted."
)
UNBLOCK = (
    "Commit and validate a Kiota-specific design that constructs the complete "
    "recursor type for supported ordinary, mutual, and nested inductive groups and "
    "specifies a sound comparison or replacement rule with acceptance-preservation "
    "fixtures before editing production checker behavior."
)

SOURCE_BINDINGS = {
    "kiota_archive": ("results/research/semantic-import-contract-1/kiota-source.tar.gz", 4587521,
                      "dacbc7bdb92471f2df8fbd4a31b6b6b07c1a0d3f435bfab9e9b093ddad06aaa8"),
    "kiota_parser": ("external/acceptance-impact-pilot-1-kiota/kiota-9fa2c297dd700fe8fd1712a86bdbb258e1c01c42/src/parser.rs", 46528,
                     "537d94a883cfdceafd20299502a954c9680e177b6ffb20252fa733bc83383f7e"),
    "kiota_environment": ("external/acceptance-impact-pilot-1-kiota/kiota-9fa2c297dd700fe8fd1712a86bdbb258e1c01c42/src/env.rs", 4057,
                          "b8665c8b96f770ffffe6d6ff50e05bd4a468edfb835c665ce98485b1bac0107b"),
    "kiota_type_checker": ("external/acceptance-impact-pilot-1-kiota/kiota-9fa2c297dd700fe8fd1712a86bdbb258e1c01c42/src/tc.rs", 545983,
                           "c5ea600b20ab058f2de4be555391e63b6ae44e38b42a6895946779e6b61b8e3b"),
    "official_parser": ("results/research/arena-inductive-isolation-1/importer-evidence/lean4export-f297dfe2-Parse.lean", 20491,
                        "1f943b5cc776eece6d528937b976509c8bd57d10bc69a39b1c119bfb6d664286"),
    "official_replay": ("results/research/arena-inductive-isolation-1/importer-evidence/installed-lean4-v4.33.0-Replay.lean", 7691,
                        "5ea88ea9b6c374ad74b8c6f5d36117cec00ec64202aff37f7cff0c6765fb746d"),
    "official_wrapper": ("external/lean-kernel-arena/checkers/official-v4.33.0/Main.lean", 968,
                         "f0c209172f79e2b0b6599f7acc989e15a158f4118a6ddab0a567773b75f333bb"),
}

FINDINGS = {
    "KIOTA_RETAINS_SUPPLIED_TYPE": ("kiota_parser", [[484, 515], [565, 579]],
                                     ("let typ = self.require_expr", "pi_telescope_len(&typ)", "ConstantInfo::Recursor", "typ,")),
    "KIOTA_EXPOSES_SUPPLIED_TYPE": ("kiota_environment", [[75, 86], [102, 112]],
                                     ("Recursor {", "pub fn typ", "ConstantInfo::Recursor { typ")),
    "KIOTA_USES_SUPPLIED_TYPE": ("kiota_type_checker", [[1858, 1889], [1930, 1946], [8465, 8705]],
                                  ("ExprData::App", "self.infer_const", "ci.typ()", "check_inductive_group")),
    "KIOTA_STREAM_ORDER": ("kiota_parser", [[866, 936]],
                            ("line by line", "self.handle_line", "self.handle_inductive_block", "self.check_last")),
    "OFFICIAL_RETAINS_INPUT_RECORD": ("official_parser", [[392, 432]],
                                      ("def parseRecInfo", "let type", ".recInfo", "type,")),
    "OFFICIAL_REGENERATES_AND_COMPARES": ("official_replay", [[74, 128], [156, 164], [170, 189]],
                                           ("replayConstants ci.getUsedConstantsAsSet", "Declaration.inductDecl", "postponedRecursors", "info == info'", "checkPostponedRecursors")),
}

PAIR_BINDINGS = {
    "audit": ("results/research/acceptance-impact-pilot-1/pair-audit.json", 6097,
              "bc3e9f48fd17f3c6ebcf96efa8d7b98133f88fc6a7b09f9b1699a8e549379007"),
    "candidate": ("corpus/generated/nanoda-gen-7b603be7dc87-valid-aux-type.ndjson", 6332,
                  "13900d3c26371111800a6c85ba8a9cc3d472beb384cf2c5fde574b8a9e7f36bd"),
    "control": ("corpus/generated/nanoda-gen-7b603be7dc87-valid-control.ndjson", 6332,
                "3b66763082822a74a203fb4dda773ff473e853e73077b8f564c603b56e9610ae"),
}

OBSERVATION_BINDINGS = {
    "stage_1_result": ("results/research/acceptance-impact-pilot-1/stage-1-run-0001/result.json", 9776,
                       "5292903191d359fc2cd307366d0eaff53e569d001e07e7b0ddd701a6b17ee1e7"),
    "stage_2_audit": ("results/research/acceptance-impact-pilot-1/stage-2-artifact-audit.json", 6890,
                      "55576511780da56dda66a78de20d42d03b5124f233a59ecc6b046ba9848245e5"),
    "stage_2_result": ("results/research/acceptance-impact-pilot-1/stage-2-run-0001/result.json", 9582,
                       "b967b13e481f781a97b365a8c3556cd1fa6fe5b1a2e5508f5840d56a77f10fbb"),
}

TEST_SEAM = ("external/acceptance-impact-pilot-1-kiota/kiota-9fa2c297dd700fe8fd1712a86bdbb258e1c01c42/tests/exports.rs", 49582,
             "db3b6313093d4d31830b32699b01a818b86620e968c42465668ac67d35304b8a")

RESULT_BINDINGS = {
    "source_policy": (POLICY.as_posix(), 6630,
                      "5ea52cf6dd37791f7d44e42f28e9b9bc121b2671038f5960e7c56547d0558058"),
    "regression_contract": (CONTRACT.as_posix(), 3219,
                            "eb14c51345b43ad5898344c183dfd651f805e08e6ec0e5fbb84e296be1fb8c2b"),
    "validator": ("scripts/validate-recursor-type-trust-boundary-1", 527,
                  "c59760c8968f36f3017ec561f8e49ee71b9fe9cf29d92864b3b2a65ea6924284"),
    "adversarial_tests": ("tests/test_recursor_type_trust_boundary.py", 4896,
                          "870e5927cdf560f1ae4eb5ac9aacbae06a71aa8305708d9577abef9fec3af795"),
}


class BoundaryError(ValueError):
    """The adjudication or repair-readiness package is invalid."""


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise BoundaryError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> dict[str, Any]:
    try:
        result = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_pairs,
                            parse_constant=lambda token: (_ for _ in ()).throw(
                                BoundaryError(f"non-finite JSON value: {token}")))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise BoundaryError(f"cannot load {path}: {error}") from error
    if not isinstance(result, dict):
        raise BoundaryError(f"JSON root is not an object: {path}")
    return result


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_bytes(root: Path, path: Path | str) -> bytes:
    try:
        return subprocess.check_output(
            ["git", "show", f"{SNAPSHOT}:{Path(path).as_posix()}"],
            cwd=root,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        raise BoundaryError(f"historical snapshot input unavailable: {path}") from error


def verify_historical_binding(root: Path, row: Any, expected: tuple[str, int, str]) -> None:
    wanted = expected_binding(expected)
    if row != wanted:
        raise BoundaryError(f"binding differs: {row!r}")
    data = git_bytes(root, wanted["path"])
    if len(data) != wanted["bytes"] or hashlib.sha256(data).hexdigest() != wanted["sha256"]:
        raise BoundaryError(f"historical bound file differs: {wanted['path']}")


def _safe(root: Path, relative: Any) -> Path:
    if (not isinstance(relative, str) or not relative or Path(relative).is_absolute()
            or ".." in Path(relative).parts):
        raise BoundaryError("path must be repository-relative")
    resolved_root = root.resolve()
    path = (resolved_root / relative).resolve()
    try:
        path.relative_to(resolved_root)
    except ValueError as error:
        raise BoundaryError(f"path escapes repository: {relative}") from error
    return path


def expected_binding(value: tuple[str, int, str]) -> dict[str, Any]:
    return {"path": value[0], "bytes": value[1], "sha256": value[2]}


def verify_binding(root: Path, row: Any, expected: tuple[str, int, str]) -> Path:
    wanted = expected_binding(expected)
    if row != wanted:
        raise BoundaryError(f"binding differs: {row!r}")
    path = _safe(root, wanted["path"])
    if (not path.is_file() or path.is_symlink() or path.stat().st_size != wanted["bytes"]
            or sha256(path) != wanted["sha256"]):
        raise BoundaryError(f"bound file differs: {wanted['path']}")
    return path


def _range_text(path: Path, ranges: list[list[int]]) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    chunks = []
    for start, end in ranges:
        if start < 1 or end < start or end > len(lines):
            raise BoundaryError(f"invalid source line range for {path}: {start}-{end}")
        chunks.append("\n".join(lines[start - 1:end]))
    return "\n".join(chunks)


def validate_policy_value(policy: dict[str, Any], root: Path = ROOT) -> None:
    expected_keys = {
        "schema_version", "item_id", "status", "adjudication_scope", "source_bindings",
        "source_findings", "observed_ordering", "policy", "authority_class",
        "implementation_boundary", "catalog_action", "claim_limits",
        "new_checker_attempts", "production_checker_edits", "external_actions",
    }
    if set(policy) != expected_keys:
        raise BoundaryError("source-policy fields differ")
    if (policy.get("schema_version") != 1 or policy.get("item_id") != ITEM
            or policy.get("status") != "COMPLETE"
            or policy.get("authority_class") != "SOURCE_BOUND_LOCAL_IMPORT_POLICY"
            or policy.get("policy") != EXPECTED_POLICY):
        raise BoundaryError("source-policy identity or scoped policy differs")

    bindings = policy.get("source_bindings")
    if not isinstance(bindings, dict) or set(bindings) != set(SOURCE_BINDINGS):
        raise BoundaryError("source binding roles differ")
    paths: dict[str, Path] = {}
    for role, expected in SOURCE_BINDINGS.items():
        paths[role] = verify_binding(root, bindings[role], expected)

    findings = policy.get("source_findings")
    if not isinstance(findings, list) or len(findings) != len(FINDINGS):
        raise BoundaryError("source findings differ")
    by_id = {row.get("id"): row for row in findings if isinstance(row, dict)}
    if set(by_id) != set(FINDINGS) or len(by_id) != len(findings):
        raise BoundaryError("source finding identities differ")
    for finding_id, (role, ranges, tokens) in FINDINGS.items():
        row = by_id[finding_id]
        if (set(row) != {"id", "binding_role", "line_ranges", "finding"}
                or row.get("binding_role") != role or row.get("line_ranges") != ranges
                or not isinstance(row.get("finding"), str) or not row["finding"]):
            raise BoundaryError(f"source finding differs: {finding_id}")
        source = _range_text(paths[role], ranges)
        for token in tokens:
            if token not in source:
                raise BoundaryError(f"source locator omits {token}: {finding_id}")

    ordering = policy.get("observed_ordering")
    if not isinstance(ordering, dict) or set(ordering) != {"bare_candidate", "extended_candidate"}:
        raise BoundaryError("observed ordering fields differ")
    expected_diagnostics = {
        "bare_candidate": ("results/research/acceptance-impact-pilot-1/stage-1-run-0001/raw/04-official-lean-4.33.0-candidate.stderr",
                           "ba89f6a7d2d19bb689184487a50bf53762f5cbf63111299a79aa0942e5689fc1",
                           b"Invalid recursor LALNest.rec_1"),
        "extended_candidate": ("results/research/acceptance-impact-pilot-1/stage-2-run-0001/raw/04-official-lean-4.33.0-candidate_use.stderr",
                               "ce7a9a7e2c744ef35487c26c7073c7088eb3c574554eecc81e4aec4480915f6f",
                               b"application type mismatch"),
    }
    for role, (relative, digest, token) in expected_diagnostics.items():
        row = ordering[role]
        if (not isinstance(row, dict)
                or set(row) != {"evidence_path", "sha256", "diagnostic", "explanation"}
                or row.get("evidence_path") != relative or row.get("sha256") != digest
                or not isinstance(row.get("explanation"), str) or not row["explanation"]):
            raise BoundaryError(f"ordering evidence differs: {role}")
        raw = _safe(root, relative).read_bytes()
        if hashlib.sha256(raw).hexdigest() != digest or token not in raw:
            raise BoundaryError(f"raw ordering diagnostic differs: {role}")

    boundary = policy.get("implementation_boundary")
    if (not isinstance(boundary, dict)
            or boundary.get("status") != "REPAIR_ALGORITHM_NOT_YET_AUTHORIZED"
            or boundary.get("exact_unblocking_condition") != UNBLOCK
            or not isinstance(boundary.get("missing_inputs"), list)
            or len(boundary["missing_inputs"]) != 2
            or not all(isinstance(row, str) and row for row in boundary["missing_inputs"])):
        raise BoundaryError("implementation boundary or unblock condition differs")
    catalog = policy.get("catalog_action")
    if (not isinstance(catalog, dict) or catalog.get("action") != "NONE"
            or "no new normative catalog authority" not in catalog.get("reason", "")):
        raise BoundaryError("catalog authority boundary differs")
    limits = " ".join(policy.get("claim_limits", [])) if isinstance(policy.get("claim_limits"), list) else ""
    for token in ("not a universal", "not normative authority", "No false-theorem", "soundness"):
        if token not in limits:
            raise BoundaryError(f"claim limits omit {token}")
    if [policy.get(name) for name in ("new_checker_attempts", "production_checker_edits", "external_actions")] != [0, 0, 0]:
        raise BoundaryError("source adjudication performed an unauthorized action")


def validate_contract_value(contract: dict[str, Any], root: Path = ROOT) -> None:
    expected_keys = {
        "schema_version", "item_id", "status", "policy", "preserved_pair",
        "required_regression", "local_test_seam", "preserved_observation_bindings",
        "repair_readiness", "fresh_launch_manifest", "new_checker_attempts",
        "production_checker_edits", "external_actions",
    }
    if set(contract) != expected_keys:
        raise BoundaryError("regression-contract fields differ")
    if (contract.get("schema_version") != 1 or contract.get("item_id") != ITEM
            or contract.get("status") != "FROZEN_REPAIR_READINESS"
            or contract.get("policy") != POLICY.as_posix()):
        raise BoundaryError("regression-contract identity differs")

    pair = contract.get("preserved_pair")
    if not isinstance(pair, dict) or set(pair) != {
        "audit", "candidate", "control", "only_scalar_difference", "same_manifest_pi_arity",
        "candidate_fifth_domain", "control_fifth_domain",
    }:
        raise BoundaryError("preserved pair fields differ")
    for role, expected in PAIR_BINDINGS.items():
        verify_binding(root, pair.get(role), expected)
    if (pair.get("only_scalar_difference") != {
            "pointer": "/104/inductive/recs/0/type", "candidate": 68, "control": 49}
            or pair.get("same_manifest_pi_arity") != 5
            or pair.get("candidate_fifth_domain") != "LALNest"
            or pair.get("control_fifth_domain") != "LALWrap LALNest"):
        raise BoundaryError("preserved pair delta or type spines differ")

    audit = load_json(root / PAIR_BINDINGS["audit"][0])
    audited = audit.get("pair", {})
    candidate_spine = audited.get("type_spines", {}).get("candidate_type_68", {})
    control_spine = audited.get("type_spines", {}).get("control_type_49", {})
    if (audited.get("scalar_differences") != [{"candidate": 68, "control": 49,
                                                "pointer": "/104/inductive/recs/0/type"}]
            or candidate_spine.get("manifest_pi_arity") != 5
            or candidate_spine.get("binders", [{}])[-1].get("type_id") != 28
            or control_spine.get("manifest_pi_arity") != 5
            or control_spine.get("binders", [{}])[-1].get("type_id") != 29):
        raise BoundaryError("pair audit no longer proves the frozen delta")

    required = contract.get("required_regression")
    if required != {
        "candidate_expected": "REJECT", "control_expected": "ACCEPT",
        "candidate_identity": "PRESERVED_EXACTLY", "control_identity": "PRESERVED_EXACTLY",
        "adaptive_replacement": False, "reuse_completed_attempt_as_new_result": False,
    }:
        raise BoundaryError("required regression behavior differs")

    seam = contract.get("local_test_seam")
    if not isinstance(seam, dict):
        raise BoundaryError("local test seam is absent")
    seam_binding = {key: seam.get(key) for key in ("path", "bytes", "sha256")}
    seam_path = verify_binding(root, seam_binding, TEST_SEAM)
    if (seam.get("accept_helper_lines") != [19, 29]
            or seam.get("reject_helper_lines") != [31, 58]
            or seam.get("existing_wrong_arity_regression_lines") != [263, 267]):
        raise BoundaryError("local test seam lines differ")
    seam_text = _range_text(seam_path, [[19, 58], [263, 267]])
    for token in ("fn assert_accept", "fn assert_reject", "extra_rec_wrong_pi_type_rejects"):
        if token not in seam_text:
            raise BoundaryError(f"local test seam omits {token}")

    observations = contract.get("preserved_observation_bindings")
    if not isinstance(observations, dict) or set(observations) != set(OBSERVATION_BINDINGS):
        raise BoundaryError("preserved observation roles differ")
    for role, expected in OBSERVATION_BINDINGS.items():
        verify_binding(root, observations[role], expected)

    readiness = contract.get("repair_readiness")
    if (not isinstance(readiness, dict)
            or readiness.get("outcome") != "VALIDATED_REGRESSION_TARGET_WITH_SOURCE_BOUNDARY"
            or readiness.get("production_edit_ready") is not False
            or readiness.get("exact_unblocking_condition") != UNBLOCK
            or "no source-bound complete recursor-type constructor" not in readiness.get("reason", "")):
        raise BoundaryError("repair-readiness boundary differs")
    if (contract.get("fresh_launch_manifest") is not None
            or [contract.get(name) for name in ("new_checker_attempts", "production_checker_edits", "external_actions")] != [0, 0, 0]):
        raise BoundaryError("contract records an unauthorized launch or edit")


def validate_result_value(result: dict[str, Any], root: Path = ROOT) -> None:
    expected_keys = {
        "schema_version", "item_id", "status", "outcome", "authority_class",
        "conclusion", "policy", "ordering_explanation", "regression_requirement",
        "repair_boundary", "claim_limits", "evidence", "new_checker_attempts",
        "production_checker_edits", "external_actions",
    }
    if set(result) != expected_keys:
        raise BoundaryError("result fields differ")
    if (result.get("schema_version") != 1 or result.get("item_id") != ITEM
            or result.get("status") != "COMPLETE"
            or result.get("outcome") != "VALIDATED_REGRESSION_TARGET_WITH_SOURCE_BOUNDARY"
            or result.get("authority_class") != "SOURCE_BOUND_LOCAL_IMPORT_POLICY"
            or result.get("policy") != EXPECTED_POLICY):
        raise BoundaryError("result identity or policy differs")
    conclusion = result.get("conclusion", "")
    for token in ("stores", "Official Lean 4.33.0", "regenerates", "regression target",
                  "does not by itself authorize"):
        if token not in conclusion:
            raise BoundaryError(f"result conclusion omits {token}")
    if result.get("regression_requirement") != {
        "candidate": "REJECT", "control": "ACCEPT", "pair_replacement": "FORBIDDEN",
        "completed_attempt_reuse_as_new_result": "FORBIDDEN",
    }:
        raise BoundaryError("result regression requirement differs")
    repair = result.get("repair_boundary")
    if (not isinstance(repair, dict) or repair.get("production_edit_ready") is not False
            or repair.get("exact_unblocking_condition") != UNBLOCK
            or "complete recursor-type construction" not in repair.get("missing_input", "")):
        raise BoundaryError("result production repair boundary differs")
    limits = " ".join(result.get("claim_limits", [])) if isinstance(result.get("claim_limits"), list) else ""
    for token in ("not a universal", "does not establish checker soundness", "no new normative authority"):
        if token not in limits:
            raise BoundaryError(f"result limits omit {token}")
    evidence = result.get("evidence")
    if not isinstance(evidence, dict) or set(evidence) != set(RESULT_BINDINGS):
        raise BoundaryError("result evidence roles differ")
    for role, expected in RESULT_BINDINGS.items():
        if role in {"validator", "adversarial_tests"}:
            verify_historical_binding(root, evidence[role], expected)
        else:
            verify_binding(root, evidence[role], expected)
    if [result.get(name) for name in ("new_checker_attempts", "production_checker_edits", "external_actions")] != [0, 0, 0]:
        raise BoundaryError("result records an unauthorized action")


def _validate_closure(root: Path) -> None:
    closure = load_json(root / CLOSURE)
    if set(closure) != {
        "schema_version", "item_id", "status", "outcome", "result", "report",
        "source_policy", "regression_contract", "production_edit_ready",
        "new_checker_attempts", "production_checker_edits", "external_actions",
        "completion_boundary",
    }:
        raise BoundaryError("closure fields differ")
    if (closure.get("schema_version") != 1 or closure.get("item_id") != ITEM
            or closure.get("status") != "COMPLETE"
            or closure.get("outcome") != "VALIDATED_REGRESSION_TARGET_WITH_SOURCE_BOUNDARY"
            or closure.get("result") != RESULT.as_posix()
            or closure.get("report") != REPORT.as_posix()
            or closure.get("source_policy") != POLICY.as_posix()
            or closure.get("regression_contract") != CONTRACT.as_posix()
            or closure.get("production_edit_ready") is not False
            or [closure.get(name) for name in ("new_checker_attempts", "production_checker_edits", "external_actions")] != [0, 0, 0]
            or "complete recursor-type construction" not in closure.get("completion_boundary", "")):
        raise BoundaryError("closure boundary differs")
    report = (root / REPORT).read_text(encoding="utf-8")
    for token in (
        "VALIDATED_REGRESSION_TARGET_WITH_SOURCE_BOUNDARY", "Kiota revision `9fa2c297`",
        "Invalid recursor LALNest.rec_1", "LALNest.rec_1_impact", "LALWrap LALNest",
        "candidate: reject", "unchanged control: accept", "not an authorized production algorithm",
        "No checker was launched", "does not change the declaration-validation catalog",
    ):
        if token.lower() not in report.lower():
            raise BoundaryError(f"report omits {token}")


def _validate_final_state(root: Path) -> None:
    work = load_json(root / WORK)
    if (work.get("item_id") != ITEM or work.get("status") != "COMPLETE"
            or work.get("current_phase") != "COMPLETE"
            or work.get("observations") != {"source_requests": 0, "checker_attempts": 0,
                                             "production_edits": 0, "external_actions": 0}
            or work.get("result", {}).get("outcome") != "VALIDATED_REGRESSION_TARGET_WITH_SOURCE_BOUNDARY"
            or work.get("result", {}).get("production_edit_ready") is not False
            or work.get("result", {}).get("exact_unblocking_condition") != UNBLOCK):
        raise BoundaryError("final work record differs")
    required_refs = {POLICY.as_posix(), CONTRACT.as_posix(), RESULT.as_posix(), CLOSURE.as_posix(),
                     REPORT.as_posix(), "scripts/validate-recursor-type-trust-boundary-1",
                     "tests/test_recursor_type_trust_boundary.py"}
    if not required_refs.issubset(set(work.get("evidence_refs", []))):
        raise BoundaryError("final work record evidence is incomplete")

    protocol = load_json(root / PROTOCOL)
    protocol_result = protocol.get("result", {})
    if (protocol.get("item_id") != ITEM or protocol.get("status") != "COMPLETE"
            or protocol.get("current_phase") != "COMPLETE"
            or protocol_result.get("outcome") != "VALIDATED_REGRESSION_TARGET_WITH_SOURCE_BOUNDARY"
            or protocol_result.get("production_edit_ready") is not False
            or [protocol_result.get(name) for name in ("new_checker_attempts", "production_checker_edits", "external_actions")] != [0, 0, 0]):
        raise BoundaryError("final protocol differs")

    queue = json.loads(git_bytes(root, QUEUE))
    if (queue.get("schema_version") != 4 or queue.get("selected_item") != SUCCESSOR
            or queue.get("handoff", {}).get("status") != "EXECUTABLE"):
        raise BoundaryError("historical queue selection differs")
    items = queue.get("items")
    by_id = {row.get("id"): row for row in items if isinstance(row, dict)} if isinstance(items, list) else {}
    item, successor = by_id.get(ITEM), by_id.get(SUCCESSOR)
    if (not isinstance(item, dict) or item.get("status") != "COMPLETE"
            or item.get("closure", {}).get("outcome") != "BOUNDED_UNRESOLVED"
            or not required_refs.issubset(set(item.get("closure", {}).get("evidence_refs", [])))
            or SUCCESSOR not in item.get("closure", {}).get("recommendation", "")
            or not isinstance(successor, dict) or successor.get("status") != "READY"
            or successor.get("budget") is not None or successor.get("depends_on") != []
            or any(row.get("status") == "ACTIVE" for row in items if isinstance(row, dict))):
        raise BoundaryError("historical queue item or successor differs")
    review_binding = queue.get("strategic_review")
    if (not isinstance(review_binding, dict) or set(review_binding) != {"path", "sha256"}
            or review_binding.get("path") != REVIEW.as_posix()
            or hashlib.sha256(git_bytes(root, REVIEW)).hexdigest() != review_binding.get("sha256")):
        raise BoundaryError("historical strategic review binding differs")
    review = json.loads(git_bytes(root, REVIEW))
    if (review.get("phase") != "CLOSURE" or review.get("stopped_item") != ITEM
            or review.get("selected_item") != SUCCESSOR
            or review.get("queue_sha256") != queue_digest(queue)):
        raise BoundaryError("historical strategic review differs")

    old_plan = git_bytes(root, "docs/research/RECURSOR_TYPE_TRUST_BOUNDARY_1_PLAN.md").decode()
    new_plan = git_bytes(root, "docs/research/KIOTA_RECURSOR_TYPE_DESIGN_1_PLAN.md").decode()
    status = git_bytes(root, "docs/RESEARCH_STATUS.md").decode()
    if "Status: **COMPLETE" not in old_plan or "Status: **READY" not in new_plan:
        raise BoundaryError("plan status handoff differs")
    for token in (f"Selected next item: `{SUCCESSOR}`", "one READY item and no ACTIVE item",
                  "VALIDATED_REGRESSION_TARGET_WITH_SOURCE_BOUNDARY"):
        if token not in status:
            raise BoundaryError(f"research status omits {token}")

    current_queue = load_queue(root, require_ready=True)
    current_items = current_queue.get("items")
    current_by_id = ({row.get("id"): row for row in current_items if isinstance(row, dict)}
                     if isinstance(current_items, list) else {})
    current_item = current_by_id.get(ITEM)
    current_design = current_by_id.get(SUCCESSOR)
    current_repair = current_by_id.get("KIOTA-RECURSOR-TYPE-REPAIR-1")
    selected = current_by_id.get(current_queue.get("selected_item"))
    if (current_queue.get("schema_version") != 4
            or current_queue.get("handoff", {}).get("status") != "EXECUTABLE"
            or not isinstance(current_item, dict)
            or current_item.get("status") != "COMPLETE"
            or current_item.get("closure") != item.get("closure")
            or not isinstance(current_design, dict)
            or current_design.get("status") != "COMPLETE"
            or current_design.get("closure", {}).get("outcome") != "SUCCESS"
            or not isinstance(current_repair, dict)
            or current_repair.get("status") != "COMPLETE"
            or current_repair.get("closure", {}).get("outcome") != "SUCCESS"
            or not isinstance(selected, dict)
            or selected.get("status") not in {"READY", "ACTIVE"}):
        raise BoundaryError("current queue does not preserve and advance the historical successor")


def validate(root: Path = ROOT) -> dict[str, Any]:
    root = Path(root).resolve()
    policy = load_json(root / POLICY)
    contract = load_json(root / CONTRACT)
    validate_policy_value(policy, root)
    validate_contract_value(contract, root)
    validate_result_value(load_json(root / RESULT), root)
    _validate_closure(root)
    _validate_final_state(root)
    return {
        "schema_version": 1,
        "item_id": ITEM,
        "status": "PASS",
        "authority_class": policy["authority_class"],
        "outcome": contract["repair_readiness"]["outcome"],
        "new_checker_attempts": 0,
        "production_checker_edits": 0,
        "external_actions": 0,
        "successor": SUCCESSOR,
    }
