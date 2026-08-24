"""Durable state for resumable rotating held-out evaluations."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class CheckpointError(RuntimeError):
    """Raised when a checkpoint cannot be resumed safely."""


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    with temporary.open("w", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


class RotatingCheckpoint:
    def __init__(self, path: Path, data: dict[str, Any], files: list[dict[str, Any]]) -> None:
        self.path = path
        self.data = data
        self.files = files

    @classmethod
    def create(
        cls,
        path: Path,
        *,
        experiment_id: str,
        fold_id: str,
        bindings: dict[str, Any],
        files: list[dict[str, Any]],
        started_at: str,
    ) -> "RotatingCheckpoint":
        data: dict[str, Any] = {
            "schema_version": 1,
            "status": "IN_PROGRESS",
            "experiment_id": experiment_id,
            "fold_id": fold_id,
            "started_at": started_at,
            "updated_at": started_at,
            "bindings": bindings,
            "progress": {
                "total_original_tests": len(files),
                "completed_original_tests": 0,
            },
            "candidate_evaluation": None,
            "control_evaluation": None,
            "original_tests": [],
            "inflight": None,
            "sessions": [],
            "costs": {
                "checker_attempts_started": 0,
                "checker_results_recorded": 0,
                "checker_seconds_recorded": 0.0,
                "abandoned_checker_attempts": 0,
            },
        }
        checkpoint = cls(path, data, files)
        checkpoint.validate(bindings)
        checkpoint.save()
        return checkpoint

    @classmethod
    def resume(
        cls,
        path: Path,
        *,
        bindings: dict[str, Any],
        files: list[dict[str, Any]],
    ) -> "RotatingCheckpoint":
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise CheckpointError(f"cannot load checkpoint {path}: {error}") from error
        checkpoint = cls(path, data, files)
        checkpoint.validate(bindings)
        if data["status"] != "IN_PROGRESS":
            raise CheckpointError(f"checkpoint status is {data['status']}, not IN_PROGRESS")
        checkpoint.recover_interrupted_attempt()
        checkpoint.save()
        return checkpoint

    def validate(self, bindings: dict[str, Any]) -> None:
        if self.data.get("schema_version") != 1:
            raise CheckpointError("unsupported checkpoint schema")
        if self.data.get("bindings") != bindings:
            raise CheckpointError("checkpoint bindings differ from the current frozen inputs or runner")
        rows = self.data.get("original_tests")
        if not isinstance(rows, list) or len(rows) > len(self.files):
            raise CheckpointError("checkpoint has an invalid completed-test inventory")
        for index, row in enumerate(rows):
            expected = self.files[index]
            observed = (row.get("name"), row.get("artifact_sha256"), row.get("bytes"))
            wanted = (expected["name"], expected["sha256"], expected["bytes"])
            if observed != wanted:
                raise CheckpointError(f"checkpoint test prefix diverges at index {index}")
        progress = self.data.get("progress", {})
        if progress.get("total_original_tests") != len(self.files):
            raise CheckpointError("checkpoint total test count differs from the frozen inventory")
        if progress.get("completed_original_tests") != len(rows):
            raise CheckpointError("checkpoint progress does not match its completed rows")
        for field, binding_name in (
            ("candidate_evaluation", "candidate"),
            ("control_evaluation", "positive_control"),
        ):
            evaluation = self.data.get(field)
            if evaluation is not None and evaluation.get("artifact_sha256") != bindings[binding_name]["sha256"]:
                raise CheckpointError(f"checkpoint {field} differs from its frozen artifact")
        inflight = self.data.get("inflight")
        if inflight is not None:
            self._validate_inflight(inflight)
        costs = self.data.get("costs", {})
        active_attempts = int(bool(inflight and inflight.get("active_attempt")))
        if costs.get("checker_attempts_started") != (
            costs.get("checker_results_recorded", 0)
            + costs.get("abandoned_checker_attempts", 0)
            + active_attempts
        ):
            raise CheckpointError("checkpoint checker-attempt accounting does not reconcile")

    def _validate_inflight(self, inflight: dict[str, Any]) -> None:
        kind = inflight.get("kind")
        if kind not in {"candidate", "control", "original"}:
            raise CheckpointError("checkpoint has an invalid inflight kind")
        if kind == "original":
            index = len(self.data["original_tests"])
            if index >= len(self.files):
                raise CheckpointError("checkpoint has an extra inflight original test")
            expected = self.files[index]
            observed = (inflight.get("key"), inflight.get("artifact_sha256"), inflight.get("bytes"))
            wanted = (expected["name"], expected["sha256"], expected["bytes"])
            if observed != wanted:
                raise CheckpointError("checkpoint inflight test differs from the frozen inventory")
        else:
            binding_name = "candidate" if kind == "candidate" else "positive_control"
            expected_key = "candidate" if kind == "candidate" else "positive-control"
            if inflight.get("key") != expected_key:
                raise CheckpointError("checkpoint inflight special-input key is invalid")
            if inflight.get("artifact_sha256") != self.data["bindings"][binding_name]["sha256"]:
                raise CheckpointError("checkpoint inflight special input differs from its binding")
        if inflight.get("active_attempt") is not None:
            side = inflight["active_attempt"].get("side")
            if side not in {"baseline", "mutant"}:
                raise CheckpointError("checkpoint has an invalid active checker attempt")

    def save(self) -> None:
        self.data["updated_at"] = timestamp()
        atomic_write_json(self.path, self.data)

    def recover_interrupted_attempt(self) -> None:
        inflight = self.data.get("inflight")
        abandoned = bool(inflight and inflight.get("active_attempt"))
        if abandoned:
            self.data["costs"]["abandoned_checker_attempts"] += 1
            inflight["active_attempt"] = None
        if self.data["sessions"] and self.data["sessions"][-1]["status"] == "RUNNING":
            session = self.data["sessions"][-1]
            session["status"] = "INTERRUPTED"
            session["completed_at"] = timestamp()
            session["reason"] = (
                "PROCESS_ENDED_DURING_CHECKER_ATTEMPT" if abandoned
                else "PROCESS_ENDED_BEFORE_SESSION_FINALIZATION"
            )

    def start_session(self) -> None:
        if self.data["sessions"] and self.data["sessions"][-1]["status"] == "RUNNING":
            raise CheckpointError("a checkpoint session is already running")
        self.data["sessions"].append({
            "sequence": len(self.data["sessions"]) + 1,
            "started_at": timestamp(),
            "completed_at": None,
            "status": "RUNNING",
            "reason": None,
            "preparation": None,
        })

    def set_preparation(self, preparation: dict[str, Any]) -> None:
        self.data["sessions"][-1]["preparation"] = preparation

    def end_session(self, status: str, reason: str | None = None) -> None:
        if not self.data["sessions"] or self.data["sessions"][-1]["status"] != "RUNNING":
            return
        session = self.data["sessions"][-1]
        session["status"] = status
        session["completed_at"] = timestamp()
        session["reason"] = reason

    def begin_unit(self, kind: str, key: str, artifact_sha256: str, size: int) -> None:
        if self.data["inflight"] is not None:
            raise CheckpointError("cannot begin a unit while another unit is inflight")
        self.data["inflight"] = {
            "kind": kind,
            "key": key,
            "artifact_sha256": artifact_sha256,
            "bytes": size,
            "baseline": None,
            "mutant": None,
            "active_attempt": None,
        }

    def require_unit(self, kind: str, key: str, artifact_sha256: str, size: int) -> None:
        inflight = self.data["inflight"]
        observed = (
            inflight.get("kind"), inflight.get("key"), inflight.get("artifact_sha256"),
            inflight.get("bytes"),
        ) if inflight else None
        wanted = (kind, key, artifact_sha256, size)
        if observed != wanted:
            raise CheckpointError(f"inflight unit {observed!r} does not match requested unit {wanted!r}")

    def next_side(self) -> str | None:
        inflight = self.data["inflight"]
        if inflight is None:
            raise CheckpointError("no inflight unit")
        if inflight["baseline"] is None:
            return "baseline"
        if inflight["mutant"] is None:
            return "mutant"
        return None

    def begin_attempt(self, side: str) -> None:
        inflight = self.data["inflight"]
        if inflight is None or inflight["active_attempt"] is not None:
            raise CheckpointError("cannot begin checker attempt")
        if side != self.next_side():
            raise CheckpointError(f"unexpected checker side {side}")
        inflight["active_attempt"] = {"side": side, "started_at": timestamp()}
        self.data["costs"]["checker_attempts_started"] += 1

    def finish_attempt(self, side: str, result: dict[str, Any]) -> None:
        inflight = self.data["inflight"]
        if inflight is None or inflight.get("active_attempt", {}).get("side") != side:
            raise CheckpointError("checker result does not match the active attempt")
        inflight[side] = result
        inflight["active_attempt"] = None
        self.data["costs"]["checker_results_recorded"] += 1
        self.data["costs"]["checker_seconds_recorded"] += float(result["seconds"])

    def complete_unit(self, evaluation: dict[str, Any]) -> None:
        inflight = self.data["inflight"]
        if inflight is None or self.next_side() is not None:
            raise CheckpointError("cannot complete a partial unit")
        kind = inflight["kind"]
        if kind == "candidate":
            self.data["candidate_evaluation"] = evaluation
        elif kind == "control":
            self.data["control_evaluation"] = evaluation
        else:
            self.data["original_tests"].append(evaluation)
            self.data["progress"]["completed_original_tests"] = len(self.data["original_tests"])
        self.data["inflight"] = None

    def mark_complete(self, output: dict[str, str]) -> None:
        if self.data["inflight"] is not None:
            raise CheckpointError("cannot complete checkpoint with inflight work")
        if len(self.data["original_tests"]) != len(self.files):
            raise CheckpointError("cannot complete checkpoint before every original test")
        if self.data["candidate_evaluation"] is None or self.data["control_evaluation"] is None:
            raise CheckpointError("cannot complete checkpoint before candidate and control")
        self.data["status"] = "COMPLETE"
        self.data["completed_at"] = timestamp()
        self.data["final_output"] = output
