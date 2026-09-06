"""Integrity checks for the unexecuted CVC-2 specification proposal.

This validates bounded records and syntax correspondence. It never invokes
Lean, a checker, an artifact, or the proposed future command. It is not a proof
of the signature, parser, comparator, or model-relative example expectations.
"""

import hashlib
import json
import math
import re
import subprocess
from datetime import datetime
from pathlib import Path

from .cvc2_artifact import decode_sort_definition


CVC_DIR = Path("results/research/conditional-validation-contracts/cvc-2")
CVC1_DIR = Path("results/research/conditional-validation-contracts/cvc-1")
SIGNATURE = "research/conditional-validation-contracts/cvc2/Contract.lean"
FINAL_FILES = {str(CVC_DIR / name) for name in (
    "work-record.json", "contract.json", "examples.json", "assumptions.json",
    "execution-protocol.json", "runtime-inventory.json", "report.md",
)} | {SIGNATURE, "lib/cvc2_artifact.py", "lib/cvc2_contract.py",
     "scripts/validate-cvc2-contract", "tests/test_cvc2_artifact.py",
     "tests/test_cvc2_contract.py"}
REQUIRED_INPUTS = {"CONSTITUTION.md", "docs/RESEARCH_STATUS.md",
                   "docs/research/CONDITIONAL_VALIDATION_CONTRACTS_PLAN.md",
                   "docs/RESEARCH_WORKFLOW.md", "config/research-queue.json",
                   str(CVC1_DIR / "assessment.json"), str(CVC1_DIR / "source-excerpts.json"),
                   "results/research/queue-reviews/2026-09-06-cvc-1.json",
                   "corpus/generated/universe-imax-right-succ.ndjson"}
REVISION = "8223d223ed98661882e95d9d6a7126df7097cd76"
TOOLCHAIN = "leanprover/lean4:v4.33.0-rc2"
BATTERIES = "76e1c118b0700b4ceafe99532e887d6431625e1a"
LIMITS = {"max_sessions": 2, "session_minutes": 90, "proof_builds": 0,
          "checker_launches": 0, "toolchain_installs": 0}
PROTOCOL_LIMITS = {"max_sessions": 4, "session_minutes": 90,
                   "max_active_seconds": 21600, "proof_build_attempts": 12,
                   "attempt_timeout_seconds": 300, "checker_launches": 0,
                   "toolchain_installs": 0, "network_requests_during_attempts": 0,
                   "candidate_families": 1}
TARGETS = [{"name": "Lab.CVC2." + name, "type": "Lab.CVC2." + target}
           for name, target in [("encoding_preserves", "EncodingTarget"),
                                ("preservation", "PreservationTarget"),
                                ("required_acceptance", "AcceptanceTarget"),
                                ("boundary", "BoundaryTarget")]]
STANDARD_AXIOMS = ["propext", "Classical.choice", "Quot.sound"]
HELPER_AXIOMS = ["Std.TreeMap.all_eq_all_toList", "Std.TreeMap.any_eq_any_toList",
                 "Lean.Level.normalize_eq"]
REQUIRED_ACCEPTANCE = ["E-POS", "E-CONTROL"]
SOURCE_GROUPS = [("meaning, Owned, Contract", ["E1", "E2"]),
                 ("encode, names, EncodingTarget", ["E3"]),
                 ("Accepts, PreservationTarget, AcceptanceTarget", ["E5", "E6", "E16"]),
                 ("conditional axiom ledger", ["E8", "E9"])]


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _exact(actual, expected, label):
    _require(json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True),
             f"{label}: changed fixed value")


def _object(pairs):
    result = {}
    for key, value in pairs:
        _require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _constant(value):
    raise ValueError(f"nonfinite JSON number: {value}")


def _json(raw):
    result = json.loads(raw, object_pairs_hook=_object, parse_constant=_constant)
    _require(isinstance(result, dict), "expected a JSON object")
    return result


