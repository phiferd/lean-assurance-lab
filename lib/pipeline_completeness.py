"""Checked-object sentinel and bounded runners for the pipeline-completeness pilot."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
from typing import Any

from lib.cvc_prep import bind, committed, require, safe
from lib.cvc_process import atomic, now, sha
from lib.metamorphic_pilot_runner import run_supervised


ROOT = Path(__file__).resolve().parents[1]
ITEM = "PIPELINE-COMPLETENESS-PILOT-1"
BASE = "results/research/pipeline-completeness-pilot-1"
EXPECTED = BASE + "/expected-module.json"
PROTOCOL = BASE + "/protocol.json"
SOURCE = "corpus/pipeline-completeness-pilot-1/PipelineCompletenessSentinel.lean"
PREPARE_RUN = BASE + "/producer-run-0001"
INPUTS = BASE + "/inputs"
INVENTORY = BASE + "/artifact-inventory.json"
MANIFEST = "config/pipeline-completeness-0001.json"
WORK = BASE + "/work-record.json"
RUN = BASE + "/run-0001"
PLAN = "docs/research/PIPELINE_COMPLETENESS_PILOT_PLAN.md"
BUILD_MEMORY = 4_294_967_296
CHECKER_MEMORY = 2_147_483_648


class SentinelError(ValueError):
    pass


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise SentinelError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _nonfinite(value: str) -> None:
    raise SentinelError(f"non-finite JSON number: {value}")


def load_json(path: Path | str) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"),
                      object_pairs_hook=_pairs, parse_constant=_nonfinite)


def file_binding(path: Path) -> dict[str, Any]:
    return {"path": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size,
            "sha256": sha(path)}


def _nat(value: Any, label: str) -> int:
    if type(value) is not int or value < 0:
        raise SentinelError(f"{label} must be a nonnegative integer")
    return value


def _single_tag(row: dict[str, Any], excluded: set[str], label: str) -> str:
    tags = set(row) - excluded
    if len(tags) != 1:
        raise SentinelError(f"{label} must have exactly one tag")
    return next(iter(tags))


@dataclass(frozen=True)
class Theorem:
    line_index: int
    name: str
    type_expression: int
    value_expression: int


@dataclass
class Artifact:
    metadata: dict[str, Any]
    rows: list[dict[str, Any]]
    lines: list[bytes]
    names: dict[int, str]
    expressions: dict[int, tuple[str, Any]]
    theorems: list[Theorem]

    def constants(self, expression: int) -> set[str]:
        visiting: set[int] = set()

        def visit(index: int) -> set[str]:
            index = _nat(index, "expression reference")
            if index in visiting:
                raise SentinelError("cyclic expression reference")
            if index not in self.expressions:
                raise SentinelError(f"unresolved expression reference {index}")
            visiting.add(index)
            tag, value = self.expressions[index]
            if tag == "const":
                if not isinstance(value, dict) or set(value) != {"name", "us"}:
                    raise SentinelError("const payload differs")
                name_id = _nat(value["name"], "const.name")
                if name_id not in self.names:
                    raise SentinelError("const name is unresolved")
                result = {self.names[name_id]}
            elif tag == "app":
                if not isinstance(value, dict) or set(value) != {"fn", "arg"}:
                    raise SentinelError("app payload differs")
                result = visit(value["fn"]) | visit(value["arg"])
            elif tag in {"lam", "forallE"}:
                if not isinstance(value, dict) or not {"type", "body"}.issubset(value):
                    raise SentinelError(f"{tag} payload differs")
                result = visit(value["type"]) | visit(value["body"])
            elif tag == "letE":
                if not isinstance(value, dict) or not {"type", "value", "body"}.issubset(value):
                    raise SentinelError("letE payload differs")
                result = visit(value["type"]) | visit(value["value"]) | visit(value["body"])
            elif tag == "mdata":
                if not isinstance(value, dict) or "expr" not in value:
                    raise SentinelError("mdata payload differs")
                result = visit(value["expr"])
            elif tag == "proj":
                if not isinstance(value, dict) or "struct" not in value:
                    raise SentinelError("proj payload differs")
                result = visit(value["struct"])
            elif tag in {"sort", "bvar", "natVal", "strVal"}:
                result = set()
            else:
                raise SentinelError(f"unsupported expression tag in dependency closure: {tag}")
            visiting.remove(index)
            return result

        return visit(expression)

    def is_true_statement(self, expression: int) -> bool:
        tag, value = self.expressions.get(expression, (None, None))
        if tag != "const" or not isinstance(value, dict) or set(value) != {"name", "us"}:
            return False
        name_id = value["name"]
        return (type(name_id) is int and self.names.get(name_id) == "True"
                and value["us"] == [])


def parse_artifact(data: bytes) -> Artifact:
    if type(data) is not bytes:
        raise SentinelError("artifact input must be bytes")
    if not data.endswith(b"\n"):
        raise SentinelError("artifact must end in LF")
    raw_lines = data.splitlines()
    if not raw_lines:
        raise SentinelError("artifact is empty")
    rows: list[dict[str, Any]] = []
    for line_no, line in enumerate(raw_lines, 1):
        if not line:
            raise SentinelError(f"blank record at line {line_no}")
        try:
            row = json.loads(line, object_pairs_hook=_pairs, parse_constant=_nonfinite)
        except (UnicodeDecodeError, json.JSONDecodeError, SentinelError) as error:
            raise SentinelError(f"invalid record at line {line_no}: {error}") from error
        if not isinstance(row, dict):
            raise SentinelError(f"record {line_no} is not an object")
        rows.append(row)
    if set(rows[0]) != {"meta"} or not isinstance(rows[0]["meta"], dict):
        raise SentinelError("first record must contain only metadata")
    metadata = rows[0]["meta"]
    expected_meta = {"exporter": {"name": "lean4export", "version": "3.1.0"},
                     "format": {"version": "3.1.0"}}
    if metadata.get("exporter") != expected_meta["exporter"] or metadata.get("format") != expected_meta["format"]:
        raise SentinelError("unsupported exporter or format metadata")
    lean = metadata.get("lean")
    if not isinstance(lean, dict) or lean.get("version") != "4.29.1" or not isinstance(lean.get("githash"), str):
        raise SentinelError("unsupported Lean producer metadata")

    names = {0: ""}
    expressions: dict[int, tuple[str, Any]] = {}
    theorems: list[Theorem] = []
    for line_index, row in enumerate(rows[1:], 1):
        if "in" in row:
            if set(row) not in ({"in", "str"}, {"in", "num"}):
                raise SentinelError("name record fields differ")
            index = _nat(row["in"], "name ID")
            if index in names:
                raise SentinelError(f"duplicate name ID {index}")
            tag = "str" if "str" in row else "num"
            payload = row[tag]
            required = {"pre", "str"} if tag == "str" else {"pre", "i"}
            if not isinstance(payload, dict) or set(payload) != required:
                raise SentinelError("name payload differs")
            prefix = _nat(payload["pre"], "name prefix")
            if prefix not in names:
                raise SentinelError("name prefix is unresolved")
            component = payload["str"] if tag == "str" else str(_nat(payload["i"], "name numeral"))
            if not isinstance(component, str) or not component:
                raise SentinelError("name component is empty")
            names[index] = component if not names[prefix] else names[prefix] + "." + component
        elif "ie" in row:
            index = _nat(row["ie"], "expression ID")
            if index in expressions:
                raise SentinelError(f"duplicate expression ID {index}")
            tag = _single_tag(row, {"ie"}, "expression record")
            expressions[index] = (tag, row[tag])
        elif "thm" in row:
            if set(row) != {"thm"} or not isinstance(row["thm"], dict):
                raise SentinelError("theorem record differs")
            value = row["thm"]
            if not {"name", "type", "value"}.issubset(value):
                raise SentinelError("theorem payload omits identity, type or value")
            name_id = _nat(value["name"], "theorem name")
            if name_id not in names:
                raise SentinelError("theorem name is unresolved")
            theorems.append(Theorem(line_index, names[name_id],
                                    _nat(value["type"], "theorem type"),
                                    _nat(value["value"], "theorem value")))
        else:
            # Level records and non-theorem declarations remain parser-visible but
            # are outside this sentinel's intended theorem inventory.
            if not row:
                raise SentinelError("empty record")
    return Artifact(metadata, rows, raw_lines, names, expressions, theorems)


def expected_model() -> dict[str, Any]:
    model = load_json(ROOT / EXPECTED)
    require(model["schema_version"] == 1 and model["item_id"] == ITEM,
            "expected-module identity differs")
    return model


def inventory(data: bytes) -> dict[str, Any]:
    artifact = parse_artifact(data)
    model = expected_model()
    expected_names = [row["name"] for row in model["declarations"]]
    expected_set = set(expected_names)
    selected = [row for row in artifact.theorems if row.name.startswith(model["namespace"] + ".")]
    actual_names = [row.name for row in selected]
    if actual_names != expected_names:
        raise SentinelError(f"intended theorem inventory differs: {actual_names}")
    records = []
    graph: dict[str, list[str]] = {}
    for actual, expected in zip(selected, model["declarations"]):
        if expected["kind"] != "theorem" or expected["statement"] != "True":
            raise SentinelError("unsupported independent expectation")
        if not artifact.is_true_statement(actual.type_expression):
            raise SentinelError(f"statement differs for {actual.name}")
        direct = sorted(artifact.constants(actual.value_expression).intersection(expected_set))
        if direct != expected["direct_value_dependencies"]:
            raise SentinelError(f"direct dependency differs for {actual.name}: {direct}")
        graph[actual.name] = direct
        records.append({"ordinal": expected["ordinal"], "name": actual.name,
                        "kind": "theorem", "statement": "True",
                        "direct_value_dependencies": direct})
    root = model["root_target"]
    closure: set[str] = set()
    stack = [root]
    while stack:
        name = stack.pop()
        if name in closure:
            continue
        if name not in graph:
            raise SentinelError(f"dependency closure is missing {name}")
        closure.add(name)
        stack.extend(graph[name])
    if closure != expected_set:
        raise SentinelError("root dependency closure does not cover all expected declarations")
    return {"metadata": artifact.metadata, "root_target": root,
            "ordered_declarations": records,
            "transitive_value_dependency_closure": [name for name in expected_names if name in closure],
            "record_count": len(artifact.rows)}


def sentinel(data: bytes, baseline_sha256: str) -> dict[str, Any]:
    digest = hashlib.sha256(data).hexdigest()
    try:
        artifact = parse_artifact(data)
    except SentinelError as error:
        return {"classification": "FAIL_PARSE_OR_DEPENDENCY_CLOSURE", "artifact_sha256": digest,
                "reason": str(error)}
    model = expected_model()
    names = [row.name for row in artifact.theorems if row.name.startswith(model["namespace"] + ".")]
    expected_names = [row["name"] for row in model["declarations"]]
    if model["root_target"] not in names:
        classification = "FAIL_MISSING_TARGET" if set(names).intersection(expected_names) else "FAIL_ARTIFACT_OR_DECLARATION_IDENTITY"
        return {"classification": classification, "artifact_sha256": digest,
                "reason": "intended root target is absent"}
    try:
        observed = inventory(data)
    except SentinelError as error:
        return {"classification": "FAIL_PARSE_OR_DEPENDENCY_CLOSURE", "artifact_sha256": digest,
                "reason": str(error)}
    if digest != baseline_sha256:
        return {"classification": "FAIL_ARTIFACT_OR_DECLARATION_IDENTITY", "artifact_sha256": digest,
                "reason": "artifact semantics match but exact baseline identity differs"}
    return {"classification": "PASS", "artifact_sha256": digest,
            "reason": "exact artifact identity and intended theorem closure match", "inventory": observed}


def omission_fault(data: bytes) -> bytes:
    artifact = parse_artifact(data)
    target = expected_model()["root_target"]
    matches = [row for row in artifact.theorems if row.name == target]
    if len(matches) != 1:
        raise SentinelError("baseline does not contain one target theorem")
    lines = list(artifact.lines)
    del lines[matches[0].line_index]
    return b"\n".join(lines) + b"\n"


def truncation_fault(data: bytes) -> bytes:
    artifact = parse_artifact(data)
    last = artifact.lines[-1]
    if len(last) < 4:
        raise SentinelError("final record is too short to truncate")
    return b"\n".join(artifact.lines[:-1]) + b"\n" + last[:len(last) // 2]


def expected_matrix() -> list[tuple[str, str, str]]:
    artifacts = [("baseline", "PASS"), ("omission", "FAIL_MISSING_TARGET"),
                 ("substitution", "FAIL_ARTIFACT_OR_DECLARATION_IDENTITY"),
                 ("truncation", "FAIL_PARSE_OR_DEPENDENCY_CLOSURE")]
    return [(artifact, adapter, expected) for artifact, expected in artifacts
            for adapter in ("official", "lean4lean")]


def process_classification(receipt: dict[str, Any]) -> str:
    if (receipt["memory_monitor_error"] is not None or receipt["memory_monitor_samples"] <= 0
            or receipt["maximum_observed_rss_bytes"] <= 0 or receipt["memory_exceeded"]
            or receipt["timed_out"] or not receipt["cleanup_complete"]):
        return "INFRASTRUCTURE_FAILURE"
    code = receipt["exit_code"]
    if code == 0:
        return "ACCEPT"
    if isinstance(code, int) and code > 0:
        return "REJECT"
    if isinstance(code, int) and code < 0:
        return "CRASH"
    return "UNKNOWN"


def _supervise(directory: Path, argv: list[str], cwd: Path, env: dict[str, str],
               seconds: int, memory: int) -> tuple[dict[str, Any], bytes, bytes]:
    directory.mkdir(parents=True, exist_ok=False)
    receipt = run_supervised(argv=argv, cwd=cwd, stdin=None, env=env,
                             timeout_seconds=seconds, memory_bytes=memory,
                             raw_prefix=directory / "process")
    receipt["recorded_at"] = now()
    atomic(directory / "supervisor.json", receipt)
    return receipt, (directory / "process.stdout").read_bytes(), (directory / "process.stderr").read_bytes()


def prepare() -> dict[str, Any]:
    from lib.research_queue_v3 import load_queue
    protocol = load_json(ROOT / PROTOCOL)
    require(protocol["status"] == "READY" and protocol["item_id"] == ITEM,
            "protocol is not READY")
    queue = load_queue(ROOT, require_ready=True)
    item = next(row for row in queue["items"] if row["id"] == ITEM)
    require(queue["selected_item"] == ITEM and item["status"] == "READY",
            "item is not selected READY")
    for path in (PLAN, PROTOCOL, EXPECTED, SOURCE, "lib/pipeline_completeness.py",
                 "scripts/prepare-pipeline-completeness", "scripts/execute-pipeline-completeness",
                 "tests/test_pipeline_completeness.py", "tests/test_pipeline_completeness_protocol.py"):
        committed(ROOT, path)
    arena = ROOT / protocol["arena"]["path"]
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=arena, text=True).strip()
    dirty = subprocess.check_output(["git", "status", "--porcelain"], cwd=arena, text=True)
    require(revision == protocol["arena"]["revision"] and not dirty, "Arena checkout differs")
    producer = ROOT / protocol["producer"]["path"]
    require(producer.is_file() and sha(producer) == protocol["producer"]["sha256"],
            "producer binary differs")

    run_dir = safe(ROOT, PREPARE_RUN, exists=False)
    input_dir = safe(ROOT, INPUTS, exists=False)
    workspace = ROOT / "external/pipeline-completeness-producer-0001"
    require(not run_dir.exists() and not input_dir.exists() and not workspace.exists(),
            "producer materialization already exists")
    run_dir.mkdir(parents=True)
    input_dir.mkdir(parents=True)
    workspace.mkdir(parents=True)
    shutil.copyfile(ROOT / SOURCE, workspace / "PipelineCompletenessSentinel.lean")
    (workspace / "lean-toolchain").write_text("leanprover/lean4:v4.29.1\n", encoding="utf-8")
    (workspace / "lakefile.toml").write_text(
        'name = "pipeline-completeness-pilot"\ndefaultTargets = ["PipelineCompletenessSentinel"]\n\n'
        '[[lean_lib]]\nname = "PipelineCompletenessSentinel"\n', encoding="utf-8")
    (workspace / "lake-manifest.json").write_text(
        '{"version":"1.1.0","packagesDir":".lake/packages","packages":[],"name":"pipeline-completeness-pilot","lakeDir":".lake"}\n',
        encoding="utf-8")
    temporary = run_dir / "baseline.ndjson.tmp"
    command = ('set -eu\nlake build PipelineCompletenessSentinel\n'
               'lake env "$PIPELINE_EXPORTER" PipelineCompletenessSentinel -- PipelineCompleteness.d12 > "$PIPELINE_OUTPUT"')
    env = dict(os.environ)
    env.update({"LANG": "C", "PIPELINE_EXPORTER": str(producer),
                "PIPELINE_OUTPUT": str(temporary)})
    receipt, stdout, _ = _supervise(run_dir / "process", ["/bin/sh", "-c", command],
                                    workspace, env, 600, BUILD_MEMORY)
    require(process_classification(receipt) == "ACCEPT" and stdout == b"" and temporary.is_file(),
            "producer build failed")
    baseline = input_dir / "baseline.ndjson"
    os.replace(temporary, baseline)
    baseline_data = baseline.read_bytes()
    observed = inventory(baseline_data)
    baseline_digest = sha(baseline)
    omission = input_dir / "omission.ndjson"
    omission.write_bytes(omission_fault(baseline_data))
    substitution_source = ROOT / "external/lean-kernel-arena/_build/tests/lal-alt-eq-refl.ndjson"
    require(substitution_source.is_file(), "substitution Arena artifact is unavailable")
    substitution = input_dir / "substitution.ndjson"
    shutil.copyfile(substitution_source, substitution)
    truncation = input_dir / "truncation.ndjson"
    truncation.write_bytes(truncation_fault(baseline_data))
    artifacts = {}
    expected = {"baseline": "PASS", "omission": "FAIL_MISSING_TARGET",
                "substitution": "FAIL_ARTIFACT_OR_DECLARATION_IDENTITY",
                "truncation": "FAIL_PARSE_OR_DEPENDENCY_CLOSURE"}
    for name in expected:
        path = input_dir / f"{name}.ndjson"
        result = sentinel(path.read_bytes(), baseline_digest)
        require(result["classification"] == expected[name], f"{name} sentinel differs")
        artifacts[name] = {"binding": file_binding(path), "sentinel": result["classification"]}
    inventory_record = {
        "schema_version": 1, "item_id": ITEM, "generated_at": now(),
        "source": file_binding(ROOT / SOURCE), "producer": file_binding(producer),
        "producer_receipt": file_binding(run_dir / "process/supervisor.json"),
        "substitution_provenance": {"source_path": substitution_source.relative_to(ROOT).as_posix(),
                                    "source_sha256": sha(substitution_source),
                                    "arena_revision": revision},
        "baseline_inventory": observed, "artifacts": artifacts,
    }
    atomic(ROOT / INVENTORY, inventory_record)
    result = {"schema_version": 1, "item_id": ITEM, "outcome": "SUCCESS",
              "generated_at": now(), "inventory": file_binding(ROOT / INVENTORY),
              "producer_receipt": file_binding(run_dir / "process/supervisor.json"),
              "artifact_count": 4, "checker_launches": 0}
    atomic(run_dir / "result.json", result)
    return result


def _validate_execution_manifest() -> dict[str, Any]:
    manifest = load_json(ROOT / MANIFEST)
    require(manifest["schema_version"] == 1 and manifest["item_id"] == ITEM,
            "execution manifest identity differs")
    for section in ("inputs", "tooling", "artifacts"):
        for row in manifest[section]:
            bind(ROOT, row)
            committed(ROOT, row["path"])
    protocol = load_json(ROOT / PROTOCOL)
    expected_adapters = {row["id"]: row for row in protocol["adapters"]}
    require({row["id"] for row in manifest["adapter_profiles"]} == set(expected_adapters),
            "adapter profile identities differ")
    for row in manifest["adapter_profiles"]:
        expected = expected_adapters[row["id"]]
        require(row["binary"] == expected["binary"],
                f"adapter binary differs for {row['id']}")
        bind(ROOT, row["binary"])
    work = load_json(bind(ROOT, manifest["work_record"]))
    require(work["status"] == "ACTIVE" and work["item_id"] == ITEM,
            "work record is not ACTIVE")
    require(manifest["matrix"] == [{"artifact": artifact, "adapter": adapter,
                                     "expected_sentinel": expected}
                                    for artifact, adapter, expected in expected_matrix()],
            "execution matrix differs")
    return manifest


def execute() -> dict[str, Any]:
    from lib.research_queue_v3 import load_queue
    manifest = _validate_execution_manifest()
    queue = load_queue(ROOT, require_ready=True)
    item = next(row for row in queue["items"] if row["id"] == ITEM)
    require(queue["selected_item"] == ITEM and item["status"] == "ACTIVE",
            "item is not selected ACTIVE")
    for path in (MANIFEST, WORK, PLAN, PROTOCOL, EXPECTED,
                 "config/research-queue.json", "docs/RESEARCH_STATUS.md"):
        committed(ROOT, path)
    run_dir = safe(ROOT, RUN, exists=False)
    require(not run_dir.exists(), "refuse execution overwrite")
    run_dir.mkdir(parents=True)
    artifacts = {Path(row["path"]).stem: ROOT / row["path"] for row in manifest["artifacts"]}
    adapters = {row["id"]: row for row in manifest["adapter_profiles"]}
    baseline_digest = sha(artifacts["baseline"])
    cells = []
    for artifact_name, adapter_id, expected_sentinel in expected_matrix():
        artifact_path = artifacts[artifact_name]
        sentinel_result = sentinel(artifact_path.read_bytes(), baseline_digest)
        require(sentinel_result["classification"] == expected_sentinel,
                f"sentinel differs before {artifact_name}/{adapter_id}")
        profile = adapters[adapter_id]
        binary = ROOT / profile["binary"]["path"]
        argv = [str(binary), *profile["arguments_before_artifact"], str(artifact_path)]
        directory = run_dir / f"{artifact_name}-{adapter_id}"
        env = {"LANG": "C", "PATH": "/usr/bin:/bin"}
        receipt, _, _ = _supervise(directory, argv, binary.parent, env, 120, CHECKER_MEMORY)
        receipt["adapter_id"] = adapter_id
        receipt["adapter_binary_sha256"] = sha(binary)
        receipt["artifact"] = file_binding(artifact_path)
        receipt["sentinel"] = sentinel_result
        atomic(directory / "supervisor.json", receipt)
        process = process_classification(receipt)
        require(process != "INFRASTRUCTURE_FAILURE" and process != "UNKNOWN",
                f"process infrastructure failed for {artifact_name}/{adapter_id}")
        if artifact_name == "baseline":
            require(process == "ACCEPT", f"baseline was not accepted by {adapter_id}")
        cells.append({"artifact": artifact_name, "adapter": adapter_id,
                      "sentinel": sentinel_result["classification"],
                      "process_outcome": process,
                      "receipt": file_binding(directory / "supervisor.json"),
                      "stdout": file_binding(directory / "process.stdout"),
                      "stderr": file_binding(directory / "process.stderr")})
    false_reassurance = [{"artifact": row["artifact"], "adapter": row["adapter"]}
                         for row in cells if row["artifact"] != "baseline"
                         and row["process_outcome"] == "ACCEPT"]
    result = {
        "schema_version": 1, "item_id": ITEM, "outcome": "SUCCESS", "generated_at": now(),
        "cells": cells, "false_reassurance_cells": false_reassurance,
        "conclusion": "The checked-object sentinel accepted only the exact intended artifact and rejected all omission, substitution and truncation faults independently of checker exit status.",
        "claim_limit": "This establishes the scoped sentinel behavior for one module, producer and two adapters. It does not make checker-correctness or semantic-authority claims.",
    }
    atomic(ROOT / BASE / "result.json", result)
    return result
