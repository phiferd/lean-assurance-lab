"""Render and validate the no-duplicate 9face association successor."""
from __future__ import annotations

import hashlib
import importlib.machinery
import importlib.util
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from lib import survivor_let_reuse as reuse
from lib.survivor_let_result import validate_chain


ROOT = Path(__file__).resolve().parents[1]
ITEM = "SURVIVOR-LET-ASSOCIATION-1"
MUTANT = "nanoda-gen-9face4e6a6f7"
REUSE_BASE = "results/research/survivor-let-reuse-1"
BASE = "results/research/survivor-let-association-1"
REGISTRY = "results/mutants/registry.jsonl"
HISTORICAL_REGISTRY = (
    "results/research/alt-survivors-2026-09-08/evidence/historical/"
    "results/mutants/registry.jsonl"
)
HISTORICAL_INVENTORY = (
    "results/research/alt-survivors-2026-09-08/evidence/historical/"
    "results/survivors/inventory.jsonl"
)
INVENTORY = "results/survivors/inventory.jsonl"
ASSOCIATION = f"results/mutants/{MUTANT}/reuse-association-v1.json"
CONFIRMATION = f"results/mutants/{MUTANT}/reuse-association-confirmation-v1.json"
TRANSITION = BASE + "/historical-transition.json"
RESULT = BASE + "/result.json"
REPORT = BASE + "/report.md"
EVIDENCE_MANIFEST = BASE + "/evidence-manifest.json"
SCHEMA = "schemas/survivor-let-association.schema.json"
PREFIX_LINES = 606
PREFIX_SHA256 = "dcd605397c53c52fab087117b02561d0c7b62c93629688753aa58c61af286944"
RECORDED_AT = "2026-09-08T15:55:02.147840+00:00"

