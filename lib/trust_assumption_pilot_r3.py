"""Portable successor helpers for immutable trust-pipeline evidence."""
from pathlib import Path

from lib import trust_assumption_pilot_r2 as p


def rebuild_result(observation_bindings, root=p.ROOT, *, synthetic_fixture=False):
    p.require(len(observation_bindings) == 2, "exactly two observations required")
    cells = []
    controls = []
    scientific = None
    synthetic_root = None
    for route, ob in zip(p.PATHS, observation_bindings):
        observation = p.read(p.verify(ob, root))
        p.require(observation["route"] == route, "observation path order")
        launch = p.read(p.verify(observation["launch"], root))
        p.require(launch["route"] == route, "launch path mismatch")
        protocol_binding = launch["protocol"]
        proto = p.read(p.verify(protocol_binding, root))
        science = p.validate_protocol(proto, root)
        review = p.read(p.verify(proto["prelaunch_review"], root))
        p.require(
            review["status"] == "PASS"
            and review["scientific_manifest"] == proto["scientific_manifest"]
            and review["tooling"] == proto["tooling"],
            "missing/stale launch clearance",
        )
        p.require(
            launch["inputs"] == p.required_inputs(protocol_binding, proto, science, root),
            "incomplete launch inputs",
        )
        if root == p.ROOT:
            for binding in launch["inputs"]:
                p.committed(binding, launch["commit"])
        if scientific is None:
            scientific = proto["scientific_manifest"]
        p.require(scientific == proto["scientific_manifest"], "mixed scientific inputs")
        p.require(
            science["paths"] == p.PATHS
            and science["cells"]
            == [{"path": path, "fixture": fixture["id"]}
                for path in p.PATHS for fixture in science["fixtures"]],
            "matrix mismatch",
        )
        receipt = p.read(p.verify(observation["receipt"], root))
        p.safety(receipt)
        p.require(receipt["exit_code"] == 0, "unsuccessful report process")

        recorded_root = Path(p.read(p.verify(proto["host_tools"], root))["repository_root"])
        if synthetic_fixture:
            expected_paths = [
                str(p.BASE / f"attempt-{index}/observation.json")
                for index in range(2)
            ]
            p.require(
                [binding["path"] for binding in observation_bindings] == expected_paths
                and root != p.ROOT,
                "synthetic fixture mode is restricted to the legacy temporary matrix",
            )
            suffix = p.BASE / "fixtures"
            cwd = Path(receipt["cwd"])
            p.require(cwd.parts[-len(suffix.parts):] == suffix.parts,
                      "synthetic receipt cwd shape")
            candidate_root = cwd.parents[len(suffix.parts) - 1]
            if synthetic_root is None:
                synthetic_root = candidate_root
            p.require(candidate_root == synthetic_root, "mixed synthetic receipt roots")
            recorded_root = synthetic_root

        producer_dir = None
        if route == p.PATHS[1]:
            producer = p.read(p.verify(observation_bindings[0], root))
            producer_dir = (root / producer["module_files"][0]["path"]).parent
            producer_dir = recorded_root / producer_dir.relative_to(root)
        argv, environment, cwd = p.command_contract(
            route,
            (recorded_root / ob["path"]).parent,
            p.read(p.verify(proto["runtime_manifest"], root)),
            producer_dir,
            recorded_root,
        )
        p.require(
            launch["argv"] == receipt["argv"] == argv
            and launch["cwd"] == receipt["cwd"] == cwd
            and launch["environment"] == environment,
            "command/cwd/environment mismatch",
        )
        prefix = str(Path(ob["path"]).parent / "process")
        p.require(
            receipt["raw_stdout_path"] == prefix + ".stdout"
            and receipt["raw_stderr_path"] == prefix + ".stderr",
            "swapped raw output path",
        )
        for stream in ("stdout", "stderr"):
            p.verify({
                "path": receipt["raw_" + stream + "_path"],
                "bytes": receipt[stream + "_bytes"],
                "sha256": receipt[stream + "_sha256"],
            }, root)
        rows = p.report_rows(
            (root / receipt["raw_stdout_path"]).read_text(),
            (root / receipt["raw_stderr_path"]).read_text(),
            science["fixtures"],
        )
        p.require(rows == observation["rows"], "raw-report observation mismatch")
        if route == p.PATHS[0]:
            p.require(
                [Path(binding["path"]).name for binding in observation["module_files"]]
                == p.MODULE_FILES,
                "incomplete producer module family",
            )
            for binding in observation["module_files"]:
                p.require(
                    Path(binding["path"]).parent == Path(ob["path"]).parent
                    and Path(binding["path"]).name.startswith(("TrustFixtures.olean", "TrustFixtures.ir")),
                    "module output path mismatch",
                )
                p.verify(binding, root)
        else:
            p.require(
                launch["generated_module_manifest"] == observation_bindings[0],
                "import producer binding mismatch",
            )
            if root == p.ROOT:
                p.committed(launch["generated_module_manifest"], launch["commit"])
                for binding in producer["module_files"]:
                    p.committed(binding, launch["commit"])
        cells.extend({"path": route, **row} for row in rows)
        control = science["permission_control"]
        row = next(row for row in rows if row["fixture"] == control["target"])
        for label, expected in zip(("sufficient", "insufficient"), control["expected"]):
            actual = p.permission(row["actual_axioms"], control[label])
            controls.append({
                "path": route,
                "fixture": control["target"],
                "policy": label,
                "allowed_axioms": control[label],
                "expected": expected,
                **actual,
            })
    return {
        "schema_version": 1,
        "item_id": "TRUST-ASSUMPTION-PIPELINE-PILOT-1",
        "scientific_manifest": scientific,
        "observations": observation_bindings,
        "cells": cells,
        "permission_controls": controls,
        "status": "SUCCESS" if all(cell["preserved"] for cell in cells)
        and all(control["expected"] == control["status"] for control in controls)
        else "MISMATCH",
        "claim_limits": science["claim_limits"],
    }
