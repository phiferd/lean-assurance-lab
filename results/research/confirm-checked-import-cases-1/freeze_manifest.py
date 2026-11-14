"""Generate or check the exact twenty-cell E1 execution manifest; never launch."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from confirmation_common import (
    CONTAINER_LIMITS, HERE, IMAGE, IMAGE_TAG, LEAN_PATH, PINNED, ROOT,
    SUPERVISION, sha256,
)

FAMILIES = {
    "expression": "explorations/runs/EXPLORE-EXPRESSION-PRECONDITION-1",
    "pi": "explorations/runs/EXPLORE-PI-CODOMAIN-ADMISSION-1",
}
TOOL_PATHS = [
    "lib/resource_envelope_supervisor.py",
    "results/research/confirm-checked-import-cases-1/confirmation_common.py",
    "results/research/confirm-checked-import-cases-1/freeze_manifest.py",
    "results/research/confirm-checked-import-cases-1/preflight.py",
    "results/research/confirm-checked-import-cases-1/run_confirmation.py",
    "results/research/confirm-checked-import-cases-1/analyze.py",
    "results/research/confirm-checked-import-cases-1/compare_replay.py",
    "results/research/confirm-checked-import-cases-1/independent-expectation-review.json",
    "results/research/confirm-checked-import-cases-1/runtime-recovery.md",
    "results/research/confirm-checked-import-cases-1/preflight-repair.json",
    "results/research/confirm-checked-import-cases-1/preflight-r2/result.json",
    "tests/test_confirm_checked_import_cases.py",
    "explorations/runs/EXPLORE-EXPRESSION-PRECONDITION-1/Replay.lean",
    "explorations/runs/EXPLORE-EXPRESSION-PRECONDITION-1/analyze.py",
    "explorations/runs/EXPLORE-PI-CODOMAIN-ADMISSION-1/analyze.py",
]


def expression_tree(pair: str, negative: bool) -> tuple[str, str]:
    arg = "(sort (succ 0))" if negative else "(sort 0)"
    body = "(sort 0)" if pair == "V" else "(sort (succ 0))"
    app = f"(app (lam _ (sort (succ 0)) {body}) {arg})"
    typ = "(sort (succ 0))" if pair == "V" else app if pair == "T" else f"(forallE x {app} (sort (succ 0)))"
    val = app if pair == "V" else "(sort 0)" if pair == "T" else "(lam x (sort (succ 0)) (sort 0))"
    return typ, val


def pi_tree(pair: str, negative: bool) -> tuple[list, list]:
    s0, s1, s2 = ["sort", 0], ["sort", 1], ["sort", 2]
    f = ["lam", s1, s0]
    g = ["forallE", s1, s1]
    n = ["forallE", s1, f]
    pi = n if negative else g
    return (pi, f) if pair == "A" else (s2, pi)


def build_manifest() -> dict:
    cells = []
    file_hashes = {path: sha256(ROOT / path) for path in TOOL_PATHS}
    for family, base in FAMILIES.items():
        cases_path = ROOT / base / "cases.json"
        file_hashes[str(cases_path.relative_to(ROOT))] = sha256(cases_path)
        review_path = ROOT / base / "input-review.md"
        file_hashes[str(review_path.relative_to(ROOT))] = sha256(review_path)
        cases = json.loads(cases_path.read_text())
        for case in cases:
            file_hashes[case["path"]] = case["sha256"]
            file_hashes[case["config"]] = case["config_sha256"]
            negative = case["expected"] == "REJECT"
            parsed = expression_tree(case["pair"], negative) if family == "expression" else pi_tree(case["pair"], negative)
            for checker in ("lean", "nanoda"):
                cells.append({
                    "ordinal": len(cells) + 1,
                    "id": f"{family}/{case['id']}/{checker}",
                    "family": family,
                    "source_case_id": case["id"],
                    "pair": f"{family}/{case['pair']}",
                    "checker": checker,
                    "expected": case["expected"],
                    "declaration": case["declaration"],
                    "input": {"path": case["path"], "sha256": case["sha256"]},
                    "config": {"path": case["config"], "sha256": case["config_sha256"]},
                    "parsed_tree": {"type": parsed[0], "value": parsed[1]},
                    "attribution_required": "complete checked declaration identity" if not negative else (
                        "application domain comparison" if family == "expression" else "Pi codomain sort inference"),
                })
    assert len(cells) == 20
    assert sum(cell["expected"] == "ACCEPT" for cell in cells) == 10
    assert sum(cell["expected"] == "REJECT" for cell in cells) == 10
    return {
        "schema_version": 1,
        "item_id": "CONFIRM-CHECKED-IMPORT-CASES-1",
        "evidence_class": "E1",
        "frozen_at": "2026-11-14",
        "question": "Do ten unchanged known checked-import cases produce their independently derived verdicts and checked identities on two exact historical profiles in both an initial run and a fresh replay?",
        "consumer": "Lean Assurance Lab manual checker-profile upgrade check",
        "nonclaims": ["not discovery", "not a fresh holdout", "not general correctness", "not current-tip behavior"],
        "source_revisions": {
            "lean4": "5045d0056413266e57c625dcd7c365b10e377c52",
            "lean4export": "076e8e57707e813375e8f9da8bf989799ace9680",
            "nanoda": "3a2407216ee84a75f9e1aead6803d0578be06ae7",
        },
        "runtime": {
            "image_id": IMAGE,
            "image_tag": IMAGE_TAG,
            "platform": "linux/arm64",
            "image_size_bytes": 3838283731,
            "archive": {
                "path": "external/runtime-images/checked-import-runtime-2026-11-14.tar.zst",
                "size_bytes": 892351532,
                "sha256": "eae9bd60f3dafd5213c58f662d45a2b7591268eb1b6801f37a31556b87ae4f2c",
            },
            "pinned_file_sha256": PINNED,
            "lean_path": LEAN_PATH,
            "container_limits": CONTAINER_LIMITS,
        },
        "supervision": SUPERVISION,
        "phases": ["initial", "replay"],
        "cells_per_phase": 20,
        "total_required_cells": 40,
        "cases": cells,
        "file_sha256": dict(sorted(file_hashes.items())),
        "classification": {
            "accept": "zero exit plus exact parsed declaration identity and complete checked-definition success",
            "reject": "expected nonzero exit plus the pinned boundary-specific diagnostic site",
            "unresolved": "missing/empty/parser/timeout/unrelated panic/identity or supervision failure",
            "pi_a_guard": "generic rejection is unresolved unless declared-type Pi codomain sort inference is identified",
        },
        "freshness": "Each cell is a separately named fresh container created from the exact image and removed after execution; replay uses new names and receipts.",
    }


def encoded() -> bytes:
    return (json.dumps(build_manifest(), indent=2) + "\n").encode()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("select exactly one of --write or --check")
    target = HERE / "execution-manifest.json"
    expected = encoded()
    if args.write:
        target.write_bytes(expected)
        print(f"WROTE {target.relative_to(ROOT)}")
    else:
        if target.read_bytes() != expected:
            raise SystemExit("execution manifest is stale")
        print("PASS: exact twenty-cell manifest is current")


if __name__ == "__main__":
    main()