def _path(root, value):
    _require(isinstance(value, str) and bool(value), "missing repository-relative path")
    path = Path(value)
    _require(not path.is_absolute() and ".." not in path.parts, f"unsafe path: {value}")
    resolved = (root / path).resolve()
    _require(root in resolved.parents, f"path escapes repository: {value}")
    return resolved


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _binding(root, binding):
    _require(isinstance(binding, dict) and set(binding) == {"path", "sha256"},
             "malformed content binding")
    path = _path(root, binding["path"])
    _require(isinstance(binding["sha256"], str) and
             re.fullmatch(r"[0-9a-f]{64}", binding["sha256"]), "malformed content hash")
    return path


def _git_blob(root, commit, path):
    _path(root, path)
    result = subprocess.run(["git", "-C", str(root), "show", f"{commit}:{path}"],
                            capture_output=True, check=False, timeout=30)
    _require(result.returncode == 0, f"historical input unavailable: {path}")
    return result.stdout


def _time(value):
    _require(isinstance(value, str), "missing timestamp")
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    _require(result.tzinfo is not None, "timestamp requires timezone")
    return result


def _number(value):
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def _ledger(root, record):
    _exact(record["schema_version"], 1, "work record schema")
    _exact(record["item_id"], "CVC-2", "work record item")
    _exact(record["status"], "COMPLETE", "work record status")
    _exact(record["limits"], LIMITS, "CVC-2 limits")
    commit = record["predecessor_commit"]
    _require(isinstance(commit, str) and re.fullmatch(r"[0-9a-f]{40}", commit),
             "invalid predecessor commit")
    inputs = record["inputs"]
    _require(isinstance(inputs, list), "inputs must be a list")
    historical = {}
    for binding in inputs:
        _binding(root, binding)
        path = binding["path"]
        _require(path not in historical, "duplicate historical input")
        raw = _git_blob(root, commit, path)
        _require(_sha(raw) == binding["sha256"], f"historical input hash mismatch: {path}")
        historical[path] = raw
    _require(REQUIRED_INPUTS <= set(historical), "required historical inputs missing")
    for path in [str(CVC1_DIR / "assessment.json"), str(CVC1_DIR / "source-excerpts.json")]:
        _require(_path(root, path).read_bytes() == historical[path],
                 f"CVC-1 predecessor content changed: {path}")
    sessions = record["sessions"]
    _require(isinstance(sessions, list) and 1 <= len(sessions) <= 2, "session count out of bounds")
    total = 0.0
    previous_end = None
    for index, session in enumerate(sessions, 1):
        _exact(session["id"], index, "session sequence")
        start, end = _time(session["started_at"]), _time(session["ended_at"])
        minutes = (end - start).total_seconds() / 60
        active = session["active_minutes"]
        _require(_number(active) and 0 <= minutes <= 90 and abs(active - minutes) <= 1e-9,
                 "session active minutes must equal timestamp interval within 90-minute bound")
        _require(previous_end is None or start >= previous_end, "overlapping sessions")
        previous_end = end
        total += active
    _require(_time(record["started_at"]) == _time(sessions[0]["started_at"]),
             "work record start differs from first session")
    consumed = record["consumed"]
    _require(set(consumed) == {"sessions", "active_minutes", "proof_builds",
                               "checker_launches", "toolchain_installs"}, "invalid consumed counters")
    _exact(consumed["sessions"], len(sessions), "consumed sessions")
    _require(_number(consumed["active_minutes"]) and
             abs(consumed["active_minutes"] - total) <= 1e-9, "consumed active time mismatch")
    for key in ("proof_builds", "checker_launches", "toolchain_installs"):
        _exact(consumed[key], 0, f"CVC-2 {key}")
    return historical


