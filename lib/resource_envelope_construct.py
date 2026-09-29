"""Guarded deterministic source/export construction for the resource pilot."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
from typing import Any

from lib.resource_envelope_audit import audit_case, audit_corpus
from lib.resource_envelope_control import (
    BASE, EMPTY_EXPORT, EXECUTION, EXPORTER_BINARY, LAKEFILE, LEAN_TOOLCHAIN, LIMITS,
    ROOT, TOOLCHAIN, GateError, binding, require_construction_gate,
)
from lib.resource_envelope_producer import (
    canonical_json, case_id, declaration_name, make_case_row, render_source,
    selected_slots, sha256,
)
from lib.resource_envelope_supervisor import SupervisedResult, run_direct


def _new_attempt() -> Path:
    for number in range(1, 10000):
        candidate = BASE / f"construction-run-{number:04d}"
        try:
            candidate.mkdir(parents=True, exist_ok=False)
            return candidate
        except FileExistsError:
            continue
    raise GateError("construction attempt namespace exhausted")


def _write_new(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(raw)


def _json_new(path: Path, value: Any) -> None:
    _write_new(path, canonical_json(value))


def _record_process(attempt: Path, label: str,
                    result: SupervisedResult) -> dict[str, Any]:
    prefix = attempt / "processes" / label
    _write_new(prefix.with_suffix(".stdout"), result.stdout)
    _write_new(prefix.with_suffix(".stderr"), result.stderr)
    _json_new(prefix.with_suffix(".receipt.json"), result.receipt)
    return {"stdout": binding(prefix.with_suffix(".stdout")),
            "stderr": binding(prefix.with_suffix(".stderr")),
            "receipt": binding(prefix.with_suffix(".receipt.json"))}


def _safe_process(result: SupervisedResult, label: str) -> None:
    r = result.receipt
    if (r.get("monitor_errors") or r.get("pipe_errors") or r.get("accounting_error")
            or not r.get("reap_complete") or not r.get("cleanup_complete")
            or r.get("trace_gap_fault") or r.get("child_peak_rss_bytes") is None):
        raise GateError(f"{label}: invalid supervision; preserve and repair")
    if r.get("stop_reason") is not None:
        raise GateError(f"{label}: supervised limit or output stop {r['stop_reason']}; diagnose")
    if r.get("exit_code") != 0:
        raise GateError(f"{label}: nonzero construction process exit {r.get('exit_code')}")


def _run_build_or_export(*, argv: list[str], workspace: Path,
                         stdin_bytes: bytes | None, phase: str,
                         execution: dict[str, Any]) -> SupervisedResult:
    limits = execution["limits"]
    profile = limits[phase]
    return run_direct(
        argv=argv, cwd=workspace, env=execution["environment"],
        stdin_bytes=stdin_bytes,
        timeout_seconds=profile["timeout_seconds"],
        memory_ceiling_bytes=profile["memory_ceiling_bytes"],
        sample_interval_seconds=limits["sample_interval_seconds"],
        max_trace_gap_seconds=limits["max_trace_gap_seconds"],
        cleanup_seconds=limits["cleanup_seconds"],
        ps_timeout_seconds=limits["ps_timeout_seconds"],
        output_cap_bytes=limits["output_cap_bytes"],
    )


def construct() -> dict[str, Any]:
    """Call only after reviewed, committed manifests; gate runs before rendering."""
    science, execution = require_construction_gate()
    if (science["case_order"] != [
            {"ordinal": ordinal, "family": family, "size": size}
            for ordinal, family, size in selected_slots()]):
        raise GateError("frozen selected case order differs")
    if execution["limits"] != LIMITS:
        raise GateError("frozen construction limits differ")
    if (execution["workspace_templates"]["lakefile_toml_sha256"] != sha256(LAKEFILE)
            or execution["workspace_templates"]["lean_toolchain_sha256"] != sha256(LEAN_TOOLCHAIN)
            or execution["empty_export"] != {"bytes": len(EMPTY_EXPORT),
                                              "sha256": sha256(EMPTY_EXPORT)}):
        raise GateError("frozen workspace/baseline templates differ")
    attempt = _new_attempt()
    staged = attempt / "staged" / "corpus"
    for name in ("sources", "exports", "cases"):
        (staged / name).mkdir(parents=True, exist_ok=False)
    progress: list[dict[str, Any]] = []
    phase = "start"
    current_id: str | None = None
    last_argv: list[str] | None = None
    try:
        for ordinal, family, size in selected_slots():
            require_construction_gate()  # Recheck all committed bindings before each batch.
            current_id = case_id(family, size)
            phase = "render"
            source = render_source(family, size)
            _write_new(staged / "sources" / f"{current_id}.lean", source)
            workspace = attempt / "workspaces" / current_id
            workspace.mkdir(parents=True, exist_ok=False)
            _write_new(workspace / "ResourceEnvelopePilot1.lean", source)
            _write_new(workspace / "lakefile.toml", LAKEFILE)
            _write_new(workspace / "lean-toolchain", LEAN_TOOLCHAIN)
            phase = "build"
            build_argv = [str(TOOLCHAIN / "lake"), "build", "ResourceEnvelopePilot1"]
            last_argv = build_argv
            built = _run_build_or_export(argv=build_argv, workspace=workspace,
                                         stdin_bytes=None, phase="build", execution=execution)
            build_ref = _record_process(attempt, current_id + "-build", built)
            _safe_process(built, current_id + " build")
            phase = "export"
            require_construction_gate()  # The exporter sees the same frozen inputs.
            export_argv = [str(TOOLCHAIN / "lake"), "env", str(ROOT / EXPORTER_BINARY),
                           "ResourceEnvelopePilot1", "--", declaration_name(family, size)]
            last_argv = export_argv
            exported = _run_build_or_export(argv=export_argv, workspace=workspace,
                                            stdin_bytes=None, phase="export", execution=execution)
            export_ref = _record_process(attempt, current_id + "-export", exported)
            _safe_process(exported, current_id + " export")
            export_raw = exported.stdout
            _write_new(staged / "exports" / f"{current_id}.ndjson", export_raw)
            phase = "package_and_audit"
            row = make_case_row(ordinal, family, size, source, export_raw)
            details = audit_case(row, export_raw, source)
            _json_new(staged / "cases" / f"{current_id}.json", row)
            progress.append({"id": current_id, "ordinal": ordinal,
                             "source": binding(staged / "sources" / f"{current_id}.lean"),
                             "export": binding(staged / "exports" / f"{current_id}.ndjson"),
                             "case": binding(staged / "cases" / f"{current_id}.json"),
                             "build_process": build_ref, "export_process": export_ref,
                             "independent_audit": details})
        phase = "index"
        index_rows = []
        for item in progress:
            row = json.loads((staged / "cases" / f"{item['id']}.json").read_text())
            case_file = staged / "cases" / f"{item['id']}.json"
            index_rows.append({"id": item["id"], "ordinal": item["ordinal"],
                               "family": row["family"], "size": row["size"],
                               "case": {"path": f"corpus/cases/{item['id']}.json",
                                        "bytes": case_file.stat().st_size,
                                        "sha256": sha256(case_file.read_bytes())}})
        _json_new(staged / "index.json", {"schema_version": 1,
                                          "item_id": "RESOURCE-ENVELOPE-PILOT-1",
                                          "cases": index_rows})
        phase = "full_independent_audit"
        audited = audit_corpus(staged)
        if audited.get("status") != "PASS" or audited.get("count") != 12:
            raise GateError("full independent corpus audit did not pass")
        phase = "publish_local_corpus"
        canonical = BASE / "corpus"
        if canonical.exists():
            raise GateError("canonical corpus already exists; preserve and reconcile")
        shutil.copytree(staged, canonical)
        if audit_corpus(canonical) != audited:
            raise GateError("published local corpus differs from independently audited staged corpus")
        result = {"schema_version": 1, "item_id": "RESOURCE-ENVELOPE-PILOT-1",
                  "status": "CONSTRUCTED_AND_INDEPENDENTLY_AUDITED",
                  "completed_at": datetime.now(timezone.utc).isoformat(),
                  "scientific_manifest": binding(BASE / "scientific-manifest.json"),
                  "execution_manifest": binding(EXECUTION),
                  "canonical_index": binding(canonical / "index.json"),
                  "independent_audit": audited, "cases": progress}
        _json_new(attempt / "construction-result.json", result)
        return result
    except Exception as exc:
        failure = {"schema_version": 1, "item_id": "RESOURCE-ENVELOPE-PILOT-1",
                   "status": "CONSTRUCTION_FAILURE_REPAIR_PAUSE",
                   "failed_at": datetime.now(timezone.utc).isoformat(),
                   "phase": phase, "case_id": current_id,
                   "attempted_argv": last_argv,
                   "error_type": type(exc).__name__, "error": str(exc),
                   "scientific_manifest": binding(BASE / "scientific-manifest.json"),
                   "execution_manifest": binding(EXECUTION),
                   "completed_cases": progress}
        _json_new(attempt / "construction-failure.json", failure)
        raise
