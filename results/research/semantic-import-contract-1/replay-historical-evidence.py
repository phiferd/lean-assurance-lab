#!/usr/bin/env python3
"""Read exact retained bytes and receipts; never run a checker or write exports."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent


def binding(path, expected=None):
    raw = (ROOT / path).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if expected is not None and digest != expected:
        raise ValueError(f"historical binding differs: {path}")
    return {"path": path, "sha256": digest, "bytes": len(raw)}


def read(path):
    return json.loads((ROOT / path).read_text())


def differences(a, b, pointer=""):
    if type(a) is not type(b):
        return [{"pointer": pointer, "control": a, "candidate": b}]
    if isinstance(a, dict):
        if a.keys() != b.keys():
            raise ValueError("unexpected structural-key difference")
        return [d for k in a for d in differences(a[k], b[k], pointer + "/" + k)]
    if isinstance(a, list):
        if len(a) != len(b):
            raise ValueError("unexpected structural-length difference")
        return [d for i, (x, y) in enumerate(zip(a, b))
                for d in differences(x, y, pointer + "/" + str(i))]
    return [] if a == b else [{"pointer": pointer, "control": a, "candidate": b}]


def decode(records):
    names = {0: "<anonymous>"}
    expressions = {}
    for r in records:
        if "in" in r:
            atom = r.get("str", r.get("num"))
            prefix = names[atom["pre"]]
            component = str(atom.get("str", atom.get("i")))
            names[r["in"]] = component if atom["pre"] == 0 else prefix + "." + component
        if "ie" in r:
            expressions[r["ie"]] = r

    def expr(i):
        r = expressions[i]
        if "bvar" in r:
            return "#" + str(r["bvar"])
        if "sort" in r:
            return "Sort(level-id=" + str(r["sort"]) + ")"
        if "const" in r:
            return names[r["const"]["name"]] + ".{" + ",".join(map(str, r["const"]["us"])) + "}"
        if "app" in r:
            return "(" + expr(r["app"]["fn"]) + " " + expr(r["app"]["arg"]) + ")"
        for kind in ("forallE", "lam"):
            if kind in r:
                x = r[kind]
                return "(" + kind + " " + names[x["name"]] + " : " + expr(x["type"]) + ", " + expr(x["body"]) + ")"
        raise ValueError(f"unhandled selected expression {r}")

    declarations = []
    for i, r in enumerate(records):
        if "inductive" in r:
            for kind, rows in r["inductive"].items():
                for j, d in enumerate(rows):
                    declarations.append({"pointer": f"/{i}/inductive/{kind}/{j}",
                                         "name": names[d["name"]], "kind": kind,
                                         "type_id": d["type"], "type_expression": expr(d["type"])})
    return names, expressions, declarations


def pair(candidate, control):
    cb = binding(candidate["path"], candidate["sha256"])
    pb = binding(control["path"], control["sha256"])
    cs = [json.loads(line) for line in (ROOT / cb["path"]).read_text().splitlines()]
    ps = [json.loads(line) for line in (ROOT / pb["path"]).read_text().splitlines()]
    diffs = differences(ps, cs)
    if len(diffs) != 1:
        raise ValueError("fixed pair no longer differs at exactly one scalar")
    pn, pe, pd = decode(ps)
    cn, ce, cd = decode(cs)
    if pn != cn or pe != ce:
        raise ValueError("fixed pairs must preserve name and expression nodes")
    ptr = diffs[0]["pointer"].rsplit("/", 1)[0]
    out = {"candidate": cb, "control": pb, "record_counts": [len(ps), len(cs)],
           "scalar_differences": diffs, "name_and_expression_nodes_unchanged": True,
           "changed_declaration_control": next(d for d in pd if d["pointer"] == ptr),
           "changed_declaration_candidate": next(d for d in cd if d["pointer"] == ptr)}
    if diffs[0]["pointer"].endswith("/type"):
        selected = {diffs[0]["control"], diffs[0]["candidate"]}
        out["direct_declaration_type_references_before"] = [d for d in pd if d["type_id"] in selected]
        out["direct_declaration_type_references_after"] = [d for d in cd if d["type_id"] in selected]
        out["shared_node_scope"] = "Only LALNest.rec_1's type pointer changes; existing expression 68 is already LALNest.rec's type. No shared expression node is edited. This is graph structure, not a proof about all semantic uses."
    return out


def observers(path):
    d = read(path)
    rows = []
    for i, row in enumerate(d["validators"]):
        rows.append({"receipt_pointer": f"/validators/{i}", "checker": row["checker"],
                     "identity": row["compatibility"]["checker_identity"],
                     "compatibility": row["compatibility"]["status"],
                     "compatibility_reasons": row["compatibility"]["reasons"],
                     "candidate_result": row["result"],
                     "control_result": row["positive_control"]["result"]})
    return {"binding": binding(path), "created_at": d["created_at"], "rows": rows}


def generate():
    matrix_path = "results/investigations/nanoda-restored-declaration-contract-matrix.json"
    matrix = read(matrix_path)
    rows = []
    controls = ["nanoda-restored-recursor/valid-control-reproduction.json",
                "nanoda-restored-recursor-type/control-reproduction.json",
                "nanoda-restored-ctor/control-reproduction.json"]
    for case, control_receipt in zip(matrix["cases"], controls):
        cv = read(case["evidence"]["cross_validation"])
        for key in ("cross_validation", "reproduction"):
            binding(case["evidence"][key], case["evidence"][key + "_sha256"])
        rp = case["evidence"]["reproduction"]
        cp = "results/investigations/" + control_receipt
        reproduction, control_reproduction = read(rp), read(cp)
        binding(reproduction["artifact"]["path"], reproduction["artifact"]["sha256"])
        binding(control_reproduction["artifact"]["path"], control_reproduction["artifact"]["sha256"])
        rows.append({"case_id": case["case_id"], "boundary": case["boundary"],
                     "pair": pair(case["artifact"], cv["validators"][0]["positive_control"]),
                     "cross_validation": observers(case["evidence"]["cross_validation"]),
                     "nanoda_reproduction": {"candidate_receipt": binding(rp),
                       "control_receipt": binding(cp), "candidate_baseline": reproduction["baseline"],
                       "control_baseline": control_reproduction["baseline"],
                       "mutation_spec": binding("mutations/" + reproduction["mutant_id"] + ".json", reproduction["mutation_spec_sha256"]),
                       "identity_limit": "These reproduction receipts bind artifact and mutation bytes, but do not themselves record the baseline source revision or binary hash. No current or fully identified baseline observation is inferred from them."}})
    np = "results/investigations/nanoda-numindices-overrejection/upstream-main.json"
    n = read(np)
    binding(n["cross_validation"]["path"], n["cross_validation"]["sha256"])
    retained_control = {"path": "results/research/semantic-import-contract-1/retained-numindices-control.ndjson",
                        "sha256": n["control"]["sha256"]}
    policy_path = "results/investigations/ecosystem-closure-2026-09-05/upstream/details/nanoda-29-comments.json"
    policy = read(policy_path)
    comment = next(x for x in policy if x["id"] == 5489276523)
    rows.append({"case_id": "nanoda-gen-82dd1d305bfd-inductive-metadata", "boundary": "inductive.numIndices",
                 "pair": pair(n["artifact"], retained_control), "upstream_receipt": binding(np),
                 "original_control_location": n["control"],
                 "retention_note": "Byte-identical copy of existing historical control, not a newly generated scientific variant.",
                 "nanoda_historical_observation": n["upstream_nanoda"],
                 "cross_validation": observers(n["cross_validation"]["path"]),
                 "policy_observation": {"binding": binding(policy_path), "pointer": "/1",
                     "url": comment["html_url"], "author": comment["user"]["login"],
                     "created_at": comment["created_at"], "updated_at": comment["updated_at"],
                     "recorded_body": comment["body"],
                     "scope": "Dated maintainer explanation of Nanoda's retained environment, not a universal export-contract requirement or live issue status."}})
    return {"item_id": "SEMANTIC-IMPORT-CONTRACT-1", "matrix": binding(matrix_path),
            "method": "Parse and hash existing files; compare JSON scalar values and decode existing DAG references. All checker results are copied from dated, content-bound historical receipts. No scientific execution or new export bytes.",
            "cases": rows, "normative_authority": "NOT_ESTABLISHED_BY_THIS_AUDIT",
            "current_checker_execution": False,
            "limits": ["Historical reference-derived expected-outcome labels are preserved in original receipts, not promoted to normative semantic authority.",
                       "Official Lean and Lean4Lean share importer/checking lineage; their agreement is not two independent semantic specifications.",
                       "Nanoda numIndices current-upstream wording belongs to its 2026-08-26 receipt; it is not a claim about today's source."]}


if __name__ == "__main__":
    payload = json.dumps(generate(), indent=2, sort_keys=True) + "\n"
    if sys.argv[1:] == ["--check"]:
        if (HERE / "historical-observations.json").read_text() != payload:
            raise SystemExit("historical observations differ")
        print("historical observations replay: PASS")
    elif not sys.argv[1:]:
        print(payload, end="")
    else:
        raise SystemExit("usage: replay-historical-evidence.py [--check]")