def _ast_examples():
    u, v = ["param", "u"], ["param", "v"]
    max_level = ["max", u, ["succ", v]]
    return {
        "E-POS": ("rightSucc", "REQUIRED_ACCEPT", {
            "name": "universeIMaxRightSucc", "params": ["u", "v"],
            "value_level": ["imax", u, ["succ", v]], "type_level": ["succ", max_level]}),
        "E-CONTROL": ("rightSuccControl", "REQUIRED_ACCEPT", {
            "name": "universeIMaxRightSuccControl", "params": ["u", "v"],
            "value_level": max_level, "type_level": ["succ", max_level]}),
        "E-ZERO": ("zeroBoundary", "MODEL_INVALID", {
            "name": "cvc2ZeroBoundary", "params": ["u"],
            "value_level": ["imax", u, ["zero"]], "type_level": ["succ", u]}),
        "E-UNOWNED": ("unownedBoundary", "UNSUPPORTED", {
            "name": "cvc2UnownedBoundary", "params": ["v"],
            "value_level": u, "type_level": ["succ", u]}),
    }


def _lean_level(node):
    tag = node[0]
    if tag == "zero":
        return ".zero"
    if tag == "param":
        return ".param " + json.dumps(node[1], ensure_ascii=False)
    return "." + tag + " " + " ".join(
        ".zero" if child[0] == "zero" else "(" + _lean_level(child) + ")"
        for child in node[1:])


def _normalize(source):
    return " ".join(re.findall(r'"(?:\\.|[^"\\])*"|[^\s]+', source))


def _lean_definitions(source):
    # The fixed proposal contains no nested comments or comment delimiters in strings.
    source = re.sub(r"/\-.*?\-/", "", source, flags=re.S)
    source = re.sub(r"--[^\n]*", "", source)
    definitions = {}
    for match in re.finditer(r"^def (\w+)\b(.*?)(?=^def |^structure |^inductive |^end |\Z)", source, re.M | re.S):
        _require(match[1] not in definitions, "duplicate Lean definition")
        definitions[match[1]] = _normalize("def " + match[1] + match[2])
    return definitions


def _examples(root, data, definitions):
    _exact(data["required_acceptance_ids"], REQUIRED_ACCEPTANCE, "example acceptance set")
    _exact(data["boundary_ids"], ["E-ZERO", "E-UNOWNED"], "example boundary set")
    rows = data["examples"]
    expected = _ast_examples()
    _require(isinstance(rows, list) and len(rows) == 4 and
             {row["id"] for row in rows} == set(expected), "exactly four fixed examples required")
    for row in rows:
        name, outcome, artifact = expected[row["id"]]
        _exact(row["signature_definition"], name, "example signature definition")
        _exact(row["expected"], outcome, "example expected label")
        _exact(row["expectation_status"], "SPECIFICATION_NOT_CHECKER_OBSERVATION", "example status")
        _exact(row["artifact"], artifact, "fixed example AST")
        body = "⟨" + ", ".join([json.dumps(artifact["name"]), json.dumps(artifact["params"]),
                                  _lean_level(artifact["value_level"]),
                                  _lean_level(artifact["type_level"])]) + "⟩"
        rendered = f"def {name} : SortDefinition := {body}"
        _require(definitions.get(name) == _normalize(rendered), f"Lean example body mismatch: {name}")
        if row["id"] in REQUIRED_ACCEPTANCE:
            binding = row["input_binding"]
            path = _binding(root, binding)
            expected_path = "corpus/generated/universe-imax-right-succ" + (
                "-control" if row["id"] == "E-CONTROL" else "") + ".ndjson"
            _exact(binding["path"], expected_path, "example input path")
            raw = path.read_bytes()
            _require(_sha(raw) == binding["sha256"], "example input hash mismatch")
            _exact(decode_sort_definition(raw), artifact, "decoded supplied artifact AST")
        else:
            _require("input_binding" not in row, "model boundary may not claim executed input")
    zero = next(row for row in rows if row["id"] == "E-ZERO")
    _exact(zero["counterexample_assignment"], {"u": 1}, "zero boundary assignment")
    _exact(zero["expected_value_type_level"], 1, "zero boundary value type level")
    _exact(zero["expected_declared_type_level"], 2, "zero boundary declared level")