FROZEN = {
    REUSE_BASE + "/result.json": (1522, "f2eb19294c25ed2c54dc9e497b6405832ab2dbe356d8c624bfb5b8a44e293224"),
    REUSE_BASE + "/association-recommendation.json": (1557, "b6c31ef5c07a68de8e150b47f05374715d95638add857f0475380407c86f33f6"),
    REUSE_BASE + "/report.md": (1192, "43189dff294aed73631b5734f593342265fcff25d6b631d80d1663179e47dab5"),
    REUSE_BASE + "/evidence-manifest.json": (10175, "039e49d1e35d906a9d4ee74bbf7821019483c9829622f0d1583fc35807ffc78d"),
    REUSE_BASE + "/run-0001/execution/events.jsonl": (13332, "96a34373e1e41d5eccd557ee907ae83bf72fbf4deef2b85b19c2ae8fe5732d9a"),
    "mutations/nanoda-gen-9face4e6a6f7.json": (956, "fde62195b585faec91ada6b493b3d1c8940845f5bccbc296ac870aa884690886"),
    "results/mutants/nanoda-gen-9face4e6a6f7/scheduled-comparison.json": (985, "9c75a15b5fa13112fe0f6ae49e2cfadc6d7e28c8c39c630f9253340dfe2b48cd"),
    "corpus/generated/nanoda-gen-21ef4d1d32a1-let-value-type-mismatch.ndjson": (601, "52e75d78c948d466e90fb203e7a04192dde4273c7319d44fc261fd2b3b6beeac"),
    "corpus/controls/nanoda-gen-21ef4d1d32a1-matching-let-control.ndjson": (601, "63ef460ca2aac739482c983457cd14309f4d7149ecd2c0d79d53fe2a410c9f16"),
    "corpus/expected/nanoda-gen-21ef4d1d32a1-witness.json": (3360, "e65b8cff534a0ea0efa68889a4081449cc1a43cae0a221790388803161da40c0"),
    "corpus/augmented/manifest-v2.json": (2546, "b9b3ff304b5584165049bd40707712ac8cf0e1a77a67d200ce50ca1ed3fc5622"),
    "results/witnesses/nanoda-gen-21ef4d1d32a1-witness/confirmation.json": (11252, "1d57fbf5da7681f41ad98008091f5d32edd9cda9dbc9d5af2b0010b46be739a4"),
    "results/witnesses/nanoda-gen-21ef4d1d32a1-witness/metadata.json": (5058, "ae2ec7cc2e7551d409955430851601c66e5f87469438bc75f82443e6b5d23840"),
    "results/mutants/nanoda-gen-21ef4d1d32a1/augmented-comparison-v2.json": (11268, "1a1221c86690b5a4e183d9c7953d648c41a648eac0df94d06fadc5b3c4dde493"),
    "scripts/build-witness-admission": (15838, "64e1ef4f50d1f9bc39ab06cabafacf9df464b40f9aa55d6d5c3f79815a00be02"),
    "config/declaration-validation-catalog.json": (563265, "33992703c088bde0994fafe1050931b93c4273f36cee26d9fafab33005ff1a35"),
    "config/declaration-validation-evidence-locks/publication-study-complete-adjudication.json": (1184, "f6047eb4ffb16d10f33c1511ac0cc577250add5c0ce35ee1dd57f68c1098e025"),
}
PAIR = {
    "candidate": "corpus/generated/nanoda-gen-21ef4d1d32a1-let-value-type-mismatch.ndjson",
    "control": "corpus/controls/nanoda-gen-21ef4d1d32a1-matching-let-control.ndjson",
    "expected_outcome": "corpus/expected/nanoda-gen-21ef4d1d32a1-witness.json",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def binding(root: Path, path: str, *, data: bytes | None = None) -> dict:
    payload = data if data is not None else (root / path).read_bytes()
    return {"path": path, "bytes": len(payload), "sha256": sha256_bytes(payload)}


def output_binding(path: str, body: str) -> dict:
    return {"path": path, "bytes": len(body.encode()), "sha256": sha256_bytes(body.encode())}


def load(root: Path, path: str) -> dict:
    return json.loads((root / path).read_text(encoding="utf-8"))


def require_frozen(root: Path) -> None:
    for path, (size, digest) in FROZEN.items():
        require(
            binding(root, path) == {"path": path, "bytes": size, "sha256": digest},
            "frozen association input changed: " + path,
        )


def registry_predecessor(root: Path) -> str:
    lines = (root / REGISTRY).read_text(encoding="utf-8").splitlines(keepends=True)
    require(len(lines) >= PREFIX_LINES, "registry is shorter than the historical successor")
    predecessor = "".join(lines[:PREFIX_LINES])
    require(
        sha256_bytes(predecessor.encode()) == PREFIX_SHA256,
        "wrong 606-line historical registry predecessor",
    )
    return predecessor


def validate_inputs(root: Path, require_full_payload: bool = False) -> tuple[str, dict, dict]:
    root = root.resolve()
    require_frozen(root)
    predecessor = registry_predecessor(root)
    require(
        (root / HISTORICAL_REGISTRY).read_text(encoding="utf-8") == predecessor,
        "historical registry copy changed",
    )
    if not (root / TRANSITION).is_file():
        require(
            (root / INVENTORY).read_bytes()
            == (root / HISTORICAL_INVENTORY).read_bytes(),
            "survivor inventory changed before this successor",
        )

    result = load(root, REUSE_BASE + "/result.json")
    recommendation = load(root, REUSE_BASE + "/association-recommendation.json")
    require(
        result.get("selected_mutant") == MUTANT
        and result.get("scientific_status") == "FIXED_PAIR_DISTINGUISHES_MUTANT",
        "wrong fresh result identity or status",
    )
    require(
        result.get("comparison")
        == {
            "control-baseline": "ACCEPT",
            "control-mutant": "ACCEPT",
            "candidate-baseline": "TYPECHECK_REFUSAL",
            "candidate-mutant": "ACCEPT",
        },
        "fresh comparison is not the fixed attributable distinction",
    )
    require(
        recommendation.get("target") == MUTANT
        and recommendation.get("preserved_state", {}).get("duplicate_corpus_artifacts") == 0,
        "reuse recommendation changed",
    )
    require(
        recommendation.get("evidence", {}).get("existing_candidate")
        == binding(root, PAIR["candidate"])
        and recommendation.get("evidence", {}).get("existing_control")
        == binding(root, PAIR["control"]),
        "reuse recommendation no longer binds the exact admitted pair",
    )

    events, _ = reuse.Ledger(root).read()
    state = validate_chain(events)
    require(
        state["charged_seconds"] == result["total_process_seconds"],
        "fresh result cost does not match the raw ledger",
    )
    if require_full_payload:
        binary = result["build"]["binary"]
        require(
            binding(root, binary["path"])["sha256"] == binary["sha256"],
            "fresh selected binary changed",
        )

    manifest = load(root, "corpus/augmented/manifest-v2.json")
    require(
        len(manifest.get("tests", [])) == 3
        and all(MUTANT not in json.dumps(row, sort_keys=True) for row in manifest["tests"]),
        "historical augmented manifest contains a duplicate 9face regression",
    )
    duplicates = [
        path
        for path in (root / "corpus").rglob("*")
        if path.is_file() and MUTANT in path.name
    ]
    require(not duplicates, "duplicate 9face corpus artifact exists")
    return predecessor, result, recommendation


def render(root: Path, require_full_payload: bool = False) -> dict[str, str]:
    root = root.resolve()
    predecessor, result, _ = validate_inputs(root, require_full_payload)
    mutation = load(root, f"mutations/{MUTANT}.json")
    common = {
        "schema_version": 1,
        "kind": "SURVIVOR_LET_REUSE_ASSOCIATION",
        "item_id": ITEM,
        "mutant_id": MUTANT,
        "recorded_at": RECORDED_AT,
        "governing_plan": binding(
            root, "docs/research/SURVIVOR_LET_ASSOCIATION_PLAN.md"
        ),
        "producer": {
            "script": binding(root, "scripts/build-survivor-let-association"),
            "implementation": binding(root, "lib/survivor_let_association.py"),
            "schema": binding(root, SCHEMA),
        },
        "fresh_result": binding(root, REUSE_BASE + "/result.json"),
        "fresh_execution": binding(root, REUSE_BASE + "/run-0001/execution/events.jsonl"),
        "mutation_spec": binding(root, f"mutations/{MUTANT}.json"),
        "source_mutation": {
            key: mutation[key]
            for key in (
                "function",
                "source_file",
                "source_span",
                "source_column",
                "original",
                "mutated",
                "mutation_operator",
                "operator_family",
                "subsystem",
            )
        },
        "reused_candidate": binding(root, PAIR["candidate"]),
        "reused_control": binding(root, PAIR["control"]),
        "reused_expected_outcome": binding(root, PAIR["expected_outcome"]),
        "historical_21ef_admission": {
            "confirmation": binding(
                root, "results/witnesses/nanoda-gen-21ef4d1d32a1-witness/confirmation.json"
            ),
            "comparison": binding(
                root, "results/mutants/nanoda-gen-21ef4d1d32a1/augmented-comparison-v2.json"
            ),
            "metadata": binding(
                root, "results/witnesses/nanoda-gen-21ef4d1d32a1-witness/metadata.json"
            ),
            "augmented_manifest": binding(root, "corpus/augmented/manifest-v2.json"),
        },
        "historical_registry_predecessor": {
            "path": HISTORICAL_REGISTRY,
            "lines": PREFIX_LINES,
            "bytes": len(predecessor.encode()),
            "sha256": PREFIX_SHA256,
        },
        "declaration_validation": {
            "stable_identity": "EXPR.LET.VALUE_TYPE_MATCH",
            "catalog": binding(root, "config/declaration-validation-catalog.json"),
            "evidence_lock": binding(
                root,
                "config/declaration-validation-evidence-locks/"
                "publication-study-complete-adjudication.json",
            ),
            "authority_status": "PROVISIONAL_UNCHANGED",
            "normative_source_change": False,
            "scope": (
                "Mutation evidence is an implementation observation and is not "
                "semantic authority."
            ),
        },
    }
    confirmation = {
        **common,
        "status": "CONFIRMED_FRESH_REUSE_ASSOCIATION",
        "mechanical_predicate": result["comparison"],
        "limits": (
            "Exact pinned implementation comparison only; no new official "
            "observation or semantic authority."
        ),
    }
    confirmation_body = canonical(confirmation)
    association = {
        **common,
        "status": "KILLED",
        "classification": "MEANINGFUL_SEMANTIC",
        "classification_scope": (
            "Meaningful source-mutant distinction for the exact fresh 9face "
            "comparison using an existing admitted regression; no semantic or "
            "official-observer authority."
        ),
        "confirmation": output_binding(CONFIRMATION, confirmation_body),
        "no_duplicate_corpus_artifact": True,
        "new_corpus_byte_variants": 0,
    }
    schema = load(root, SCHEMA)
    Draft202012Validator.check_schema(schema)
    errors = list(Draft202012Validator(schema).iter_errors(association))
    require(
        not errors,
        "association schema failure: " + "; ".join(error.message for error in errors),
    )
    association_body = canonical(association)

    row = {
        "id": MUTANT,
        "status": "KILLED",
        "classification": "MEANINGFUL_SEMANTIC",
        "updated_at": RECORDED_AT,
        "checker": mutation["checker"],
        "subsystem": mutation["subsystem"],
        "source_file": mutation["source_file"],
        "source_span": mutation["source_span"],
        "mutation_operator": mutation["mutation_operator"],
        "operator_family": mutation["operator_family"],
        "comparison": ASSOCIATION,
        "confirmation": CONFIRMATION,
        "reused_witness": PAIR["candidate"],
        "reused_control": PAIR["control"],
        "reused_expected_outcome": PAIR["expected_outcome"],
        "classification_scope": association["classification_scope"],
        "notes": (
            "Fresh fixed-pair association; exact 21ef corpus artifacts reused "
            "without duplicate admission."
        ),
    }
    successor_registry = (
        predecessor + json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n"
    )

    historical_registry = binding(root, HISTORICAL_REGISTRY)
    historical_inventory = binding(root, HISTORICAL_INVENTORY)
    transition = {
        "schema_version": 1,
        "kind": "SURVIVOR_LET_ASSOCIATION_HISTORICAL_TRANSITION",
        "item_id": ITEM,
        "recorded_at": RECORDED_AT,
        "predecessor_reuse_outputs": [
            binding(root, REUSE_BASE + "/" + name)
            for name in (
                "result.json",
                "association-recommendation.json",
                "report.md",
                "evidence-manifest.json",
            )
        ],
        "historical_substitutions": [
            {
                "live_path": REGISTRY,
                "original_live_binding": {**historical_registry, "path": REGISTRY},
                "historical_binding": historical_registry,
            },
            {
                "live_path": INVENTORY,
                "original_live_binding": {**historical_inventory, "path": INVENTORY},
                "historical_binding": historical_inventory,
            },
        ],
        "historical_admission": {
            "producer": binding(root, "scripts/build-witness-admission"),
            "registry": historical_registry,
            "augmented_manifest": binding(root, "corpus/augmented/manifest-v2.json"),
            "confirmation_21ef": binding(
                root, "results/witnesses/nanoda-gen-21ef4d1d32a1-witness/confirmation.json"
            ),
            "comparison_21ef": binding(
                root, "results/mutants/nanoda-gen-21ef4d1d32a1/augmented-comparison-v2.json"
            ),
        },
        "successor_state": {
            "registry": binding(root, REGISTRY, data=successor_registry.encode()),
            "survivor_inventory": {**historical_inventory, "path": INVENTORY},
            "association": output_binding(ASSOCIATION, association_body),
            "confirmation": output_binding(CONFIRMATION, confirmation_body),
            "new_corpus_byte_variants": 0,
        },
    }
    result_artifact = {
        "schema_version": 1,
        "item_id": ITEM,
        "outcome": "SUCCESS",
        "canonical_update": {
            "mutant_id": MUTANT,
            "status": "KILLED",
            "classification": "MEANINGFUL_SEMANTIC",
            "registry_appends": 1,
            "association": ASSOCIATION,
            "confirmation": CONFIRMATION,
        },
        "population_transition": {
            "evaluated_mutants": {"before": 161, "after": 161},
            "killed_mutants": {"before": 138, "after": 139},
            "surviving_mutants": {"before": 23, "after": 22},
            "pending_survivors": {"before": 7, "after": 6},
            "modeled_score": {"before": "134/144", "after": "135/144"},
            "meaningful_score": {"before": "134/137", "after": "135/138"},
        },
        "reuse": {
            "candidate": binding(root, PAIR["candidate"]),
            "control": binding(root, PAIR["control"]),
            "expected_outcome": binding(root, PAIR["expected_outcome"]),
            "new_corpus_byte_variants": 0,
            "new_witness_metadata_records": 0,
        },
        "historical_transition": TRANSITION,
        "declaration_validation": {
            "stable_identity": "EXPR.LET.VALUE_TYPE_MATCH",
            "authority_status": "PROVISIONAL_UNCHANGED",
            "catalog_changes": 0,
            "evidence_lock_changes": 0,
            "normative_source_changes": 0,
        },
        "research_counts": {
            "checker_launches": 0,
            "build_launches": 0,
            "proof_launches": 0,
            "setup_launches": 0,
            "research_network_requests": 0,
            "scientific_byte_variants": 0,
            "new_corpus_byte_variants": 0,
            "external_research_actions": 0,
        },
        "limits": (
            "The classification records the exact pinned source-mutant distinction. "
            "It does not establish semantic authority, a new official observation, "
            "or a distinct upstream defect."
        ),
    }
    result_body = canonical(result_artifact)
    report_body = (
        "# Survivor let association result\n\n"
        "The no-duplicate association succeeded. The canonical registry now records "
        "nanoda-gen-9face4e6a6f7 as KILLED / MEANINGFUL_SEMANTIC from the fresh "
        "fixed comparison. It points to the exact existing 21ef candidate, control, "
        "and expected-outcome bytes; no 9face corpus artifact or witness metadata was "
        "created.\n\n"
        "The mutation population remains 161 evaluated mutants. Killed moves from "
        "138 to 139, surviving from 23 to 22, and the pending survivor set from seven "
        "to six. The modeled denominator remains 144 because the previously measured "
        "survival was already included; its numerator moves from 134 to 135.\n\n"
        "The unchanged historical admission producer re-rendered its preserved "
        "606-line successor, and the completed reuse outputs validate through the "
        "explicit historical substitution map. The declaration-validation catalog "
        "entry remains provisional and unchanged. No checker, build, proof, setup, "
        "network, external action, scientific byte variant, or corpus byte variant "
        "was launched or created.\n"
    )
    manifest_artifact = {
        "schema_version": 1,
        "kind": "SURVIVOR_LET_ASSOCIATION_CLOSURE",
        "inputs": [
            ({**historical_inventory, "path": INVENTORY}
             if path == INVENTORY else binding(root, path))
            for path in sorted(
                set(FROZEN)
                | {
                    HISTORICAL_REGISTRY,
                    HISTORICAL_INVENTORY,
                    INVENTORY,
                    "docs/research/SURVIVOR_LET_ASSOCIATION_PLAN.md",
                    BASE + "/entry-decision.json",
                    "lib/survivor_let_association.py",
                    "scripts/build-survivor-let-association",
                    SCHEMA,
                }
            )
        ],
        "derived_outputs": [
            ASSOCIATION,
            CONFIRMATION,
            TRANSITION,
            REGISTRY,
            RESULT,
            REPORT,
        ],
        "note": "Generated prose and classification state do not replace the bound raw evidence.",
    }
    return {
        ASSOCIATION: association_body,
        CONFIRMATION: confirmation_body,
        TRANSITION: canonical(transition),
        RESULT: result_body,
        REPORT: report_body,
        EVIDENCE_MANIFEST: canonical(manifest_artifact),
        REGISTRY: successor_registry,
    }


def validate_historical_admission(
    root: Path, require_full_payload: bool = False
) -> dict:
    """Run the unchanged old producer against its preserved 606-line registry."""
    root = root.resolve()
    loader = importlib.machinery.SourceFileLoader(
        "historical_witness_admission", str(root / "scripts/build-witness-admission")
    )
    spec = importlib.util.spec_from_loader(loader.name, loader)
    old = importlib.util.module_from_spec(spec)
    loader.exec_module(old)
    require(
        old.PREDECESSOR_REGISTRY_LINES == 604
        and old.PREDECESSOR_REGISTRY_SHA256
        == "1806b2ea4a3c16a29065318bcbd4bc8c95cb904da380bdf8a97addd44a81a76e",
        "old admission predecessor constants changed",
    )
    old.REGISTRY = HISTORICAL_REGISTRY
    if not require_full_payload:
        strict_verify = old.verify

        def clone_safe_verify(row: dict) -> None:
            if not row["path"].startswith("external/"):
                strict_verify(row)

        old.verify = clone_safe_verify
    outputs = old.build()
    require(
        outputs[HISTORICAL_REGISTRY]
        == (root / HISTORICAL_REGISTRY).read_text(encoding="utf-8"),
        "old producer no longer renders the preserved 606-line registry",
    )
    for path, body in outputs.items():
        if path != HISTORICAL_REGISTRY:
            require(
                (root / path).read_text(encoding="utf-8") == body,
                "historical admission output changed: " + path,
            )
    return {
        "status": "PASS",
        "historical_registry_lines": PREFIX_LINES,
        "historical_registry_sha256": PREFIX_SHA256,
        "old_admission_outputs_verified": True,
    }


def _write_atomic(path: Path, body: str) -> None:
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(body, encoding="utf-8")
    temporary.replace(path)


def check(
    root: Path, *, write: bool = False, require_full_payload: bool = False
) -> dict:
    root = root.resolve()
    outputs = render(root, require_full_payload)
    historical = validate_historical_admission(root, require_full_payload)
    current_registry = (root / REGISTRY).read_text(encoding="utf-8")
    predecessor = registry_predecessor(root)
    successor = outputs[REGISTRY]
    if write:
        require(
            current_registry in {predecessor, successor},
            "refusing to overwrite a later registry successor",
        )
        for path, body in outputs.items():
            destination = root / path
            destination.parent.mkdir(parents=True, exist_ok=True)
            _write_atomic(destination, body)
    else:
        require(current_registry.startswith(successor),
                "live registry does not preserve the exact association prefix")
        for path, body in outputs.items():
            if path == REGISTRY:
                continue
            require(
                (root / path).is_file()
                and (root / path).read_text(encoding="utf-8") == body,
                "stale association successor: " + path,
            )
    return historical
