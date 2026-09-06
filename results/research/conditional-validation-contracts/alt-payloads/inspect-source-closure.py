#!/usr/bin/env python3
"""Offline generator/verifier for the CVC-U1 explicit source-import closure.

This is deliberately a source and receipt checker.  It never invokes Lean,
Lake, git network operations, or a compiler.  ``--write`` refreshes only its
own proposal; ``--check`` rewrites nothing and rejects a stale proposal.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[4]
OUT = pathlib.Path(__file__).with_name("source-closure.json")
INV = ROOT / "results/research/conditional-validation-contracts/cvc-2/runtime-inventory.json"
CONTRACT = ROOT / "research/conditional-validation-contracts/cvc2/Contract.lean"
DONOR = ROOT / "external/lean-kernel-arena/_build/checkers/lean4lean/src"
BATTERIES = DONOR / ".lake/packages/batteries"
LEAN = pathlib.Path("/Users/danphifer/.elan/toolchains/leanprover--lean4---v4.33.0-rc2")
ROOT_MODULE = "Lean4Lean.Verify.Level"
SUPPORT = {
    "lake_output_arguments": (LEAN / "src/lean/lake/Lake/Build/Actions.lean", 37, 43),
    "olean_search_path": (LEAN / "src/lean/Lean/Util/Path.lean", 6, 10),
    "lean_path_environment": (LEAN / "src/lean/Lean/Util/Path.lean", 98, 110),
    "header_import_serialization": (LEAN / "src/lean/Lean/Elab/Import.lean", 29, 35),
    "cwd_module_name": (LEAN / "src/lean/Lean/Util/Path.lean", 146, 158),
    "module_companion_serialization": (LEAN / "src/lean/Lean/Environment.lean", 1901, 1917),
}


def digest(path: pathlib.Path) -> dict:
    raw = path.read_bytes()
    return {"path": str(path), "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def excerpt(path: pathlib.Path, start: int, end: int) -> dict:
    lines = path.read_text().splitlines()
    return {**digest(path), "start_line": start, "end_line": end,
            "text": "\n".join(lines[start - 1:end]) + "\n"}


def header_tokens(text: str) -> list[str]:
    """Lex just enough of Lean's header to avoid regex-only import parsing.

    Nested block comments and line comments are removed, then the header is
    tokenized.  The walk accepts ``module``/``prelude``, public/meta imports,
    ``import all``, and repeated imports.  An ordinary implicit ``Init`` is
    added separately unless ``prelude`` occurs.  It intentionally does not
    claim elaboration-equivalence to Lean's parser.
    """
    out, i, depth = [], 0, 0
    while i < len(text):
        if text.startswith("/-", i): depth, i = depth + 1, i + 2; continue
        if depth and text.startswith("-/", i): depth, i = depth - 1, i + 2; continue
        if depth: i += 1; continue
        if text.startswith("--", i):
            i = text.find("\n", i)
            if i < 0: break
            continue
        c = text[i]
        if c.isalnum() or c in "_.'":
            j = i + 1
            while j < len(text) and (text[j].isalnum() or text[j] in "_.!'?"): j += 1
            out.append(text[i:j]); i = j; continue
        if c in "\"`":  # headers cannot need string contents; skip safely
            quote, i = c, i + 1
            while i < len(text) and text[i] != quote: i += 2 if text[i] == "\\" else 1
            i += 1; continue
        i += 1
    return out


def imports(path: pathlib.Path) -> tuple[list[dict], bool]:
    tokens = header_tokens(path.read_text())
    result, is_module, prelude, i = [], False, False, 0
    while i < len(tokens):
        tok = tokens[i]
        if tok == "module": is_module = True; i += 1; continue
        if tok == "prelude": prelude = True; i += 1; continue
        public = meta = all_ = False
        while i < len(tokens) and tokens[i] in {"public", "private", "meta"}:
            public |= tokens[i] == "public"; meta |= tokens[i] == "meta"; i += 1
        if i >= len(tokens) or tokens[i] != "import":
            break
        i += 1
        if i < len(tokens) and tokens[i] == "all": all_ = True; i += 1
        if i >= len(tokens) or "." not in tokens[i] and tokens[i] not in {"Init", "Lean", "Std"}:
            raise ValueError(f"unparseable import header in {path}")
        result.append({"module": tokens[i], "public": public, "meta": meta, "import_all": all_})
        i += 1
    if not prelude:
        result = [{"module": "Init", "public": False, "meta": False, "import_all": False,
                   "implicit": True},
                  {"module": "Init", "public": False, "meta": True, "import_all": False,
                   "implicit": True}] + result
    return result, is_module


def source_for(module: str) -> tuple[pathlib.Path | None, str]:
    if module.startswith("Lean4Lean."):
        return DONOR / (module.replace(".", "/") + ".lean"), "lean4lean"
    if module.startswith("Batteries."):
        return BATTERIES / (module.replace(".", "/") + ".lean"), "batteries"
    return None, "core_runtime"


def closure() -> dict:
    inv = json.loads(INV.read_text())
    selected = {x["module"]: x for x in inv["lean4lean_donor"]["selected_source_closure"]}
    modules, pending = {}, [ROOT_MODULE]
    while pending:
        module = pending.pop()
        if module in modules: continue
        path, kind = source_for(module)
        if path is None:
            modules[module] = {"module": module, "kind": kind, "imports": [], "boundary": "installed_lean_runtime"}
            continue
        if not path.is_file(): raise ValueError(f"missing source for {module}: {path}")
        imps, module_header = imports(path)
        row = {"module": module, "kind": kind, "source": digest(path), "git_blob_sha1": git_blob(path.read_bytes()),
               "module_header": module_header, "imports": imps}
        if module in selected:
            pin = selected[module]["pinned_git_blob"]
            row["target_pin"] = {"revision": pin["revision"], "expected_blob_sha1": pin["expected_blob_sha1"],
                                 "matches": row["git_blob_sha1"] == pin["expected_blob_sha1"]}
        if kind == "batteries":
            rel = path.relative_to(BATTERIES).as_posix()
            tree_blob = subprocess.run(["git", "-C", str(BATTERIES), "rev-parse", f"HEAD:{rel}"],
                check=True, text=True, capture_output=True).stdout.strip()
            if tree_blob != row["git_blob_sha1"]:
                raise ValueError(f"Batteries tree blob mismatch for {module}")
            row["batteries_tree_blob_sha1"] = tree_blob
        modules[module] = row
        pending.extend(x["module"] for x in imps)
    noncore = {m for m, row in modules.items() if row["kind"] != "core_runtime"}
    deps = {m: [x["module"] for x in modules[m]["imports"] if x["module"] in noncore] for m in noncore}
    ordered, done = [], set()
    while len(done) < len(noncore):
        ready = sorted(m for m in noncore - done if all(d in done for d in deps[m]))
        if not ready: raise ValueError("cycle in explicit non-core imports")
        ordered.extend(ready); done.update(ready)
    batteries_head = subprocess.run(["git", "-C", str(BATTERIES), "rev-parse", "HEAD"],
                                    check=True, text=True, capture_output=True).stdout.strip()
    batteries_dirty = subprocess.run(["git", "-C", str(BATTERIES), "status", "--porcelain"],
                                     check=True, text=True, capture_output=True).stdout
    if batteries_head != "76e1c118b0700b4ceafe99532e887d6431625e1a" or batteries_dirty:
        raise ValueError("Batteries source receipt is not the pinned clean checkout")
    donor_head = subprocess.run(["git", "-C", str(DONOR), "rev-parse", "HEAD"],
        check=True, text=True, capture_output=True).stdout.strip()
    donor_dirty = subprocess.run(["git", "-C", str(DONOR), "status", "--porcelain"],
        check=True, text=True, capture_output=True).stdout
    lean_rows = [row for row in modules.values() if row["kind"] == "lean4lean"]
    if any("target_pin" not in row or not row["target_pin"]["matches"] for row in lean_rows):
        raise ValueError("each Lean4Lean closure module must have a matching target-tree blob pin")
    return {"modules": [modules[m] for m in ordered] + [modules[m] for m in sorted(modules) if m not in noncore],
            "topological_noncore_order": ordered,
            "noncore_module_count": len(ordered),
            "batteries_source_receipt": {"head": batteries_head, "clean": not batteries_dirty},
            "donor_source_receipt": {"head": donor_head, "clean": not donor_dirty},
            "core_runtime_boundary": sorted(m for m, row in modules.items() if row["kind"] == "core_runtime"),
            "target_pin_matches": all(row.get("target_pin", {}).get("matches", True) for row in modules.values())}


def document() -> dict:
    graph = closure()
    return {
      "schema_version": 1, "item_id": "ALT-PAYLOADS", "status": "STATIC_PROPOSAL_UNCHECKED",
      "scope": "Explicit import closure and offline receipt correspondence only; no Lean/Lake execution, compilation, proof attempt, checker, download, or install occurred.",
      "inputs": {"runtime_inventory": digest(INV), "contract": digest(CONTRACT),
        "lean4lean_target": {"repository": "https://github.com/digama0/lean4lean", "revision": "8223d223ed98661882e95d9d6a7126df7097cd76"},
        "batteries": {"revision": "76e1c118b0700b4ceafe99532e887d6431625e1a", "tag": "v4.33.0-rc2"},
        "donor": {"path": str(DONOR)},
        "runtime": {"path": str(LEAN), "version": "4.33.0-rc2"}},
      "closure": graph,
      "successor_materialization": {"proposal_path": "results/research/conditional-validation-contracts/alt-payloads/proposal.json", "closure_input": "Use closure.topological_noncore_order and all 37 source entries; do not adopt mixed donor outputs.", "command_authority": "The successor proposal owns its isolated merged-tree cwd and direct compiler command; this diagnostic intentionally contains no executable command template."},
      "runtime_source_support": {name: excerpt(*args) for name, args in SUPPORT.items()},
      "limitations": ["This is an explicit source-import closure, not a proof of elaboration/build closure.", "The source parser models module/public/meta/import all and implicit Init, but does not call Lean's parser.", "The installed sources show Lake passing -o/-i and Lean resolving imports through LEAN_PATH; direct compilation and companion-output behavior remain unexecuted hypotheses.", "Core imports stop at the installed Lean runtime boundary; their internal closure is not materialized here.", "A target source tree is not present: target correspondence is limited to retained target-tree blob receipts and the exact Batteries checkout.", "The four Batteries modules absent from the predecessor's selected 21 are reached by explicit public meta imports: CodeAction.Deprecated via Tactic.Alias, Lean.Position via CodeAction.Misc, Lean.Syntax via Util.ProofWanted, and Tactic.Lint.Basic via Tactic.Lint.Misc."],
      "verification": {"command": "python3 results/research/conditional-validation-contracts/alt-payloads/inspect-source-closure.py --check", "offline": True, "writes_on_check": False}}


def main() -> int:
    p = argparse.ArgumentParser(); p.add_argument("--check", action="store_true"); p.add_argument("--write", action="store_true")
    args = p.parse_args()
    if args.check == args.write: p.error("choose exactly one of --check or --write")
    current = document()
    rendered = json.dumps(current, indent=2, sort_keys=True) + "\n"
    if args.write:
        OUT.write_text(rendered); return 0
    if not OUT.is_file() or OUT.read_text() != rendered:
        print("source closure evidence is missing or stale", file=sys.stderr); return 1
    return 0

if __name__ == "__main__": raise SystemExit(main())