def _source_mappings(root, contract, historical, commit):
    excerpts = _json(historical[str(CVC1_DIR / "source-excerpts.json")])["excerpts"]
    by_id = {row["id"]: row for row in excerpts}
    prior_record = _json(_git_blob(root, commit, str(CVC1_DIR / "work-record.json")))
    inspections = {row["id"]: row for row in prior_record["code_inspections"]}
    mappings = contract["source_mappings"]
    _require(isinstance(mappings, list) and len(mappings) == len(SOURCE_GROUPS), "source mapping count changed")
    for mapping, (target, ids) in zip(mappings, SOURCE_GROUPS):
        _exact(mapping["target"], target, "source mapping target")
        _exact(mapping["revision"], REVISION, "source revision")
        _exact([row["id"] for row in mapping["excerpts"]], ids, "source mapping excerpt IDs")
        for reference in mapping["excerpts"]:
            row = by_id[reference["id"]]
            _require(_sha(row["text"].encode()) == row["sha256"], "predecessor excerpt hash mismatch")
            _exact(inspections[row["inspection_id"]]["revision"], REVISION, "predecessor source pin")
            _exact(reference, {key: row[key] for key in
                              ("id", "path", "source_sha256", "start_line", "end_line")} |
                   {"excerpt_sha256": row["sha256"]}, "source excerpt correspondence")
            _path(root, reference["path"])


def _contract(root, contract, definitions):
    _exact(contract["model_id"], "CVC-U1", "model identity")
    _exact(contract["scientific_status"], "SPECIFICATION_PROPOSAL_UNCHECKED", "scientific claim")
    _exact(contract["outcome"], "SUCCESS", "bounded specification outcome")
    _exact(contract["byte_interpretation"]["required_acceptance_ids"], REQUIRED_ACCEPTANCE, "byte acceptance set")
    _exact(contract["byte_interpretation"]["decoder"], "lib/cvc2_artifact.py", "decoder binding")
    _exact(contract["acceptance_obligation"]["ids"], REQUIRED_ACCEPTANCE, "contract acceptance set")
    _require(contract["acceptance_obligation"]["broader_completeness"].startswith("NOT_PROMISED;"),
             "broader completeness claim is not authorized")
    _exact(contract["assumptions_ledger"], "assumptions.json", "assumptions ledger")
    _exact(contract["execution_protocol"], "execution-protocol.json", "execution protocol")
    strategies = contract["strategies"]
    _require(isinstance(strategies, list) and len(strategies) == 1, "exactly one strategy required")
    _exact(strategies[0]["id"], "S1", "strategy ID")
    _exact(strategies[0]["definition"], "Lab.CVC2.Accepts", "strategy definition")
    for key in ("input_constants", "input_axioms", "local_context"):
        _exact(contract["environment"][key], [], "input environment " + key)
    for key, value in {"name": "PreservationTarget", "intermediate_target": "EncodingTarget",
                       "acceptance_target": "AcceptanceTarget", "boundary_target": "BoundaryTarget"}.items():
        _exact(contract["proof_target"][key], "Lab.CVC2." + value, "proof target " + key)
    required_definitions = {
        "meaning": "def meaning (ρ : String → Nat) : U → Nat | .zero => 0 | .succ u => meaning ρ u + 1 | .max u v => Nat.max (meaning ρ u) (meaning ρ v) | .imax u v => if meaning ρ v = 0 then 0 else Nat.max (meaning ρ u) (meaning ρ v) | .param n => ρ n",
        "Owned": "def Owned (params : List String) : U → Prop | .zero => True | .succ u => Owned params u | .max u v | .imax u v => Owned params u ∧ Owned params v | .param n => n ∈ params",
        "encode": "def encode : U → Lean.Level | .zero => .zero | .succ u => .succ (encode u) | .max u v => .max (encode u) (encode v) | .imax u v => .imax (encode u) (encode v) | .param n => .param (.str .anonymous n)",
        "names": "def names (params : List String) : List Lean.Name := params.map (fun n => .str .anonymous n)",
        "Supported": "def Supported (a : SortDefinition) : Prop := a.params.Nodup ∧ Owned a.params a.valueLevel ∧ Owned a.params a.typeLevel",
        "Contract": "def Contract (a : SortDefinition) : Prop := Supported a ∧ ∀ ρ, meaning ρ a.valueLevel + 1 = meaning ρ a.typeLevel",
        "Accepts": "def Accepts (a : SortDefinition) : Prop := Supported a ∧ Lean.Level.isEquiv' (.succ (encode a.valueLevel)) (encode a.typeLevel) = true",
        "EncodingTarget": "def EncodingTarget : Prop := ∀ (params : List String) (u : U), params.Nodup → Owned params u → ∃ v, Lean4Lean.VLevel.ofLevel (names params) (encode u) = some v ∧ v.WF params.length ∧ ∀ ρ, v.eval (params.map ρ) = meaning ρ u",
        "PreservationTarget": "def PreservationTarget : Prop := ∀ a, Accepts a → Contract a",
        "AcceptanceTarget": "def AcceptanceTarget : Prop := Accepts rightSucc ∧ Accepts rightSuccControl",
        "BoundaryTarget": "def BoundaryTarget : Prop := Supported zeroBoundary ∧ ¬ Contract zeroBoundary ∧ ¬ Accepts zeroBoundary ∧ ¬ Supported unownedBoundary ∧ ¬ Accepts unownedBoundary",
    }
    for name, expected in required_definitions.items():
        _require(definitions.get(name) == _normalize(expected), f"signature target changed: {name}")
    _require(set(definitions) == set(required_definitions) |
             {row[0] for row in _ast_examples().values()}, "signature definition inventory changed")


