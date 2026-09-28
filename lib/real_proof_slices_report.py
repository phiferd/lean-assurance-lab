"""Build the canonical result and derived human report for the fixed pilot."""
from __future__ import annotations

import json
from pathlib import Path

from lib.real_proof_slices import ROOT
from lib.real_proof_slices_closure import validate

BASE=ROOT/"results/research/real-proof-slices-pilot-1"
RESULT=BASE/"result.json"
REPORT=BASE/"report.md"


def _read(path:Path)->dict:
    return json.loads(path.read_text())


def build() -> tuple[bytes,bytes]:
    checked=validate()
    science=_read(BASE/"scientific-manifest.json")
    matrix=_read(BASE/"execution/attempt-0001/result.json")
    cells={(row["case"],row["profile"]):row for row in matrix["cells"]}
    cases=[]
    for source in science["sources"]:
        for selected in source["selected"]:
            case=f"{source['source']}-{selected['slot']:02d}"
            receipt_path=BASE/"slices"/f"{case}.json"
            receipt=_read(receipt_path)
            outcomes={profile:cells[(case,profile)]["outcome"] for profile in checked["profiles"] if (case,profile) in cells}
            disposition="ACCEPT_BOTH" if receipt["disposition"]=="READY" and set(outcomes.values())=={"ACCEPT"} else receipt["disposition"]
            cases.append({"case":case,"source":source["source"],"name":selected["name"],
                          "source_line":selected["source_line"],"source_row_sha256":selected["source_row_sha256"],
                          "slice_receipt":str(receipt_path.relative_to(ROOT)),"slice_rows":receipt["record_count"],
                          "slice_bytes":receipt["would_be_bytes"],"slice_sha256":receipt["output_sha256"],
                          "disposition":disposition,"observer_outcomes":outcomes})
    if len(cases)!=12 or sum(c["disposition"]=="ACCEPT_BOTH" for c in cases)!=9 or sum(c["disposition"]=="OVERSIZE" for c in cases)!=3:
        raise ValueError("fixed disposition counts differ")
    result={"schema":"real-proof-slices-result-v1","item_id":"REAL-PROOF-SLICES-PILOT-1",
            "date":"2026-09-28","outcome":"SUCCESS","question_answer":"Nine independently audited dependency-complete slices were accepted by both supported observer profiles; three fixed Std selections exceeded committed size ceilings. No compatibility difference was observed in the executed cells.",
            "summary":checked,"cases":cases,
            "observer_scope":"official Lean 4.33.0 and Nanoda 6ae1f0c, exact binary/configuration and host execution controls; exit-based observations only",
            "source_scope":"three retained Gate-8 exports, lean4export 3.1.0 / Lean 4.29.1; legacy coverage-revision mismatch preserved; not fresh holdouts",
            "recommendation":{"action":"Retain the provenance-preserving slicer, independent auditor and nine accepted real-proof slices as a local regression asset; no external contribution from this all-agreement pilot.",
                              "target":"Lean Assurance Lab real-proof-slices corpus and validation scripts",
                              "priority":"NORMAL","prerequisites":"Keep exact source/tooling/observer bindings and review any later source or ceiling change as a separately frozen successor.",
                              "supporting_evidence":["results/research/real-proof-slices-pilot-1/source-reuse-review.json","results/research/real-proof-slices-pilot-1/scientific-manifest.json","results/research/real-proof-slices-pilot-1/independent-artifact-audit-review.json","results/research/real-proof-slices-pilot-1/independent-observation-review.json","results/research/real-proof-slices-pilot-1/execution/attempt-0001/result.json"]},
            "limits":["The original exports were previously observed; this is not fresh holdout evidence.",
                      "Agreement of two implementations is not semantic authority or a soundness claim.",
                      "Nanoda's bound success contract is silent exit zero and does not emit a per-declaration checked-object trace.",
                      "Three oversize selections were not launched; their semantic outcomes remain unobserved.",
                      "Source acceptance did not establish slice acceptance; the nine ready slices were separately observed."]}
    result_bytes=json.dumps(result,indent=2,sort_keys=True).encode()+b"\n"
    lines=["# Real proof slices pilot 1", "", "Outcome: **SUCCESS**, scoped to the retained inputs and supported observer profiles.", "",
           "The fixed selection produced twelve declarations from `init`, `std`, and `cedar`. Independent closure audit passed all twelve receipts. Nine slices fit the 8,000,000-byte and 120,000-record ceilings; official Lean 4.33.0 and Nanoda `6ae1f0c` accepted every one of their 18 bound cells. Three fixed `std` slices were oversize and were not launched.", "",
           "| Case | Selected declaration | Closure rows | Derived bytes | Disposition |", "| --- | --- | ---: | ---: | --- |"]
    for case in cases:
        lines.append(f"| `{case['case']}` | `{case['name']}` | {case['slice_rows']:,} | {case['slice_bytes']:,} | {case['disposition']} |")
    lines.extend(["", "The independent auditor reconstructed typed name, universe, expression, declaration, grouped inductive/recursor, quotient and environment closure from the retained source bytes, checked row provenance and order, and rejected the planned negative controls. The first real-case audit exposed a prose-only protocol/manifest binding defect; its failed attempts and reviewed R2 tooling repair remain preserved. The initial RSS preflight encountered sandbox denial of `/bin/ps`; the actual-host retry passed with five positive samples and complete cleanup. All 18 observed cells had positive RSS and complete cleanup.", "",
                  f"Observed process time across the 18 cells was {checked['process_seconds']:.3f} seconds, and maximum recorded child-group RSS was {checked['maximum_observed_rss_bytes']:,} bytes. The exact raw execution is in [`attempt-0001/result.json`](execution/attempt-0001/result.json); the [independent observation review](independent-observation-review.json) verifies its 18 receipts and streams.", "",
                  "The selected libraries were already observed, and the Gate-8 legacy coverage-revision mismatch remains. Checker agreement is not semantic authority or a soundness claim. Nanoda's supported profile reports silent exit-zero success, with no per-declaration checked-object trace. The three oversize cases have no semantic observation; none was replaced after selection.", "",
                  "**Recommendation:** Retain the slicer, auditor, and nine accepted slices as a local regression asset at normal priority. No external contribution is warranted by this all-agreement result. Any extension of sources, feature rule, or ceilings needs a separately frozen successor and exact source/tooling/observer review.", ""])
    return result_bytes,("\n".join(lines)).encode()


def write()->None:
    result,report=build();RESULT.write_bytes(result);REPORT.write_bytes(report)


def check()->None:
    result,report=build()
    if RESULT.read_bytes()!=result or REPORT.read_bytes()!=report:
        raise ValueError("real-proof-slices report is stale")