def _assumptions(data):
    _exact(data["status"], "REVIEWED_FOR_TARGET_NOT_TRANSITIVELY_AUDITED", "assumption review status")
    runtime = data["proof_runtime"]
    for key, value in {"lean4lean_revision": REVISION, "lean_toolchain": TOOLCHAIN,
                       "batteries_revision": BATTERIES, "runtime_inventory": "runtime-inventory.json",
                       "status": "COMPILED_DEPENDENCY_BUNDLE_NOT_AVAILABLE"}.items():
        _exact(runtime[key], value, "proof runtime " + key)
    policy = data["conditional_axiom_policy"]
    _exact(policy["standard_allowed"], STANDARD_AXIOMS, "standard axiom allowlist")
    _exact(policy["source_helpers_allowed"], HELPER_AXIOMS, "source helper axiom allowlist")
    _exact(policy["source_helper_bindings"], ["E8", "E9"], "source helper bindings")
    _require(policy["closure_status"].startswith("NOT_PRINTED;"), "axiom closure cannot be claimed audited")
    _require("sorryAx" in policy["forbidden"] and "New axioms in Lab proof files" in policy["forbidden"],
             "required forbidden axiom policy missing")


def _protocol(root, protocol, signature):
    _exact(protocol["item_id"], "CVC-3", "protocol successor")
    _exact(protocol["protocol_id"], "CVC3-U1-PROOF-0001", "protocol ID")
    _exact(protocol["status"], "SPECIFIED_NOT_EXECUTABLE", "protocol status")
    _exact(protocol["contract_id"], "CVC-U1", "protocol contract")
    _exact(protocol["signature"], signature, "protocol signature binding")
    _exact(protocol["limits"], PROTOCOL_LIMITS, "successor protocol limits")
    _exact(protocol["current_execution"], {"proof_attempts": 0, "checker_launches": 0,
                                           "runner_implemented": False}, "current execution")
    _exact(protocol["required_result_declarations"], TARGETS, "required result declarations")
    for key, value in {"run_directory": "results/research/conditional-validation-contracts/cvc-3/run-0001",
                       "workspace": "external/cvc3-u1-proof-0001"}.items():
        _path(root, protocol[key])
        _exact(protocol[key], value, "protocol " + key)
    command = protocol["attempt_command"]
    _exact(command["argv"], ["{bound_lean_binary}", "-o", "{attempt_directory}/CVC2Proof.olean", "CVC2Proof.lean"],
           "specified attempt command")
    _exact(command["cwd"], protocol["workspace"], "specified command cwd")
    _exact(command["input_file"], "CVC2Proof.lean", "specified input")
    first = protocol["signature_attempt"]
    _exact(first["attempt_number"], 1, "counted first signature attempt")
    _exact(first["argv"], ["{bound_lean_binary}", "-o", "{workspace}/Contract.olean", "Contract.lean"],
           "signature attempt command")
    _exact(first["cwd"], protocol["workspace"], "signature attempt cwd")
    _exact(first["source_binding"], signature, "signature attempt source")
    preparation = protocol["preparation_accounting"]
    for key, value in {"compiled_input_scope": "UPSTREAM_DEPENDENCIES_ONLY",
                       "lab_elaboration_permitted": False,
                       "budget_source": "SEPARATELY_AUTHORIZED_ITEM",
                       "cvc3_attempts_charged": 0,
                       "aggregate_cost_reporting_required": True}.items():
        _exact(preparation[key], value, "preparation accounting " + key)


def _manifest(root, manifest):
    _exact(manifest["schema_version"], 1, "manifest schema")
    _exact(manifest["item_id"], "CVC-2", "manifest item")
    rows = manifest["files"]
    _require(isinstance(rows, list), "manifest files must be a list")
    seen = set()
    for binding in rows:
        path = _binding(root, binding)
        name = binding["path"]
        _require(name in FINAL_FILES and name not in seen, "unexpected or duplicate manifest file")
        _require(_sha(path.read_bytes()) == binding["sha256"], f"manifest content mismatch: {name}")
        seen.add(name)
    _require(seen == FINAL_FILES, "manifest must bind every required CVC-2 file")


def _runtime(runtime):
    # Absolute inventory paths are historical labels, never opened or executed.
    _exact(runtime["entry_gate_satisfied"], False, "runtime entry gate")
    _exact(runtime["scientific_status"], "FILESYSTEM_SOURCE_INVENTORY_ONLY", "runtime scientific status")
    for key in ("proof_builds", "checker_launches"):
        _exact(runtime[key], 0, "runtime inventory " + key)
    _exact(runtime["other_execution_counts"], {"lean_executions": 0, "lake_executions": 0,
                                               "toolchain_installs": 0, "downloads": 0},
           "runtime inventory execution counts")
    for key, value in {"revision": REVISION, "lean_toolchain": TOOLCHAIN,
                       "batteries_revision": BATTERIES}.items():
        _exact(runtime["selected_revision"][key], value, "runtime selected " + key)


def validate_cvc2_contract(root: Path) -> None:
    """Validate completed CVC-2 integrity without executing its proposed protocol."""
    try:
        root = Path(root).resolve()
        def load(name):
            data = _json(_path(root, str(CVC_DIR / name)).read_bytes())
            _exact(data["schema_version"], 1, name + " schema")
            if name != "execution-protocol.json":
                _exact(data["item_id"], "CVC-2", name + " item")
            return data
        record = load("work-record.json")
        historical = _ledger(root, record)
        contract = load("contract.json")
        signature = contract["signature"]
        signature_path = _binding(root, signature)
        _exact(signature["path"], SIGNATURE, "signature path")
        source = signature_path.read_text(encoding="utf-8")
        _require(_sha(signature_path.read_bytes()) == signature["sha256"], "signature hash mismatch")
        definitions = _lean_definitions(source)
        _contract(root, contract, definitions)
        _examples(root, load("examples.json"), definitions)
        _source_mappings(root, contract, historical, record["predecessor_commit"])
        _assumptions(load("assumptions.json"))
        _protocol(root, load("execution-protocol.json"), signature)
        _runtime(load("runtime-inventory.json"))
        _require(_path(root, str(CVC_DIR / "report.md")).read_text(encoding="utf-8").strip(), "empty report")
        _manifest(root, load("evidence-manifest.json"))
    except ValueError:
        raise
    except (OSError, KeyError, TypeError, IndexError, AttributeError, RecursionError,
            subprocess.SubprocessError) as error:
        raise ValueError(f"invalid or unavailable CVC-2 evidence: {error}") from error
